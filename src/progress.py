"""Progress reporting utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class ProgressReporter:
    """Creates progress callback functions for history fetching.

    Provides factory methods for creating progress callbacks that display
    loading status during long-running operations (fetch, export, search).
    """

    @staticmethod
    def create_loading_callback(
        verbose: bool, json_mode: bool = False, limit: int | None = None
    ) -> Callable[[int], None]:
        """Create a progress callback for loading operations.

        Args:
            verbose: Whether to show progress
            json_mode: Whether in JSON output mode
            limit: Optional limit for max display

        Returns:
            Progress callback function
        """
        if json_mode or not verbose:
            return lambda total: None

        def progress(total: int) -> None:
            max_display = limit if limit else total
            print(f"\r   Loading... {min(total, max_display)} items", end="", flush=True)

        return progress

    @staticmethod
    def create_fetching_callback(verbose: bool, limit: int | None = None) -> Callable[[int], None]:
        """Create a progress callback for fetching/export operations.

        Args:
            verbose: Whether to show progress
            limit: Optional limit for max display

        Returns:
            Progress callback function
        """
        if not verbose:
            return lambda total: None

        def progress(total: int) -> None:
            max_display = limit if limit else total
            print(f"\r   Fetching... {min(total, max_display)} items", end="", flush=True)

        return progress

    @staticmethod
    def create_analyzing_callback(verbose: bool, limit: int | None = None) -> Callable[[int], None]:
        """Create a progress callback for analyzing/search operations.

        Args:
            verbose: Whether to show progress
            limit: Optional limit for max display

        Returns:
            Progress callback function
        """
        if not verbose:
            return lambda total: None

        def progress(total: int) -> None:
            max_display = limit if limit else total
            print(f"\r   Analyzing... {min(total, max_display)} items", end="", flush=True)

        return progress


__all__ = ["ProgressReporter"]
