"""YouTube History Fetcher - Core modules."""

from .auth import (
    detect_available_browsers,
    extract_from_first_available,
    get_live_cookies,
    load_cookies,
    load_cookies_from_file,
    save_cookies_to_file,
    test_authentication,
)
from .config import AppConfig, load_env_config
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigError,
    CookieExtractionError,
    ParseError,
    YouTubeHistoryError,
)
from .history_fetcher import HistoryFetcher
from .history_parser import HistoryItem, HistoryParser
from .models import HistoryGroup
from .youtube_client import YouTubeClient

__all__ = [
    "APIError",
    "AppConfig",
    "AuthenticationError",
    "ConfigError",
    "CookieExtractionError",
    "HistoryFetcher",
    "HistoryGroup",
    "HistoryItem",
    "HistoryParser",
    "ParseError",
    "YouTubeClient",
    "YouTubeHistoryError",
    "detect_available_browsers",
    "extract_from_first_available",
    "get_live_cookies",
    "load_cookies",
    "load_cookies_from_file",
    "load_env_config",
    "save_cookies_to_file",
    "test_authentication",
]

__version__ = "1.0.0"
