# Fake News Detector Source Package
"""
Modular architecture following SOLID principles:

- config/: Configuration management (Settings)
- models/: Domain models (AnalysisResult, NewsContent, etc.)
- repositories/: Data persistence (HistoryRepository)
- services/: Business logic (ScraperService, SearchService, AnalysisService, VerificationService)
- ui/: Gradio UI components and application builder
"""

from src.config import Settings, get_settings
from src.models import AnalysisResult, NewsContent, SearchResult, SourceInfo
from src.repositories import HistoryRepository
from src.services import (
    AnalysisService,
    ScraperService,
    SearchService,
    VerificationService,
)
from src.ui import create_app

__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Models
    "AnalysisResult",
    "NewsContent",
    "SearchResult",
    "SourceInfo",
    # Repositories
    "HistoryRepository",
    # Services
    "AnalysisService",
    "ScraperService",
    "SearchService",
    "VerificationService",
    # UI
    "create_app",
]

__version__ = "1.0.0"
