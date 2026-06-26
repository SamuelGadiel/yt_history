"""History fetcher with pagination support."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .history_parser import HistoryItem, HistoryParser
from .models import HistoryGroup

if TYPE_CHECKING:
    from collections.abc import Callable

    from .youtube_client import YouTubeClient


class HistoryFetcher:
    """Fetch history with pagination support."""

    def __init__(self, client: YouTubeClient) -> None:
        """Initialize history fetcher.

        Args:
            client: Configured YouTube client
        """
        self.client = client

    def fetch_all(
        self, limit: int | None = None, progress_callback: Callable[[int], None] | None = None
    ) -> list[HistoryItem]:
        """Fetch all history (or up to limit).

        Args:
            limit: Maximum number of items (None = all)
            progress_callback: Function called on each page (receives total items)

        Returns:
            List of HistoryItem

        Raises:
            requests.HTTPError: If request fails
        """
        all_items: list[HistoryItem] = []
        continuation: str | None = None
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

    def fetch_page(self, continuation: str | None = None) -> tuple[list[HistoryItem], str | None]:
        """Fetch one page of history.

        Args:
            continuation: Continuation token (None = first page)

        Returns:
            Tuple (items, next_continuation)
        """
        response = self.client.get_history(continuation)
        items = HistoryParser.parse_response(response)
        next_continuation = self.client.get_continuation_token(response)

        return items, next_continuation

    def fetch_all_grouped(
        self, limit: int | None = None, progress_callback: Callable[[int], None] | None = None
    ) -> HistoryGroup:
        """Fetch all history grouped by type.

        Args:
            limit: Maximum number of items (None = all)
            progress_callback: Function called on each page (receives total items)

        Returns:
            HistoryGroup with videos and shorts separated
        """
        all_items = self.fetch_all(limit=limit, progress_callback=progress_callback)

        # Group by type
        videos = [item for item in all_items if item.item_type == "video"]
        shorts = [item for item in all_items if item.item_type == "short"]

        # Statistics
        stats: dict[str, int] = {}
        for item in all_items:
            stats[item.item_type] = stats.get(item.item_type, 0) + 1

        return HistoryGroup(
            total_items=len(all_items), statistics=stats, videos=videos, shorts=shorts
        )


__all__ = ["HistoryFetcher"]
