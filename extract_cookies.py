#!/usr/bin/env python3
"""
Extract YouTube cookies automatically from browser.
Supports: Chrome, Firefox, Safari, Edge, Brave
"""

import sys
import json
from pathlib import Path

try:
    import browser_cookie3
except ImportError:
    print("❌ Error: 'browser-cookie3' library not installed")
    print("\nInstall with: pip install browser-cookie3")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from src.youtube_client import YouTubeClient


def extract_cookies_from_browser(browser_name='chrome', verbose=True):
    """Extract YouTube cookies from browser.

    Args:
        browser_name: Browser to extract from
        verbose: Print extraction progress (default: True)

    Returns:
        tuple: (cookie_string, cookies_dict)
    """
    if verbose:
        print(f"📡 Extracting cookies from {browser_name.title()}...")

    browser_functions = {
        'chrome': browser_cookie3.chrome,
        'firefox': browser_cookie3.firefox,
        'safari': browser_cookie3.safari,
        'edge': browser_cookie3.edge,
        'brave': browser_cookie3.brave,
    }

    if browser_name not in browser_functions:
        raise ValueError(f"Unsupported browser: {browser_name}")

    try:
        cookiejar = browser_functions[browser_name](domain_name='youtube.com')

        cookies = {}
        for cookie in cookiejar:
            cookies[cookie.name] = cookie.value

        if not cookies:
            raise Exception("No cookies found. Are you logged in to YouTube?")

        if verbose:
            print(f"   ✓ {len(cookies)} cookies extracted")

            critical = ['__Secure-3PAPISID', 'SAPISID', 'HSID', 'SSID', 'SID']
            found = [n for n in critical if n in cookies]

            if found:
                print(f"   ✓ Critical cookies: {', '.join(found)}")

        cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
        return cookie_string, cookies

    except Exception as e:
        if verbose:
            print(f"   ✗ Error: {e}")
        raise


def get_live_cookies(verbose=True):
    """Extract fresh cookies from browser without saving to file.

    Args:
        verbose: Print extraction progress (default: True)

    Returns:
        dict: Cookie dictionary ready for YouTubeClient
    """
    if verbose:
        print("🔴 Live mode: Extracting fresh cookies from browser...")

    # Detect available browsers
    browsers = ['firefox', 'chrome', 'safari', 'edge', 'brave']

    for browser in browsers:
        try:
            _, cookies = extract_cookies_from_browser(browser, verbose=verbose)
            return cookies
        except:
            continue

    raise Exception("No browser available for live cookie extraction")


def save_cookies(cookie_string, filepath='browser_auth.json'):
    """Save cookies to JSON file."""
    print(f"\n💾 Saving cookies...")

    auth_data = {"cookie": cookie_string}

    with open(filepath, 'w') as f:
        json.dump(auth_data, f, indent=2)

    print(f"   ✓ Saved: {Path(filepath).absolute()}")
    return filepath


def test_cookies(auth_file):
    """Test extracted cookies."""
    print(f"\n🧪 Testing authentication...")

    try:
        from src.youtube_client import load_cookies_from_file
        cookies = load_cookies_from_file(auth_file)
        client = YouTubeClient(cookies)
        response = client.get_history()

        from src.history_parser import HistoryParser
        items = HistoryParser.parse_response(response)

        print(f"   ✓ Success! {len(items)} items in history")

        if items:
            print(f"\n   📹 First: {items[0].title}")

        return True

    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


def main():
    print("=" * 60)
    print("AUTOMATIC COOKIE EXTRACTION")
    print("=" * 60)

    print("\n🔍 Detecting browsers...")

    browsers = ['firefox', 'chrome', 'safari', 'edge', 'brave']
    available = []

    for browser in browsers:
        try:
            func = getattr(browser_cookie3, browser)
            func(domain_name='google.com')
            available.append(browser)
            print(f"   ✓ {browser.title()}")
        except:
            print(f"   ✗ {browser.title()}")

    if not available:
        print("\n❌ No browsers found!")
        print("\nTips:")
        print("1. Log in to YouTube in your browser")
        print("2. Chrome 127+ has issues - use Firefox")
        print("3. macOS: allow Keychain access")
        sys.exit(1)

    browser = available[0]
    print(f"\n✓ Using {browser.title()}")

    print(f"\n{'=' * 60}")
    try:
        cookie_string, cookies = extract_cookies_from_browser(browser)
    except Exception as e:
        print(f"\n❌ Failed: {e}")

        if browser == 'chrome':
            print("\n💡 Chrome 127+ blocked cookies.")
            print("   Try Firefox or manual method.")

        sys.exit(1)

    auth_file = save_cookies(cookie_string)
    success = test_cookies(auth_file)

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
