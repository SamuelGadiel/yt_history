#!/usr/bin/env python3
"""
Extract YouTube cookies automatically from browser.
Supports: Chrome, Firefox, Safari, Edge, Brave
"""

import sys
import json
from pathlib import Path
from typing import Optional

try:
    import browser_cookie3
except ImportError:
    print("❌ Error: 'browser-cookie3' library not installed")
    print("\nInstall with: pip install browser-cookie3")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))

from src.auth import extract_cookies_from_browser
from src.youtube_client import YouTubeClient
from src.history_parser import HistoryParser
from src.exceptions import CookieExtractionError, YouTubeHistoryError


def save_cookies(cookie_string: str, filepath: str = 'browser_auth.json') -> str:
    """
    Save cookies to JSON file.

    Args:
        cookie_string: Cookie string to save
        filepath: Output file path

    Returns:
        Absolute path to saved file
    """
    print(f"\n💾 Saving cookies...")

    auth_data = {"cookie": cookie_string}

    with open(filepath, 'w') as f:
        json.dump(auth_data, f, indent=2)

    abs_path = Path(filepath).absolute()
    print(f"   ✓ Saved: {abs_path}")
    return str(abs_path)


def test_cookies(auth_file: str) -> bool:
    """
    Test extracted cookies by fetching history.

    Args:
        auth_file: Path to auth file to test

    Returns:
        True if authentication works, False otherwise
    """
    print(f"\n🧪 Testing authentication...")

    try:
        from src.auth import load_cookies_from_file

        cookies = load_cookies_from_file(auth_file)
        client = YouTubeClient(cookies)
        response = client.get_history()

        items = HistoryParser.parse_response(response)

        print(f"   ✓ Success! {len(items)} items in history")

        if items:
            print(f"\n   📹 First: {items[0].title}")

        return True

    except YouTubeHistoryError as e:
        print(f"   ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def detect_available_browsers() -> list[str]:
    """
    Detect which browsers are available on the system.

    Returns:
        List of available browser names
    """
    print("\n🔍 Detecting browsers...")

    browsers = ['firefox', 'chrome', 'safari', 'edge', 'brave']
    available = []

    for browser in browsers:
        try:
            func = getattr(browser_cookie3, browser)
            # Quick test to see if browser is accessible
            func(domain_name='google.com')
            available.append(browser)
            print(f"   ✓ {browser.title()}")
        except Exception:
            print(f"   ✗ {browser.title()}")

    return available


def extract_from_first_available(browsers: list[str]) -> tuple[str, dict]:
    """
    Extract cookies from first available browser.

    Args:
        browsers: List of browser names to try

    Returns:
        Tuple of (cookie_string, cookies_dict)

    Raises:
        CookieExtractionError: If extraction fails from all browsers
    """
    for browser in browsers:
        try:
            return extract_cookies_from_browser(browser)
        except Exception:
            continue

    raise CookieExtractionError("Failed to extract cookies from all available browsers")


def print_chrome_warning(browser: str) -> None:
    """Print warning if Chrome extraction failed."""
    if browser == 'chrome':
        print("\n💡 Chrome 127+ blocked cookies.")
        print("   Try Firefox or manual method.")


def main() -> None:
    """Main entry point."""
    print("=" * 60)
    print("AUTOMATIC COOKIE EXTRACTION")
    print("=" * 60)

    # Detect browsers
    available = detect_available_browsers()

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
        cookie_string, cookies = extract_from_first_available(available)
    except CookieExtractionError as e:
        print(f"\n❌ Failed: {e}")
        print_chrome_warning(browser)
        sys.exit(1)

    # Save cookies
    auth_file = save_cookies(cookie_string)

    # Test authentication
    success = test_cookies(auth_file)

    # Final message
    print(f"\n{'=' * 60}")
    if success:
        print("✅ SUCCESS!")
        print(f"\nUse with:")
        print(f"  python yt_history.py list")
    else:
        print("⚠️  Cookies extracted but test failed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
