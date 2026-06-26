"""HTTP client for YouTube API (watch history)."""

from __future__ import annotations

import hashlib
import time
from typing import Any

import requests

from .config import AppConfig, load_env_config
from .exceptions import APIError, AuthenticationError


class YouTubeClient:
    """Client for YouTube API."""

    BASE_URL = "https://www.youtube.com/youtubei/v1/"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self, cookies: dict[str, str], config: AppConfig | None = None):
        """Initialize YouTube client.

        Args:
            cookies: Dict with YouTube cookies (extracted from browser)
            config: Optional AppConfig instance (loads from .env if None)

        Raises:
            AuthenticationError: If required cookies are missing
            ConfigError: If configuration is invalid
        """
        self.cookies = cookies
        self.session = requests.Session()

        # Load config if not provided
        if config is None:
            config = load_env_config()

        self.api_key = config.api_key
        language = config.language
        region = config.region

        self.session.headers.update(self._get_base_headers(language))

        self.context: dict[str, Any] = {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20250124.00.00",
                "userAgent": self.USER_AGENT,
            },
            "user": {"lockedSafetyMode": False},
        }

        # Add locale only if configured
        if language:
            self.context["client"]["hl"] = language
        if region:
            self.context["client"]["gl"] = region

    def _get_base_headers(self, language: str | None) -> dict[str, str]:
        """Build HTTP headers for authentication.

        Args:
            language: Optional language code (e.g., "en-US", "pt-BR")

        Returns:
            Dict of HTTP headers

        Raises:
            AuthenticationError: If SAPISID cookie not found
        """
        cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        sapisid = self.cookies.get("SAPISID") or self.cookies.get("__Secure-3PAPISID")

        if not sapisid:
            raise AuthenticationError(
                "SAPISID cookie not found. Please log in to YouTube in your browser."
            )

        timestamp = str(int(time.time()))
        origin = "https://www.youtube.com"
        hash_string = f"{timestamp} {sapisid} {origin}"
        sapisidhash = hashlib.sha1(hash_string.encode()).hexdigest()
        authorization = f"SAPISIDHASH {timestamp}_{sapisidhash}"

        # Build Accept-Language header
        if language:
            lang_code = language.split("-")[0] if "-" in language else language
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

    def _send_request(self, endpoint: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send HTTP request to YouTube API.

        Args:
            endpoint: Endpoint name (e.g., "browse")
            body: JSON payload (optional)

        Returns:
            JSON response

        Raises:
            APIError: If request fails or returns non-200 status
        """
        url = f"{self.BASE_URL}{endpoint}?key={self.api_key}&prettyPrint=false"

        payload: dict[str, Any] = body.copy() if body else {}
        payload["context"] = self.context

        try:
            response = self.session.post(url, json=payload)
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}") from e

        if response.status_code != 200:
            raise APIError(f"YouTube API returned {response.status_code}: {response.text[:200]}")

        try:
            return response.json()
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}") from e

    def get_history(self, continuation: str | None = None) -> dict[str, Any]:
        """Fetch YouTube watch history.

        Args:
            continuation: Pagination token (None = first page)

        Returns:
            JSON response with history

        Raises:
            APIError: If request fails
        """
        body = {"continuation": continuation} if continuation else {"browseId": "FEhistory"}
        return self._send_request("browse", body)

    def get_continuation_token(self, response: dict[str, Any]) -> str | None:
        """Extract pagination token from response.

        Args:
            response: JSON response

        Returns:
            Pagination token or None
        """
        try:
            if "contents" in response:
                contents = response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0][
                    "tabRenderer"
                ]["content"]
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

    def get_library(self) -> dict[str, Any]:
        """Fetch YouTube library.

        Returns:
            JSON response with library data

        Raises:
            APIError: If request fails
        """
        body = {"browseId": "FElibrary"}
        return self._send_request("browse", body)

    def get_subscriptions(self) -> dict[str, Any]:
        """Fetch YouTube subscriptions.

        Returns:
            JSON response with subscriptions

        Raises:
            APIError: If request fails
        """
        body = {"browseId": "FEsubscriptions"}
        return self._send_request("browse", body)


__all__ = ["YouTubeClient"]
