#!/usr/bin/env python3
"""YouTube History CLI - Fetch complete YouTube watch history.

Usage:
    python yt_history.py list              # List last 50 items
    python yt_history.py list --limit 200  # List 200 items
    python yt_history.py export            # Export everything to JSON
    python yt_history.py search "term"     # Search in history
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.auth import load_cookies
from src.exceptions import AuthenticationError, YouTubeHistoryError
from src.history_fetcher import HistoryFetcher
from src.history_filter import filter_by_type, search_items, separate_by_type
from src.progress import ProgressReporter
from src.youtube_client import YouTubeClient

if TYPE_CHECKING:
    from src.history_parser import HistoryItem
    from src.models import HistoryGroup


def cmd_list(args: argparse.Namespace) -> None:
    """Execute list command - display history items.

    Args:
        args: Parsed command-line arguments containing limit, type, json, verbose flags.
    """
    verbose = getattr(args, "verbose", False)

    if not args.json and verbose:
        print("🔍 Fetching YouTube history...")

    # Load cookies and fetch
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit
    progress = ProgressReporter.create_loading_callback(verbose, args.json, limit)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if not args.json and verbose:
        print()  # New line after progress

    # Filter by type
    filtered = filter_by_type(grouped, args.type)

    if filtered.total_items == 0:
        if args.json:
            print(json.dumps(filtered.to_dict(), indent=2))
        else:
            print("❌ No items found in history.")
        return

    # JSON output
    if args.json:
        print(json.dumps(filtered.to_dict(), indent=2, ensure_ascii=False))
        return

    # Human-readable output
    _print_summary(filtered, args.type)
    _display_items_grouped(filtered.shorts, filtered.videos)


def cmd_export(args: argparse.Namespace) -> None:
    """Execute export command - export history to JSON file.

    Args:
        args: Parsed command-line arguments containing output, limit, type, verbose flags.
    """
    verbose = getattr(args, "verbose", False)

    if verbose:
        print("📦 Exporting YouTube history...")

    # Load cookies and fetch
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit
    progress = ProgressReporter.create_fetching_callback(verbose, limit)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if verbose:
        print()  # New line

    if grouped.total_items == 0:
        print("❌ History is empty.")
        return

    # Filter by type
    filtered = filter_by_type(grouped, args.type)

    # Save file
    output = Path(args.output)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(filtered.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"\n✅ Exported: {output.absolute()}")
    print(f"   Total: {filtered.total_items} items")

    if filtered.statistics:
        print("   Statistics:")
        for item_type, count in filtered.statistics.items():
            print(f"     - {item_type}: {count}")


def cmd_search(args: argparse.Namespace) -> None:
    """Execute search command - search for term in history.

    Args:
        args: Parsed command-line arguments containing query, limit, type, verbose flags.
    """
    verbose = getattr(args, "verbose", False)

    if verbose:
        print(f"🔎 Searching '{args.query}' in history...")

    # Load cookies and fetch
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit
    progress = ProgressReporter.create_analyzing_callback(verbose, limit)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if verbose:
        print()

    if grouped.total_items == 0:
        print("❌ History is empty.")
        return

    # Filter by type first
    filtered = filter_by_type(grouped, args.type)
    all_items = filtered.all_items()

    # Search in filtered items
    matches = search_items(all_items, args.query)

    if not matches:
        print(f"\n❌ No results for '{args.query}'")
        print(f"   (Searched {len(all_items)} items)")
        return

    # Separate matches by type
    matched_videos, matched_shorts = separate_by_type(matches)

    # Print summary
    total_matches = len(matches)
    if args.type == "all" and matched_videos and matched_shorts:
        print(
            f"\n✅ {total_matches} result(s) found ({len(matched_shorts)} shorts, {len(matched_videos)} videos)"
        )
    else:
        print(f"\n✅ {total_matches} result(s) found")

    # Display results
    _display_items_grouped(matched_shorts, matched_videos)
    print("\n" + "=" * 80)


def cmd_extract_cookies(args: argparse.Namespace) -> None:
    """Execute extract-cookies command - extract fresh cookies from browser.

    Args:
        args: Parsed command-line arguments containing output file path.
    """
    try:
        import browser_cookie3  # noqa: F401
    except ImportError:
        print("❌ Error: 'browser-cookie3' library not installed")
        print("\nInstall with: pip install browser-cookie3")
        sys.exit(1)

    from src.auth import (
        detect_available_browsers,
        extract_from_first_available,
        save_cookies_to_file,
        test_authentication,
    )
    from src.exceptions import CookieExtractionError

    print("=" * 60)
    print("AUTOMATIC COOKIE EXTRACTION")
    print("=" * 60)

    # Detect browsers
    available = detect_available_browsers(verbose=True)

    if not available:
        print("\n❌ No browsers found!")
        print("\nTips:")
        print("1. Log in to YouTube in your browser")
        print("2. Chrome 127+ has issues - use Firefox")
        print("3. macOS: allow Keychain access")
        sys.exit(1)

    browser = available[0]
    print(f"\n✓ Using {browser.title()}")

    # Extract cookies
    print(f"\n{'=' * 60}")
    try:
        cookie_string, _cookies = extract_from_first_available(available, verbose=True)
    except CookieExtractionError as e:
        print(f"\n❌ Failed: {e}")
        if browser == "chrome":
            print("\n💡 Chrome 127+ blocked cookies.")
            print("   Try Firefox or manual method.")
        sys.exit(1)

    # Save cookies
    output_file = args.output if hasattr(args, "output") else "browser_auth.json"
    try:
        auth_file = save_cookies_to_file(cookie_string, output_file, verbose=True)
    except OSError as e:
        print(f"\n❌ Error saving cookies: {e}")
        sys.exit(1)

    # Test authentication
    success = test_authentication(auth_file, verbose=True)

    # Final message
    print(f"\n{'=' * 60}")
    if success:
        print("✅ SUCCESS!")
        print("\nUse with:")
        print("  python yt_history.py list")
    else:
        print("⚠️  Cookies extracted but test failed.")
    print("=" * 60)


def _print_summary(grouped: HistoryGroup, type_filter: str) -> None:
    """Print summary of found items.

    Args:
        grouped: Grouped history items.
        type_filter: Type filter applied ("all", "videos", "shorts").
    """
    total = grouped.total_items
    videos_count = len(grouped.videos)
    shorts_count = len(grouped.shorts)

    if type_filter == "all":
        print(f"✅ {total} items found ({shorts_count} shorts, {videos_count} videos)")
    else:
        print(f"✅ {total} items found")


def _display_items_grouped(
    shorts: list[HistoryItem],
    videos: list[HistoryItem],
    start_index: int = 1,
) -> None:
    """Display items grouped by type.

    Args:
        shorts: List of short items.
        videos: List of video items.
        start_index: Starting number for display (default: 1).
    """
    counter = start_index

    # Shorts section
    if shorts:
        print("\n📱 SHORTS")
        print("─" * 80)
        for item in shorts:
            print(f"\n{counter}. 📱 {item.title}")
            if item.watched_time:
                print(f"   🕐 {item.watched_time}")
            print(f"   🔗 https://www.youtube.com/watch?v={item.video_id}")
            counter += 1

    # Videos section
    if videos:
        print("\n🎬 VIDEOS")
        print("─" * 80)
        for item in videos:
            print(f"\n{counter}. 🎬 {item.title}")
            if item.channel_name:
                print(f"   📺 {item.channel_name}")
            if item.watched_time:
                print(f"   🕐 {item.watched_time}")
            print(f"   🔗 https://www.youtube.com/watch?v={item.video_id}")
            counter += 1


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level.

    Args:
        verbose: Enable debug-level logging if True.
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s [%(name)s]: %(message)s")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with all commands and options.

    Returns:
        Configured ArgumentParser instance.
    """
    # Parent parser for shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--auth",
        default="browser_auth.json",
        metavar="FILE",
        help="authentication file (default: browser_auth.json)",
    )
    parent_parser.add_argument(
        "--live-cookies",
        action="store_true",
        help="extract fresh cookies from browser on every command (ignores --auth)",
    )
    parent_parser.add_argument(
        "--verbose", "-v", action="store_true", help="enable verbose logging (debug level)"
    )

    parser = argparse.ArgumentParser(
        prog="yt_history",
        description="YouTube History CLI - Fetch complete YouTube watch history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                                    # List last 50 items (grouped by type)
  %(prog)s list --live-cookies                     # List with fresh cookies from browser
  %(prog)s --verbose list --limit 200              # List last 200 items with debug
  %(prog)s list --type shorts --verbose            # List only shorts with debug
  %(prog)s search "cooking"                        # Search in last 50 items
  %(prog)s search "cooking" --limit 0              # Search in all history
  %(prog)s search "cooking" --type videos          # Search only in videos
  %(prog)s search "music" --type shorts --limit 0  # Search shorts in all history
  %(prog)s export                                  # Export last 50 items
  %(prog)s export --limit 0                        # Export all history
  %(prog)s export --limit 0 --live-cookies         # Export all with fresh cookies
  %(prog)s export --type videos --limit 0          # Export only videos
  %(prog)s export --output my.json                 # Export to custom file
  %(prog)s extract-cookies                         # Extract cookies from browser (first-time setup)
  %(prog)s extract-cookies --output custom.json    # Save to custom file
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="available commands",
        metavar="{list,export,search,extract-cookies}",
    )

    # Command: list
    list_parser = subparsers.add_parser(
        "list",
        help="list history items",
        description="Display YouTube watch history with videos and shorts.",
        parents=[parent_parser],
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="maximum number of items to fetch (default: 50, use 0 for all)",
    )
    list_parser.add_argument(
        "--json", action="store_true", help="output as JSON instead of human-readable format"
    )
    list_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)",
    )

    # Command: export
    export_parser = subparsers.add_parser(
        "export",
        help="export history to JSON",
        description="Export YouTube watch history to a JSON file.",
        parents=[parent_parser],
    )
    export_parser.add_argument(
        "--output",
        default="youtube_history.json",
        metavar="FILE",
        help="output file path (default: youtube_history.json)",
    )
    export_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="maximum number of items to export (default: 50, use 0 for all)",
    )
    export_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)",
    )

    # Command: search
    search_parser = subparsers.add_parser(
        "search",
        help="search in history",
        description="Search for videos/channels in your watch history.",
        parents=[parent_parser],
    )
    search_parser.add_argument(
        "query", metavar="TERM", help="search term (matches title or channel name)"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="search in last N items (default: 50, use 0 for all history)",
    )
    search_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)",
    )

    # Command: extract-cookies
    extract_parser = subparsers.add_parser(
        "extract-cookies",
        help="extract cookies from browser",
        description="Extract YouTube cookies from browser for authentication (first-time setup).",
    )
    extract_parser.add_argument(
        "--output",
        default="browser_auth.json",
        metavar="FILE",
        help="output file path (default: browser_auth.json)",
    )

    return parser


def check_auth_file(args: argparse.Namespace) -> None:
    """Check if authentication file exists.

    Args:
        args: Parsed arguments.

    Raises:
        SystemExit: If auth file not found (unless using live cookies or extract-cookies command).
    """
    if args.command == "extract-cookies" or args.live_cookies:
        return

    if not Path(args.auth).exists():
        print(f"❌ Authentication file not found: {args.auth}")
        print("\nRun first:")
        print("  python yt_history.py extract-cookies")
        print("\nOr use live mode:")
        print("  python yt_history.py list --live-cookies")
        sys.exit(1)


def main() -> NoReturn:
    """Main entry point for CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    verbose = getattr(args, "verbose", False)
    setup_logging(verbose=verbose)

    # Check command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check auth file
    check_auth_file(args)

    # Execute command
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "export":
            cmd_export(args)
        elif args.command == "search":
            cmd_search(args)
        elif args.command == "extract-cookies":
            cmd_extract_cookies(args)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)

    except AuthenticationError as e:
        print(f"\n❌ Error: {e}")
        print("\nRun first:")
        print("  python yt_history.py extract-cookies")
        sys.exit(1)

    except YouTubeHistoryError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
