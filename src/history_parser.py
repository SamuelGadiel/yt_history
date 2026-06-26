"""Parser for YouTube watch history."""

from __future__ import annotations

import logging
from typing import Any

from .exceptions import ParseError

logger = logging.getLogger(__name__)


class HistoryItem:
    """Represents a YouTube history item (video or short).

    Attributes:
        video_id: YouTube video ID (11 characters).
        title: Video or short title.
        channel_name: Channel name (may be None for shorts).
        channel_id: Channel ID (may be None for shorts).
        thumbnail_url: Thumbnail URL.
        duration: Video duration (e.g., "10:45", may be None for shorts).
        view_count: View count text (e.g., "1.2M views").
        watched_time: When watched (e.g., "Today", "Yesterday").
        item_type: Type of item ("video" or "short").
    """

    def __init__(
        self,
        video_id: str,
        title: str,
        channel_name: str | None = None,
        channel_id: str | None = None,
        thumbnail_url: str | None = None,
        duration: str | None = None,
        view_count: str | None = None,
        watched_time: str | None = None,
        item_type: str = "video",
    ) -> None:
        """Initialize a history item.

        Args:
            video_id: YouTube video ID.
            title: Video or short title.
            channel_name: Channel name (optional).
            channel_id: Channel ID (optional).
            thumbnail_url: Thumbnail URL (optional).
            duration: Video duration (optional).
            view_count: View count text (optional).
            watched_time: When watched (optional).
            item_type: Type of item ("video" or "short").
        """
        self.video_id = video_id
        self.title = title
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.thumbnail_url = thumbnail_url
        self.duration = duration
        self.view_count = view_count
        self.watched_time = watched_time
        self.item_type = item_type

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON export.

        Returns:
            Dictionary representation with all fields plus generated URL.
        """
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel_name": self.channel_name,
            "channel_id": self.channel_id,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "view_count": self.view_count,
            "watched_time": self.watched_time,
            "type": self.item_type,
            "url": f"https://www.youtube.com/watch?v={self.video_id}",
        }

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"<HistoryItem {self.item_type}: {self.title[:50]}>"


__all__ = ["HistoryItem", "HistoryParser"]


class HistoryParser:
    """Parser for YouTube history API responses.

    Parses JSON responses from YouTube's internal API and extracts
    video and short items with metadata (title, channel, duration, etc.).
    """

    @staticmethod
    def parse_response(response: dict[str, Any]) -> list[HistoryItem]:
        """Parse complete API response.

        Args:
            response: JSON response

        Returns:
            List of HistoryItem
        """
        items: list[HistoryItem] = []

        # Identify response type
        sections = []

        # First page (browseId)
        if "contents" in response:
            try:
                contents = response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0][
                    "tabRenderer"
                ]["content"]
                sections = contents["sectionListRenderer"]["contents"]
            except (KeyError, IndexError) as e:
                logger.error(f"Invalid response structure (first page): {e}", exc_info=True)
                raise ParseError(f"Invalid response structure (first page): {e}") from e

        # Continuation pages
        elif "onResponseReceivedActions" in response:
            try:
                actions = response["onResponseReceivedActions"]
                for action in actions:
                    if "appendContinuationItemsAction" in action:
                        sections = action["appendContinuationItemsAction"]["continuationItems"]
                        break
            except (KeyError, IndexError) as e:
                logger.error(f"Invalid response structure (continuation): {e}", exc_info=True)
                raise ParseError(f"Invalid response structure (continuation): {e}") from e

        else:
            raise ParseError("Response without 'contents' or 'onResponseReceivedActions'")

        # Process each section
        for section in sections:
            # itemSectionRenderer contains video items
            if "itemSectionRenderer" in section:
                section_items = section["itemSectionRenderer"].get("contents", [])

                # Section header may contain timestamp ("Today", "Yesterday", etc)
                section_header = section["itemSectionRenderer"].get("header", {})
                watched_time = HistoryParser._extract_section_timestamp(section_header)

                # Parse each item
                for item_data in section_items:
                    parsed_items = HistoryParser._parse_item(item_data, watched_time)
                    items.extend(parsed_items)

        return items

    @staticmethod
    def _extract_section_timestamp(header: dict[str, Any]) -> str | None:
        """Extract timestamp from section (e.g., "Today", "Yesterday", specific date)."""
        if not header:
            return None

        try:
            # itemSectionHeaderRenderer → title → simpleText
            if "itemSectionHeaderRenderer" in header:
                title = header["itemSectionHeaderRenderer"].get("title", {})
                return title.get("simpleText") or title.get("runs", [{}])[0].get("text")
        except (KeyError, IndexError):
            pass

        return None

    @staticmethod
    def _parse_item(
        item_data: dict[str, Any], watched_time: str | None = None
    ) -> list[HistoryItem]:
        """Parse single history item.

        Args:
            item_data: Item data (can be various renderer types)
            watched_time: Section timestamp (when watched)

        Returns:
            List of HistoryItem (usually 1, but reelShelfRenderer returns multiple)
        """
        # Identify renderer type
        renderer_type = next(iter(item_data.keys())) if item_data else None

        if not renderer_type:
            return []

        # Shorts (reelShelfRenderer) - returns multiple items
        if renderer_type == "reelShelfRenderer":
            return HistoryParser._parse_reel_shelf(item_data[renderer_type], watched_time)

        # Regular videos (lockupViewModel)
        elif renderer_type == "lockupViewModel":
            parsed = HistoryParser._parse_lockup_view_model(item_data[renderer_type], watched_time)
            return [parsed] if parsed else []

        # Old videos may use videoRenderer
        elif renderer_type == "videoRenderer":
            parsed = HistoryParser._parse_video_renderer(item_data[renderer_type], watched_time)
            return [parsed] if parsed else []

        # Unsupported type
        return []

    @staticmethod
    def _parse_reel_shelf(data: dict[str, Any], watched_time: str | None) -> list[HistoryItem]:
        """Parse shorts (reelShelfRenderer) - returns all shorts in shelf."""
        parsed_shorts: list[HistoryItem] = []

        try:
            # reelShelfRenderer contains multiple shorts
            reel_items = data.get("items", [])

            if not reel_items:
                return []

            # Parse all shorts
            for reel_item in reel_items:
                if "shortsLockupViewModel" not in reel_item:
                    continue

                try:
                    short_data = reel_item["shortsLockupViewModel"]

                    # Get video ID from reelWatchEndpoint
                    on_tap = short_data.get("onTap", {})
                    innertube_cmd = on_tap.get("innertubeCommand", {})
                    reel_endpoint = innertube_cmd.get("reelWatchEndpoint", {})
                    video_id = reel_endpoint.get("videoId", "")

                    if not video_id:
                        continue

                    # Title and view count from overlayMetadata
                    overlay = short_data.get("overlayMetadata", {})
                    title = overlay.get("primaryText", {}).get("content", "Untitled short")
                    view_count = overlay.get("secondaryText", {}).get("content")

                    # Thumbnail from reelWatchEndpoint
                    thumbnail_data = reel_endpoint.get("thumbnail", {})
                    thumbnails = thumbnail_data.get("thumbnails", [])
                    thumbnail_url = thumbnails[0].get("url") if thumbnails else None

                    parsed_shorts.append(
                        HistoryItem(
                            video_id=video_id,
                            title=title,
                            thumbnail_url=thumbnail_url,
                            view_count=view_count,
                            watched_time=watched_time,
                            item_type="short",
                        )
                    )

                except (KeyError, IndexError, AttributeError, TypeError) as e:
                    logger.debug(f"Failed to parse short item: {e}", exc_info=True)
                    continue

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse reelShelfRenderer: {e}", exc_info=True)

        return parsed_shorts

    @staticmethod
    def _parse_lockup_view_model(
        data: dict[str, Any], watched_time: str | None
    ) -> HistoryItem | None:
        """Parse regular videos (lockupViewModel)."""
        try:
            # Video metadata
            metadata = data.get("metadata", {}).get("lockupMetadataViewModel", {})

            # Title
            title_data = metadata.get("title", {})
            title = title_data.get("content", "Untitled video")

            # Channel ID from decoratedAvatarViewModel
            channel_id = None
            image_data_meta = metadata.get("image", {})
            decorated_avatar = image_data_meta.get("decoratedAvatarViewModel", {})
            renderer_context = decorated_avatar.get("rendererContext", {})
            command_context = renderer_context.get("commandContext", {})
            on_tap = command_context.get("onTap", {})
            innertube_cmd = on_tap.get("innertubeCommand", {})
            browse_endpoint = innertube_cmd.get("browseEndpoint", {})
            channel_id = browse_endpoint.get("browseId")

            # Additional metadata (channel name, views)
            metadata_parts = (
                metadata.get("metadata", {})
                .get("contentMetadataViewModel", {})
                .get("metadataRows", [])
            )

            channel_name = None
            view_count = None

            # Parse metadata rows
            for row in metadata_parts:
                parts = row.get("metadataParts", [])
                if len(parts) >= 1:
                    # First part is usually channel
                    if not channel_name:
                        channel_name = parts[0].get("text", {}).get("content")

                    # Second part may be views
                    if len(parts) >= 2 and not view_count:
                        view_count = parts[1].get("text", {}).get("content")

            # Video ID
            content_id = data.get("contentId", "")
            video_id = content_id

            # Thumbnail and duration from contentImage
            content_image = data.get("contentImage", {})
            thumbnail_vm = content_image.get("thumbnailViewModel", {})
            image_data = thumbnail_vm.get("image", {})

            # Thumbnail URL
            sources = image_data.get("sources", [])
            thumbnail = sources[-1].get("url") if sources else None  # Last source = highest quality

            # Duration from overlays
            duration = None
            overlays = image_data.get("overlays", [])
            for overlay in overlays:
                if "thumbnailBottomOverlayViewModel" in overlay:
                    bottom = overlay["thumbnailBottomOverlayViewModel"]
                    badges = bottom.get("badges", [])
                    for badge in badges:
                        if "thumbnailBadgeViewModel" in badge:
                            badge_vm = badge["thumbnailBadgeViewModel"]
                            duration = badge_vm.get("text")
                            break
                    if duration:
                        break

            return HistoryItem(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                channel_id=channel_id,
                view_count=view_count,
                duration=duration,
                thumbnail_url=thumbnail,
                watched_time=watched_time,
                item_type="video",
            )

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse lockupViewModel: {e}", exc_info=True)

        return None

    @staticmethod
    def _parse_video_renderer(data: dict[str, Any], watched_time: str | None) -> HistoryItem | None:
        """Parse old format (videoRenderer)."""
        try:
            video_id = data.get("videoId")
            if not video_id:
                return None

            # Title
            title_data = data.get("title", {})
            title = title_data.get("simpleText") or (
                title_data.get("runs", [{}])[0].get("text")
                if title_data.get("runs")
                else "Untitled video"
            )

            # Channel
            owner_text = data.get("ownerText", {})
            channel_name = None
            channel_id = None

            if owner_text.get("runs"):
                channel_name = owner_text["runs"][0].get("text")
                browse_endpoint = (
                    owner_text["runs"][0].get("navigationEndpoint", {}).get("browseEndpoint", {})
                )
                channel_id = browse_endpoint.get("browseId")

            # Thumbnail
            thumbnails = data.get("thumbnail", {}).get("thumbnails", [])
            thumbnail_url = thumbnails[-1]["url"] if thumbnails else None

            # Duration
            duration = data.get("lengthText", {}).get("simpleText")

            # Views
            view_count = data.get("shortViewCountText", {}).get("simpleText")

            return HistoryItem(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                channel_id=channel_id,
                thumbnail_url=thumbnail_url,
                duration=duration,
                view_count=view_count,
                watched_time=watched_time,
                item_type="video",
            )

        except (KeyError, IndexError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse videoRenderer: {e}", exc_info=True)

        return None
