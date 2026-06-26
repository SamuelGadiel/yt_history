"""Custom exceptions for the application."""


class YouTubeHistoryError(Exception):
    """Base exception for all application errors."""
    pass


class AuthenticationError(YouTubeHistoryError):
    """Raised when authentication fails."""
    pass


class APIError(YouTubeHistoryError):
    """Raised when YouTube API request fails."""
    pass


class ParseError(YouTubeHistoryError):
    """Raised when parsing response fails."""
    pass


class ConfigError(YouTubeHistoryError):
    """Raised when configuration is invalid or missing."""
    pass


class CookieExtractionError(AuthenticationError):
    """Raised when cookie extraction from browser fails."""
    pass
