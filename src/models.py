"""Data models and dataclasses."""

from dataclasses import dataclass, field
from typing import List, Dict, Any

from .history_parser import HistoryItem


@dataclass
class HistoryGroup:
    """Grouped history items by type."""
    total_items: int
    statistics: Dict[str, int]
    videos: List[HistoryItem] = field(default_factory=list)
    shorts: List[HistoryItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "total_items": self.total_items,
            "statistics": self.statistics,
            "videos": [item.to_dict() for item in self.videos],
            "shorts": [item.to_dict() for item in self.shorts]
        }

    def all_items(self) -> List[HistoryItem]:
        """Get all items (videos + shorts) in order."""
        return self.videos + self.shorts


__all__ = ['HistoryGroup']
