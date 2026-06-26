"""Authentication and cookie management."""

import json
from pathlib import Path
from typing import Dict
from argparse import Namespace

from .exceptions import AuthenticationError, CookieExtractionError


def load_cookies(args: Namespace) -> Dict[str, str]:
    """
    Load cookies from file or live extraction based on args.

    Args:
        args: Parsed command-line arguments with 'live_cookies' and 'auth' attributes

    Returns:
        Cookie dictionary

    Raises:
        AuthenticationError: If cookie loading fails
    """
    if args.live_cookies:
        verbose = getattr(args, 'verbose', False) and not getattr(args, 'json', False)
        return get_live_cookies(verbose=verbose)
    else:
        return load_cookies_from_file(args.auth)


def load_cookies_from_file(filepath: str) -> Dict[str, str]:
    """
    Load cookies saved from browser.

    Args:
        filepath: Path to browser_auth.json

    Returns:
        Dict with cookies

    Raises:
        AuthenticationError: If file not found or invalid format
    """
    file_path = Path(filepath)

    if not file_path.exists():
        raise AuthenticationError(f"Authentication file not found: {filepath}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise AuthenticationError(f"Invalid JSON in {filepath}: {e}")
    except IOError as e:
        raise AuthenticationError(f"Failed to read {filepath}: {e}")

    cookie_string = data.get('cookie', '')

    if not cookie_string:
        raise AuthenticationError(f"'cookie' field not found in {filepath}")

    cookies = {}
    for item in cookie_string.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value

    return cookies


def get_live_cookies(verbose: bool = True) -> Dict[str, str]:
    """
    Extract fresh cookies from browser without saving to file.

    Args:
        verbose: Print extraction progress (default: True)

    Returns:
        Cookie dictionary ready for YouTubeClient

    Raises:
        CookieExtractionError: If extraction fails
    """
    try:
        import browser_cookie3
    except ImportError:
        raise CookieExtractionError(
            "'browser-cookie3' library not installed\n"
            "Install with: pip install browser-cookie3"
        )

    if verbose:
        print("🔴 Live mode: Extracting fresh cookies from browser...")

    # Detect available browsers
    browsers = ['firefox', 'chrome', 'safari', 'edge', 'brave']

    last_error = None
    for browser in browsers:
        try:
            _, cookies = extract_cookies_from_browser(browser, verbose=verbose)
            return cookies
        except Exception as e:
            last_error = e
            continue

    raise CookieExtractionError(
        f"No browser available for live cookie extraction. Last error: {last_error}"
    )


def extract_cookies_from_browser(
    browser_name: str = 'chrome',
    verbose: bool = True
) -> tuple[str, Dict[str, str]]:
    """
    Extract YouTube cookies from browser.

    Args:
        browser_name: Browser to extract from (chrome, firefox, safari, edge, brave)
        verbose: Print extraction progress (default: True)

    Returns:
        Tuple of (cookie_string, cookies_dict)

    Raises:
        CookieExtractionError: If extraction fails
        ImportError: If browser_cookie3 not installed
    """
    import browser_cookie3

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
            raise CookieExtractionError("No cookies found. Are you logged in to YouTube?")

        if verbose:
            print(f"   ✓ {len(cookies)} cookies extracted")

            critical = ['__Secure-3PAPISID', 'SAPISID', 'HSID', 'SSID', 'SID']
            found = [n for n in critical if n in cookies]

            if found:
                print(f"   ✓ Critical cookies: {', '.join(found)}")

        cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
        return cookie_string, cookies

    except CookieExtractionError:
        raise
    except Exception as e:
        if verbose:
            print(f"   ✗ Error: {e}")
        raise CookieExtractionError(f"Failed to extract cookies from {browser_name}: {e}")


__all__ = [
    'load_cookies',
    'load_cookies_from_file',
    'get_live_cookies',
    'extract_cookies_from_browser'
]
