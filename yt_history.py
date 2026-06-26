#!/usr/bin/env python3
"""
YouTube History CLI - Fetch complete YouTube watch history.

Usage:
    python yt_history.py list              # List last 50 items
    python yt_history.py list --limit 200  # List 200 items
    python yt_history.py export            # Export everything to JSON
    python yt_history.py search "term"     # Search in history
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.youtube_client import YouTubeClient, load_cookies_from_file
from src.history_fetcher import HistoryFetcher


def load_cookies(args):
    """Load cookies from file or live extraction based on args.

    Args:
        args: Parsed command-line arguments with 'live_cookies' and 'auth' attributes

    Returns:
        dict: Cookie dictionary
    """
    if args.live_cookies:
        from extract_cookies import get_live_cookies
        # Only show verbose output if --verbose flag is set
        verbose = getattr(args, 'verbose', False) and not getattr(args, 'json', False)
        return get_live_cookies(verbose=verbose)
    else:
        return load_cookies_from_file(args.auth)


def cmd_list(args):
    """Command: list - Display history items."""
    verbose = getattr(args, 'verbose', False)

    if not args.json and verbose:
        print("🔍 Fetching YouTube history...")

    # Load cookies
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit

    def progress(total):
        if not args.json and verbose:
            max_display = limit if limit else total
            print(f"\r   Loading... {min(total, max_display)} items", end="", flush=True)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if not args.json and verbose:
        print()  # New line after progress

    # Filter by type
    videos = grouped["videos"]
    shorts = grouped["shorts"]

    if args.type == "videos":
        shorts = []
    elif args.type == "shorts":
        videos = []

    total_displayed = len(videos) + len(shorts)

    if total_displayed == 0:
        if args.json:
            print(json.dumps({"total_items": 0, "statistics": {}, "videos": [], "shorts": []}, indent=2))
        else:
            print("❌ No items found in history.")
        return

    # JSON output
    if args.json:
        output = {
            "total_items": total_displayed,
            "statistics": {},
            "videos": [item.to_dict() for item in videos],
            "shorts": [item.to_dict() for item in shorts]
        }
        # Recalculate statistics
        if videos:
            output["statistics"]["video"] = len(videos)
        if shorts:
            output["statistics"]["short"] = len(shorts)

        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    print(f"\n✅ {total_displayed} items found", end="")
    if args.type == "all":
        print(f" ({len(shorts)} shorts, {len(videos)} videos)")
    else:
        print()

    # Always display grouped by type
    _display_items_grouped(shorts, videos)


def _display_items_grouped(shorts, videos):
    """Display items grouped by type."""
    counter = 1

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




def cmd_export(args):
    """Command: export - Export history to file."""
    verbose = getattr(args, 'verbose', False)

    if verbose:
        print("📦 Exporting YouTube history...")

    # Load cookies
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit

    def progress(total):
        if verbose:
            max_display = limit if limit else total
            print(f"\r   Fetching... {min(total, max_display)} items", end="", flush=True)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if verbose:
        print()  # New line

    if grouped["total_items"] == 0:
        print("❌ No items found.")
        return

    # Filter by type if specified
    videos = grouped["videos"]
    shorts = grouped["shorts"]

    if args.type == "videos":
        shorts = []
    elif args.type == "shorts":
        videos = []

    # Recalculate stats after filtering
    stats = {}
    if videos:
        stats["video"] = len(videos)
    if shorts:
        stats["short"] = len(shorts)

    total_exported = len(videos) + len(shorts)

    # Prepare data
    export_data = {
        "total_items": total_exported,
        "statistics": stats,
        "videos": [item.to_dict() for item in videos],
        "shorts": [item.to_dict() for item in shorts]
    }

    # Save file
    output = Path(args.output)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Exported: {output.absolute()}")
    print(f"   Total: {total_exported} items")
    if stats:
        print(f"   Statistics:")
        for item_type, count in stats.items():
            print(f"     - {item_type}: {count}")


def cmd_search(args):
    """Command: search - Search term in history."""
    verbose = getattr(args, 'verbose', False)

    if verbose:
        print(f"🔎 Searching '{args.query}' in history...")

    # Load cookies
    cookies = load_cookies(args)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    limit = None if args.limit == 0 else args.limit

    def progress(total):
        if verbose:
            max_display = limit if limit else total
            print(f"\r   Analyzing... {min(total, max_display)} items", end="", flush=True)

    # Fetch items grouped
    grouped = fetcher.fetch_all_grouped(limit=limit, progress_callback=progress)

    if verbose:
        print()

    if grouped["total_items"] == 0:
        print("❌ History is empty.")
        return

    # Get items based on type filter
    videos = grouped["videos"]
    shorts = grouped["shorts"]

    if args.type == "videos":
        all_items = videos
    elif args.type == "shorts":
        all_items = shorts
    else:
        all_items = videos + shorts

    # Filter by query (case-insensitive)
    query_lower = args.query.lower()
    matches = [
        item for item in all_items
        if query_lower in item.title.lower() or
           (item.channel_name and query_lower in item.channel_name.lower())
    ]

    if not matches:
        print(f"\n❌ No results for '{args.query}'")
        print(f"   (Searched {len(all_items)} items)")
        return

    # Separate matches by type
    matched_videos = [item for item in matches if item.item_type == "video"]
    matched_shorts = [item for item in matches if item.item_type == "short"]

    print(f"\n✅ {len(matches)} result(s) found", end="")
    if args.type == "all" and matched_videos and matched_shorts:
        print(f" ({len(matched_shorts)} shorts, {len(matched_videos)} videos)")
    else:
        print()

    # Always display grouped by type
    _display_items_grouped(matched_shorts, matched_videos)

    print("\n" + "=" * 80)


def cmd_refresh_cookies(args):
    """Command: refresh-cookies - Extract fresh cookies from browser."""
    print("🍪 Extracting cookies from browser...")

    # Import extract_cookies script
    import subprocess

    result = subprocess.run(
        [sys.executable, "extract_cookies.py"],
        capture_output=False
    )

    if result.returncode == 0:
        print("\n✅ Cookies refreshed!")
    else:
        print("\n❌ Failed to extract cookies")
        sys.exit(1)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s [%(name)s]: %(message)s"
    )


def main():
    # Extract --verbose from argv before argparse (to support any position)
    argv = sys.argv[1:]
    verbose = False
    if "--verbose" in argv:
        verbose = True
        argv = [arg for arg in argv if arg != "--verbose"]
    if "-v" in argv:
        verbose = True
        argv = [arg for arg in argv if arg != "-v"]

    setup_logging(verbose=verbose)

    # Parent parser for shared arguments (can be used in subcommands)
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--auth",
        default="browser_auth.json",
        metavar="FILE",
        help="authentication file (default: browser_auth.json)"
    )
    parent_parser.add_argument(
        "--live-cookies",
        action="store_true",
        help="extract fresh cookies from browser on every command (ignores --auth)"
    )
    parent_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="enable verbose logging (debug level)"
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
  %(prog)s refresh-cookies                         # Refresh authentication cookies
        """
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="available commands",
        metavar="{list,export,search,refresh-cookies}"
    )

    # Command: list
    list_parser = subparsers.add_parser(
        "list",
        help="list history items",
        description="Display YouTube watch history with videos and shorts.",
        parents=[parent_parser]
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="maximum number of items to fetch (default: 50, use 0 for all)"
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="output as JSON instead of human-readable format"
    )
    list_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)"
    )

    # Command: export
    export_parser = subparsers.add_parser(
        "export",
        help="export history to JSON",
        description="Export YouTube watch history to a JSON file.",
        parents=[parent_parser]
    )
    export_parser.add_argument(
        "--output",
        default="youtube_history.json",
        metavar="FILE",
        help="output file path (default: youtube_history.json)"
    )
    export_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="maximum number of items to export (default: 50, use 0 for all)"
    )
    export_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)"
    )

    # Command: search
    search_parser = subparsers.add_parser(
        "search",
        help="search in history",
        description="Search for videos/channels in your watch history.",
        parents=[parent_parser]
    )
    search_parser.add_argument(
        "query",
        metavar="TERM",
        help="search term (matches title or channel name)"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="search in last N items (default: 50, use 0 for all history)"
    )
    search_parser.add_argument(
        "--type",
        choices=["all", "videos", "shorts"],
        default="all",
        help="filter by item type (default: all)"
    )

    # Command: refresh-cookies
    refresh_parser = subparsers.add_parser(
        "refresh-cookies",
        help="refresh browser cookies",
        description="Extract fresh cookies from browser for authentication.",
        parents=[parent_parser]
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check if auth file exists (except for refresh-cookies and --live-cookies)
    if args.command != "refresh-cookies" and not args.live_cookies:
        if not Path(args.auth).exists():
            print(f"❌ Authentication file not found: {args.auth}")
            print("\nRun first:")
            print("  python extract_cookies.py")
            print("\nOr:")
            print("  python yt_history.py refresh-cookies")
            print("\nOr use live mode:")
            print("  python yt_history.py list --live-cookies")
            sys.exit(1)

    # Execute command
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "export":
            cmd_export(args)
        elif args.command == "search":
            cmd_search(args)
        elif args.command == "refresh-cookies":
            cmd_refresh_cookies(args)

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
