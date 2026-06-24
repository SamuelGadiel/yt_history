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
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.youtube_client import YouTubeClient, load_cookies_from_file
from src.history_fetcher import HistoryFetcher


def cmd_list(args):
    """Command: list - Display history items."""
    if not args.json:
        print("🔍 Fetching YouTube history...")

    # Load cookies
    cookies = load_cookies_from_file(args.auth)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    def progress(total):
        if not args.json:
            print(f"\r   Loading... {total} items", end="", flush=True)

    # Fetch items
    items = fetcher.fetch_all(limit=args.limit, progress_callback=progress)

    if not args.json:
        print()  # New line after progress

    if not items:
        if args.json:
            print(json.dumps([], indent=2))
        else:
            print("❌ No items found in history.")
        return

    # JSON output
    if args.json:
        items_data = [item.to_dict() for item in items]
        print(json.dumps(items_data, indent=2, ensure_ascii=False))
        return

    # Human-readable output
    print(f"\n✅ {len(items)} items found\n")
    print("=" * 80)

    # Display items
    for i, item in enumerate(items, 1):
        type_emoji = "🎬" if item.item_type == "video" else "📱"

        print(f"\n{i}. {type_emoji} {item.title}")

        if item.channel_name:
            print(f"   📺 {item.channel_name}")

        if item.watched_time:
            print(f"   🕐 {item.watched_time}")

        print(f"   🔗 https://www.youtube.com/watch?v={item.video_id}")

    print("\n" + "=" * 80)


def cmd_export(args):
    """Command: export - Export history to file."""
    print("📦 Exporting YouTube history...")

    # Load cookies
    cookies = load_cookies_from_file(args.auth)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    def progress(total):
        print(f"\r   Fetching... {total} items", end="", flush=True)

    # Fetch items (with limit, 0 = all)
    limit = None if args.limit == 0 else args.limit
    items = fetcher.fetch_all(limit=limit, progress_callback=progress)
    print()  # New line

    if not items:
        print("❌ No items found.")
        return

    # Statistics
    stats = {}
    for item in items:
        stats[item.item_type] = stats.get(item.item_type, 0) + 1

    # Prepare data
    export_data = {
        "total_items": len(items),
        "statistics": stats,
        "items": [item.to_dict() for item in items]
    }

    # Save file
    output = Path(args.output)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Exported: {output.absolute()}")
    print(f"   Total: {len(items)} items")
    print(f"   Statistics:")
    for item_type, count in stats.items():
        print(f"     - {item_type}: {count}")


def cmd_search(args):
    """Command: search - Search term in history."""
    print(f"🔎 Searching '{args.query}' in history...")

    # Load cookies
    cookies = load_cookies_from_file(args.auth)
    client = YouTubeClient(cookies)
    fetcher = HistoryFetcher(client)

    # Progress callback
    def progress(total):
        print(f"\r   Analyzing... {total} items", end="", flush=True)

    # Fetch items (with limit, 0 = all)
    limit = None if args.limit == 0 else args.limit
    all_items = fetcher.fetch_all(limit=limit, progress_callback=progress)
    print()

    if not all_items:
        print("❌ History is empty.")
        return

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

    print(f"\n✅ {len(matches)} result(s) found\n")
    print("=" * 80)

    # Display results
    for i, item in enumerate(matches, 1):
        type_emoji = "🎬" if item.item_type == "video" else "📱"

        print(f"\n{i}. {type_emoji} {item.title}")

        if item.channel_name:
            print(f"   📺 {item.channel_name}")

        if item.watched_time:
            print(f"   🕐 {item.watched_time}")

        print(f"   🔗 https://www.youtube.com/watch?v={item.video_id}")

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


def main():
    parser = argparse.ArgumentParser(
        prog="yt_history",
        description="YouTube History CLI - Fetch complete YouTube watch history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                          # List last 50 items
  %(prog)s list --limit 200              # List last 200 items
  %(prog)s search "cooking"              # Search in last 50 items
  %(prog)s search "cooking" --limit 200  # Search in last 200 items
  %(prog)s search "cooking" --limit 0    # Search in all history
  %(prog)s export                        # Export last 50 items
  %(prog)s export --limit 0              # Export all history
  %(prog)s export --output my.json       # Export to custom file
  %(prog)s refresh-cookies               # Refresh authentication cookies
        """
    )

    parser.add_argument(
        "--auth",
        default="browser_auth.json",
        metavar="FILE",
        help="authentication file (default: browser_auth.json)"
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
        description="Display YouTube watch history with videos and shorts."
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="maximum number of items to fetch (default: 50)"
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="output as JSON instead of human-readable format"
    )

    # Command: export
    export_parser = subparsers.add_parser(
        "export",
        help="export history to JSON",
        description="Export YouTube watch history to a JSON file."
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

    # Command: search
    search_parser = subparsers.add_parser(
        "search",
        help="search in history",
        description="Search for videos/channels in your watch history."
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

    # Command: refresh-cookies
    refresh_parser = subparsers.add_parser(
        "refresh-cookies",
        help="refresh browser cookies",
        description="Extract fresh cookies from browser for authentication."
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check if auth file exists (except for refresh-cookies)
    if args.command != "refresh-cookies":
        if not Path(args.auth).exists():
            print(f"❌ Authentication file not found: {args.auth}")
            print("\nRun first:")
            print("  python extract_cookies.py")
            print("\nOr:")
            print("  python yt_history.py refresh-cookies")
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
