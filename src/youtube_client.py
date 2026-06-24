"""
HTTP client for YouTube API (watch history).
"""

import json
import time
import hashlib
import os
from typing import Dict, Any, Optional
from pathlib import Path

import requests


class YouTubeClient:
    """Client for YouTube API."""

    BASE_URL = "https://www.youtube.com/youtubei/v1/"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    @staticmethod
    def _load_env_config() -> Dict[str, str]:
        """Load configuration from .env file"""
        env_path = Path(__file__).parent.parent / '.env'

        if not env_path.exists():
            raise FileNotFoundError(
                f".env not found at {env_path}\n"
                f"Copy .env.example to .env and configure YOUTUBE_API_KEY"
            )

        config = {
            'api_key': None,
            'language': None,  # Default: None (YouTube assumes English)
            'region': None     # Default: None (YouTube assumes US)
        }

        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'YOUTUBE_API_KEY' and value and value != 'your_api_key_here':
                        config['api_key'] = value
                    elif key == 'YOUTUBE_LANGUAGE' and value:
                        config['language'] = value
                    elif key == 'YOUTUBE_REGION' and value:
                        config['region'] = value

        if not config['api_key']:
            raise ValueError(
                "YOUTUBE_API_KEY not configured in .env\n"
                "Set it to a valid YouTube API key (see README for instructions)"
            )

        return config

    def __init__(self, cookies: Dict[str, str]):
        """
        Initialize YouTube client.

        Args:
            cookies: Dict with YouTube cookies (extracted from browser)
        """
        self.cookies = cookies
        self.session = requests.Session()

        # Load config from .env
        config = self._load_env_config()
        self.api_key = config['api_key']
        language = config['language']
        region = config['region']

        self.session.headers.update(self._get_base_headers(language))

        self.context = {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20250124.00.00",
                "userAgent": self.USER_AGENT,
            },
            "user": {
                "lockedSafetyMode": False
            }
        }

        # Add locale only if configured
        if language:
            self.context["client"]["hl"] = language
        if region:
            self.context["client"]["gl"] = region

    def _get_base_headers(self, language: Optional[str]) -> Dict[str, str]:
        """Return HTTP headers for authentication."""
        cookie_string = '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
        sapisid = self.cookies.get('SAPISID') or self.cookies.get('__Secure-3PAPISID')

        if not sapisid:
            raise ValueError("SAPISID cookie not found. Please log in to YouTube in your browser.")

        timestamp = str(int(time.time()))
        origin = "https://www.youtube.com"
        hash_string = f"{timestamp} {sapisid} {origin}"
        sapisidhash = hashlib.sha1(hash_string.encode()).hexdigest()
        authorization = f"SAPISIDHASH {timestamp}_{sapisidhash}"

        # Build Accept-Language header
        if language:
            lang_code = language.split('-')[0] if '-' in language else language
            accept_language = f"{language},{lang_code};q=0.9,en-US;q=0.8,en;q=0.7"
        else:
            accept_language = "en-US,en;q=0.9"

        return {
            "User-Agent": self.USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": accept_language,
            "Content-Type": "application/json",
            "Cookie": cookie_string,
            "Origin": origin,
            "Referer": origin + "/",
            "Authorization": authorization,
            "X-Goog-AuthUser": "0",
            "X-Origin": origin,
        }

    def _send_request(self, endpoint: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send HTTP request to YouTube API.

        Args:
            endpoint: Endpoint name
            body: JSON payload (optional)

        Returns:
            JSON response

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}?key={self.api_key}&prettyPrint=false"

        payload = body or {}
        payload["context"] = self.context

        response = self.session.post(url, json=payload)

        if response.status_code != 200:
            raise requests.HTTPError(
                f"YouTube API returned {response.status_code}: {response.text[:200]}"
            )

        return response.json()

    def get_history(self, continuation: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch YouTube watch history.

        Args:
            continuation: Pagination token (None = first page)

        Returns:
            JSON response with history

        Raises:
            requests.HTTPError: If request fails
        """
        body = {"continuation": continuation} if continuation else {"browseId": "FEhistory"}
        return self._send_request("browse", body)

    def get_continuation_token(self, response: Dict[str, Any]) -> Optional[str]:
        """
        Extract pagination token from response.

        Args:
            response: JSON response

        Returns:
            Pagination token or None
        """
        try:
            if "contents" in response:
                contents = response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]
                sections = contents["sectionListRenderer"]["contents"]
            elif "onResponseReceivedActions" in response:
                actions = response["onResponseReceivedActions"]
                for action in actions:
                    if "appendContinuationItemsAction" in action:
                        sections = action["appendContinuationItemsAction"]["continuationItems"]
                        break
                else:
                    return None
            else:
                return None

            for section in reversed(sections):
                if "continuationItemRenderer" in section:
                    cont_endpoint = section["continuationItemRenderer"]["continuationEndpoint"]
                    continuation_command = cont_endpoint["continuationCommand"]
                    return continuation_command.get("token")

        except (KeyError, IndexError):
            pass

        return None

    def get_library(self) -> Dict[str, Any]:
        """Fetch YouTube library."""
        body = {"browseId": "FElibrary"}
        return self._send_request("browse", body)

    def get_subscriptions(self) -> Dict[str, Any]:
        """Fetch YouTube subscriptions."""
        body = {"browseId": "FEsubscriptions"}
        return self._send_request("browse", body)


def load_cookies_from_file(filepath: str) -> Dict[str, str]:
    """
    Load cookies saved from browser.

    Args:
        filepath: Path to browser_auth.json

    Returns:
        Dict with cookies
    """
    with open(filepath, 'r') as f:
        data = json.load(f)

    cookie_string = data.get('cookie', '')

    if not cookie_string:
        raise ValueError(f"'cookie' field not found in {filepath}")

    cookies = {}
    for item in cookie_string.split('; '):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value

    return cookies
