"""
Domain models for news analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SourceInfo:
    """Information about a source found during verification."""

    title: str
    url: str
    snippet: str
    domain: str = ""
    credibility: str = "unknown"  # high, medium, low, unknown

    def __post_init__(self):
        if not self.domain and self.url:
            from urllib.parse import urlparse

            self.domain = urlparse(self.url).netloc


@dataclass
class SearchResult:
    """Results from web search verification."""

    query: str
    sources: list[SourceInfo] = field(default_factory=list)
    raw_snippets: str = ""

    @property
    def source_count(self) -> int:
        return len(self.sources)

    def get_urls(self) -> list[str]:
        return [s.url for s in self.sources if s.url]


@dataclass
class NewsContent:
    """Extracted news content from URL or text input."""

    raw_input: str
    content: str
    title: str = ""
    domain: str = ""
    url: str = ""
    is_url: bool = False
    extraction_error: Optional[str] = None

    @classmethod
    def from_text(cls, text: str) -> "NewsContent":
        """Create NewsContent from plain text."""
        return cls(raw_input=text, content=text, is_url=False)

    @classmethod
    def from_url_data(
        cls,
        url: str,
        content: str,
        title: str = "",
        domain: str = "",
        error: Optional[str] = None,
    ) -> "NewsContent":
        """Create NewsContent from extracted URL data."""
        return cls(
            raw_input=url,
            content=content,
            title=title,
            domain=domain,
            url=url,
            is_url=True,
            extraction_error=error,
        )


@dataclass
class AnalysisResult:
    """Complete analysis result for a news item."""

    # Input information
    input_text: str
    title: str
    domain: str
    url: str

    # Analysis results
    score: int  # 0-100
    verdict: str
    semaphore: str  # 🟢, 🟡, 🔴
    semaphore_label: str

    # Detailed analysis
    full_analysis: str
    alert_signals: list[str] = field(default_factory=list)
    main_claims: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    domain_analysis: str = ""

    # Verification sources
    search_queries: list[str] = field(default_factory=list)
    sources_found: list[SourceInfo] = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    model_used: str = ""

    @property
    def is_reliable(self) -> bool:
        """Check if the news is considered reliable."""
        return self.score >= 70

    @property
    def is_suspicious(self) -> bool:
        """Check if the news is suspicious."""
        return 40 <= self.score < 70

    @property
    def is_likely_fake(self) -> bool:
        """Check if the news is likely fake."""
        return self.score < 40

    def get_summary_card(self) -> str:
        """Generate a summary card for UI display."""
        title_display = (
            f"**Title:** {self.title}"
            if self.title
            else "**Input:** Direct text provided"
        )
        sources_md = ""
        if self.sources_found:
            sources_md = "\n**Sources found:**\n\n"
            sources_md += "\n".join(
                [f"- [{s.title or s.domain}]({s.url})" for s in self.sources_found[:5]]
            )

        return f"""
### {self.semaphore} {self.semaphore_label}
**Score:** {self.score}/100
{title_display}
{f"**Domain:** {self.domain}" if self.domain else ""}
---
{sources_md}
"""

    def get_search_queries_md(self) -> str:
        """Get search queries as markdown list."""
        if not self.search_queries:
            return "No search queries generated."
        return "\n".join([f"- `{q}`" for q in self.search_queries])

    def to_history_row(self) -> list:
        """Convert to a row for history display."""
        return [
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            self.title or "Direct text",
            self.score,
            f"{self.semaphore} {self.semaphore_label}",
        ]
