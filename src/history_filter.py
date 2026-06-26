"""History filtering and grouping utilities."""

from typing import List, Dict

from .models import HistoryGroup
from .history_parser import HistoryItem


def filter_by_type(grouped: HistoryGroup, type_filter: str) -> HistoryGroup:
    """
    Filter grouped history by item type.

    Args:
        grouped: HistoryGroup to filter
        type_filter: Filter value ("all", "videos", "shorts")

    Returns:
        New HistoryGroup with filtered items and recalculated statistics
    """
    if type_filter == "all":
        return grouped

    videos = grouped.videos if type_filter == "videos" else []
    shorts = grouped.shorts if type_filter == "shorts" else []

    stats = recalculate_stats(videos, shorts)

    return HistoryGroup(
        total_items=len(videos) + len(shorts),
        statistics=stats,
        videos=videos,
        shorts=shorts
    )


def recalculate_stats(videos: List[HistoryItem], shorts: List[HistoryItem]) -> Dict[str, int]:
    """
    Recalculate statistics for videos and shorts.

    Args:
        videos: List of video items
        shorts: List of short items

    Returns:
        Statistics dict with counts by type
    """
    stats = {}
    if videos:
        stats["video"] = len(videos)
    if shorts:
        stats["short"] = len(shorts)
    return stats


def separate_by_type(items: List[HistoryItem]) -> tuple[List[HistoryItem], List[HistoryItem]]:
    """
    Separate items into videos and shorts.

    Args:
        items: List of mixed HistoryItem objects

    Returns:
        Tuple of (videos, shorts)
    """
    videos = [item for item in items if item.item_type == "video"]
    shorts = [item for item in items if item.item_type == "short"]
    return videos, shorts


def search_items(
    items: List[HistoryItem],
    query: str
) -> List[HistoryItem]:
    """
    Search items by title or channel name.

    Args:
        items: List of HistoryItem to search
        query: Search term (case-insensitive)

    Returns:
        List of matching items
    """
    query_lower = query.lower()
    return [
        item for item in items
        if query_lower in item.title.lower() or
           (item.channel_name and query_lower in item.channel_name.lower())
    ]


__all__ = [
    'filter_by_type',
    'recalculate_stats',
    'separate_by_type',
    'search_items'
]
