"""
History fetcher with pagination support.
"""

from typing import List, Optional, Callable
import time

from .youtube_client import YouTubeClient
from .history_parser import HistoryParser, HistoryItem


class HistoryFetcher:
    """Fetch history with pagination support."""

    def __init__(self, client: YouTubeClient):
        """
        Args:
            client: Configured YouTube client
        """
        self.client = client

    def fetch_all(
        self,
        limit: Optional[int] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> List[HistoryItem]:
        """
        Fetch all history (or up to limit).

        Args:
            limit: Maximum number of items (None = all)
            progress_callback: Function called on each page (receives total items)

        Returns:
            List of HistoryItem

        Raises:
            requests.HTTPError: If request fails
        """
        all_items: List[HistoryItem] = []
        continuation: Optional[str] = None
        page = 0

        while True:
            page += 1

            # Fetch page
            response = self.client.get_history(continuation)

            # Parse items
            items = HistoryParser.parse_response(response)
            all_items.extend(items)

            # Progress callback (always call, even if list is empty)
            if progress_callback:
                progress_callback(len(all_items))

            # Check limit
            if limit and len(all_items) >= limit:
                all_items = all_items[:limit]
                break

            # Check continuation
            continuation = self.client.get_continuation_token(response)

            if not continuation:
                # End of history
                break

            if page > 1:
                time.sleep(0.5)

        return all_items

    def fetch_page(self, continuation: Optional[str] = None) -> tuple[List[HistoryItem], Optional[str]]:
        """
        Fetch one page of history.

        Args:
            continuation: Continuation token (None = first page)

        Returns:
            Tuple (items, next_continuation)
        """
        response = self.client.get_history(continuation)
        items = HistoryParser.parse_response(response)
        next_continuation = self.client.get_continuation_token(response)

        return items, next_continuation
