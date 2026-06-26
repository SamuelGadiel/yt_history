"""Configuration management."""

import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from .exceptions import ConfigError


@dataclass
class AppConfig:
    """Application configuration."""
    api_key: str
    language: Optional[str] = None
    region: Optional[str] = None


def load_env_config(env_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from .env file.

    Args:
        env_path: Path to .env file (default: project root/.env)

    Returns:
        AppConfig instance

    Raises:
        ConfigError: If .env not found or API key not configured
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        raise ConfigError(
            f".env not found at {env_path}\n"
            f"Copy .env.example to .env and configure YOUTUBE_API_KEY"
        )

    # Try python-dotenv first (best practice)
    try:
        from dotenv import dotenv_values
        config_dict = dotenv_values(env_path)
    except ImportError:
        # Fallback to manual parsing if python-dotenv not installed
        config_dict = _parse_env_file(env_path)

    api_key = config_dict.get('YOUTUBE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        raise ConfigError(
            "YOUTUBE_API_KEY not configured in .env\n"
            "Set it to a valid YouTube API key (see README for instructions)"
        )

    language = config_dict.get('YOUTUBE_LANGUAGE') or None
    region = config_dict.get('YOUTUBE_REGION') or None

    return AppConfig(
        api_key=api_key,
        language=language,
        region=region
    )


def _parse_env_file(env_path: Path) -> Dict[str, str]:
    """
    Manual .env parser (fallback when python-dotenv not available).

    Handles:
    - Comments (# prefix)
    - Empty lines
    - Quoted values ("value" or 'value')
    - Inline comments (key=value # comment)
    - Whitespace trimming

    Args:
        env_path: Path to .env file

    Returns:
        Dict of env variables
    """
    config = {}

    with open(env_path) as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Skip malformed lines
            if '=' not in line:
                continue

            # Split key=value (only first =)
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()

            # Remove inline comments (but preserve # in quoted strings)
            if '#' in value and not _is_quoted(value):
                value = value.split('#')[0].strip()

            # Remove quotes if present
            if _is_quoted(value):
                value = value[1:-1]

            # Only store non-empty values
            if value:
                config[key] = value

    return config


def _is_quoted(value: str) -> bool:
    """Check if value is properly quoted."""
    return (
        (value.startswith('"') and value.endswith('"')) or
        (value.startswith("'") and value.endswith("'"))
    ) and len(value) >= 2


__all__ = ['AppConfig', 'load_env_config']
