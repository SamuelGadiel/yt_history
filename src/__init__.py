"""YouTube History Fetcher - Core modules."""

from .youtube_client import YouTubeClient
from .history_parser import HistoryParser, HistoryItem
from .history_fetcher import HistoryFetcher
from .models import HistoryGroup
from .auth import load_cookies, load_cookies_from_file, get_live_cookies
from .config import AppConfig, load_env_config
from .exceptions import (
    YouTubeHistoryError,
    AuthenticationError,
    APIError,
    ParseError,
    ConfigError,
    CookieExtractionError
)

__all__ = [
    # Core classes
    'YouTubeClient',
    'HistoryParser',
    'HistoryFetcher',
    'HistoryItem',
    'HistoryGroup',
    # Auth
    'load_cookies',
    'load_cookies_from_file',
    'get_live_cookies',
    # Config
    'AppConfig',
    'load_env_config',
    # Exceptions
    'YouTubeHistoryError',
    'AuthenticationError',
    'APIError',
    'ParseError',
    'ConfigError',
    'CookieExtractionError',
]

__version__ = '1.0.0'
