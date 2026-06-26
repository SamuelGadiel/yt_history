"""Custom exceptions for the application."""


class YouTubeHistoryError(Exception):
    """Base exception for all application errors.

    All custom exceptions in this application inherit from this class.
    """

    pass


class AuthenticationError(YouTubeHistoryError):
    """Raised when authentication with YouTube fails.

    Common causes:
        - Invalid or expired cookies
        - Missing SAPISID cookie
        - Browser not logged in to YouTube
        - Saved cookies older than 3-5 days
    """

    pass


class APIError(YouTubeHistoryError):
    """Raised when YouTube API request fails.

    Causes:
        - Network connectivity issues
        - HTTP errors (non-200 status codes)
        - Invalid JSON response from API
        - API endpoint changes
    """

    pass


class ParseError(YouTubeHistoryError):
    """Raised when parsing YouTube API response fails.

    Causes:
        - Unexpected response structure from API
        - Missing required fields in JSON
        - YouTube changed internal API format
    """

    pass


class ConfigError(YouTubeHistoryError):
    """Raised when configuration is invalid or missing.

    Causes:
        - Missing .env file
        - YOUTUBE_API_KEY not set or invalid
        - Malformed configuration values
    """

    pass


class CookieExtractionError(AuthenticationError):
    """Raised when cookie extraction from browser fails.

    Causes:
        - No supported browser installed
        - Browser not logged in to YouTube
        - Chrome 127+ blocking cookie access
        - Keychain access denied (macOS)
        - browser-cookie3 library not installed
    """

    pass
