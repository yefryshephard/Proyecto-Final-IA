"""
Yefry Shephard de Jesus
22-SISN-2-020
Application configuration management.
Supports environment variables and runtime updates.
"""

import os
from dataclasses import dataclass, field
from typing import Literal, Optional


SearchProvider = Literal["duckduckgo", "serpapi", "bing", "google"]


@dataclass
class Settings:
    """Application settings with sensible defaults."""

    # OpenAI Configuration
    openai_api_key: Optional[str] = field(default=None)
    model: str = field(default="gpt-4o")

    # Web Search Configuration
    use_search: bool = field(default=True)
    search_provider: SearchProvider = field(default="duckduckgo")
    serpapi_key: str = field(default="")
    bing_key: str = field(default="")
    google_api_key: str = field(default="")
    google_cx: str = field(default="")

    # Database Configuration
    db_path: str = field(default="")

    # Request Configuration
    request_timeout: int = field(default=15)
    max_content_length: int = field(default=3000)
    search_results_count: int = field(default=5)

    def __post_init__(self):
        """Load environment variables after initialization."""
        self._load_from_env()

    def _load_from_env(self):
        """Load settings from environment variables."""
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.serpapi_key:
            self.serpapi_key = os.getenv("SERPAPI_KEY", "")

        if not self.bing_key:
            self.bing_key = os.getenv("BING_KEY", "")

        if not self.google_api_key:
            self.google_api_key = os.getenv("GOOGLE_API_KEY", "")

        if not self.google_cx:
            self.google_cx = os.getenv("GOOGLE_CX", "")

        if not self.db_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.db_path = os.path.join(base_dir, "history.db")

    def update(self, **kwargs) -> "Settings":
        """Update settings with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        return self

    def validate_search_config(self) -> list[str]:
        """Validate search configuration and return warnings."""
        warnings = []
        if not self.use_search:
            return warnings

        # DuckDuckGo doesn't need an API key
        if self.search_provider == "duckduckgo":
            return warnings
        elif self.search_provider == "serpapi" and not self.serpapi_key:
            warnings.append(
                "SerpAPI key not provided — searches will not work with SerpAPI."
            )
        elif self.search_provider == "bing" and not self.bing_key:
            warnings.append("Bing key not provided — searches will not work with Bing.")
        elif self.search_provider == "google" and (
            not self.google_api_key or not self.google_cx
        ):
            warnings.append(
                "Google API key or CX missing — searches will not work with Google CSE."
            )

        return warnings


# Global settings instance (singleton pattern)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings():
    """Reset global settings (useful for testing)."""
    global _settings
    _settings = None
