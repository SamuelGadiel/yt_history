"""Data models and dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .history_parser import HistoryItem


@dataclass
class HistoryGroup:
    """Grouped history items by type."""

    total_items: int
    statistics: dict[str, int]
    videos: list[HistoryItem] = field(default_factory=list)
    shorts: list[HistoryItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "total_items": self.total_items,
            "statistics": self.statistics,
            "videos": [item.to_dict() for item in self.videos],
            "shorts": [item.to_dict() for item in self.shorts],
        }

    def all_items(self) -> list[HistoryItem]:
        """Get all items (videos + shorts) in order."""
        return self.videos + self.shorts


__all__ = ["HistoryGroup"]
