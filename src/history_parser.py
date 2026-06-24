"""
Parser for YouTube watch history.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class HistoryItem:
    """Represents a history item."""

    def __init__(
        self,
        video_id: str,
        title: str,
        channel_name: Optional[str] = None,
        channel_id: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration: Optional[str] = None,
        view_count: Optional[str] = None,
        published_time: Optional[str] = None,
        watched_time: Optional[str] = None,
        item_type: str = "video"
    ):
        self.video_id = video_id
        self.title = title
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.thumbnail_url = thumbnail_url
        self.duration = duration
        self.view_count = view_count
        self.published_time = published_time
        self.watched_time = watched_time
        self.item_type = item_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel_name": self.channel_name,
            "channel_id": self.channel_id,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "view_count": self.view_count,
            "published_time": self.published_time,
            "watched_time": self.watched_time,
            "type": self.item_type,
            "url": f"https://www.youtube.com/watch?v={self.video_id}"
        }

    def __repr__(self) -> str:
        return f"<HistoryItem {self.item_type}: {self.title[:50]}>"


class HistoryParser:
    """Parser for history API response."""

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> List[HistoryItem]:
        """
        Parse complete API response.

        Args:
            response: JSON response

        Returns:
            List of HistoryItem
        """
        items: List[HistoryItem] = []

        # Identify response type
        sections = []

        # First page (browseId)
        if "contents" in response:
            try:
                contents = response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]
                sections = contents["sectionListRenderer"]["contents"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Invalid response structure (first page): {e}")

        # Continuation pages
        elif "onResponseReceivedActions" in response:
            try:
                actions = response["onResponseReceivedActions"]
                for action in actions:
                    if "appendContinuationItemsAction" in action:
                        sections = action["appendContinuationItemsAction"]["continuationItems"]
                        break
            except (KeyError, IndexError) as e:
                raise ValueError(f"Invalid response structure (continuation): {e}")

        else:
            raise ValueError("Response without 'contents' or 'onResponseReceivedActions'")

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
                    parsed = HistoryParser._parse_item(item_data, watched_time)
                    if parsed:
                        items.append(parsed)

        return items

    @staticmethod
    def _extract_section_timestamp(header: Dict[str, Any]) -> Optional[str]:
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
    def _parse_item(item_data: Dict[str, Any], watched_time: Optional[str] = None) -> Optional[HistoryItem]:
        """
        Parse single history item.

        Args:
            item_data: Item data (can be various renderer types)
            watched_time: Section timestamp (when watched)

        Returns:
            HistoryItem or None if cannot parse
        """
        # Identify renderer type
        renderer_type = list(item_data.keys())[0] if item_data else None

        if not renderer_type:
            return None

        # Shorts (reelShelfRenderer)
        if renderer_type == "reelShelfRenderer":
            return HistoryParser._parse_reel_shelf(item_data[renderer_type], watched_time)

        # Regular videos (lockupViewModel)
        elif renderer_type == "lockupViewModel":
            return HistoryParser._parse_lockup_view_model(item_data[renderer_type], watched_time)

        # Old videos may use videoRenderer
        elif renderer_type == "videoRenderer":
            return HistoryParser._parse_video_renderer(item_data[renderer_type], watched_time)

        # Unsupported type
        return None

    @staticmethod
    def _parse_reel_shelf(data: Dict[str, Any], watched_time: Optional[str]) -> Optional[HistoryItem]:
        """Parse shorts (reelShelfRenderer)."""
        try:
            # reelShelfRenderer contains multiple shorts
            items = data.get("items", [])

            if not items:
                return None

            # For now, return only first short
            # TODO: Expand to return all
            first_reel = items[0]

            if "shortsLockupViewModel" in first_reel:
                short_data = first_reel["shortsLockupViewModel"]

                # Get video ID from reelWatchEndpoint (correct location)
                on_tap = short_data.get("onTap", {})
                innertube_cmd = on_tap.get("innertubeCommand", {})
                reel_endpoint = innertube_cmd.get("reelWatchEndpoint", {})
                video_id = reel_endpoint.get("videoId", "")

                # Title and view count from overlayMetadata
                overlay = short_data.get("overlayMetadata", {})
                title = overlay.get("primaryText", {}).get("content", "Untitled short")
                view_count = overlay.get("secondaryText", {}).get("content")

                # Thumbnail from reelWatchEndpoint
                thumbnail_data = reel_endpoint.get("thumbnail", {})
                thumbnails = thumbnail_data.get("thumbnails", [])
                thumbnail_url = thumbnails[0].get("url") if thumbnails else None

                return HistoryItem(
                    video_id=video_id,
                    title=title,
                    thumbnail_url=thumbnail_url,
                    view_count=view_count,
                    watched_time=watched_time,
                    item_type="short"
                )

        except (KeyError, IndexError):
            pass

        return None

    @staticmethod
    def _parse_lockup_view_model(data: Dict[str, Any], watched_time: Optional[str]) -> Optional[HistoryItem]:
        """Parse regular videos (lockupViewModel)."""
        try:
            # Video metadata
            metadata = data.get("metadata", {}).get("lockupMetadataViewModel", {})

            # Title
            title_data = metadata.get("title", {})
            title = title_data.get("content", "Untitled video")

            # Additional metadata (channel, views, time)
            metadata_parts = metadata.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", [])

            channel_name = None
            view_count = None
            published_time = None

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
                view_count=view_count,
                duration=duration,
                thumbnail_url=thumbnail,
                watched_time=watched_time,
                item_type="video"
            )

        except (KeyError, IndexError) as e:
            # Debug: log error but don't fail
            # print(f"Warning: Failed to parse lockupViewModel: {e}")
            pass

        return None

    @staticmethod
    def _parse_video_renderer(data: Dict[str, Any], watched_time: Optional[str]) -> Optional[HistoryItem]:
        """Parse old format (videoRenderer)."""
        try:
            video_id = data.get("videoId")
            if not video_id:
                return None

            # Title
            title_data = data.get("title", {})
            title = (
                title_data.get("simpleText") or
                (title_data.get("runs", [{}])[0].get("text") if title_data.get("runs") else "Untitled video")
            )

            # Channel
            owner_text = data.get("ownerText", {})
            channel_name = None
            channel_id = None

            if owner_text.get("runs"):
                channel_name = owner_text["runs"][0].get("text")
                browse_endpoint = owner_text["runs"][0].get("navigationEndpoint", {}).get("browseEndpoint", {})
                channel_id = browse_endpoint.get("browseId")

            # Thumbnail
            thumbnails = data.get("thumbnail", {}).get("thumbnails", [])
            thumbnail_url = thumbnails[-1]["url"] if thumbnails else None

            # Duration
            duration = data.get("lengthText", {}).get("simpleText")

            # Views
            view_count = data.get("shortViewCountText", {}).get("simpleText")

            # Published time
            published_time = data.get("publishedTimeText", {}).get("simpleText")

            return HistoryItem(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                channel_id=channel_id,
                thumbnail_url=thumbnail_url,
                duration=duration,
                view_count=view_count,
                published_time=published_time,
                watched_time=watched_time,
                item_type="video"
            )

        except (KeyError, IndexError):
            pass

        return None
