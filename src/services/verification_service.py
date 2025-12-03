"""
Verification service that orchestrates the complete fact-checking workflow.
Combines scraping, searching, and AI analysis into a cohesive verification process.
"""

from datetime import datetime
from typing import Optional

from src.config import Settings, get_settings
from src.models import AnalysisResult, NewsContent, SourceInfo
from src.repositories import HistoryRepository
from .scraper_service import ScraperService
from .search_service import SearchService
from .analysis_service import AnalysisService


class VerificationService:
    """
    Main verification service that orchestrates the complete fact-checking workflow.
    This is the primary entry point for news verification.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        scraper: Optional[ScraperService] = None,
        search: Optional[SearchService] = None,
        analysis: Optional[AnalysisService] = None,
        history: Optional[HistoryRepository] = None,
    ):
        """Initialize verification service with dependencies."""
        self.settings = settings or get_settings()
        self.scraper = scraper or ScraperService()
        self.search = search or SearchService(self.settings)
        self.analysis = analysis or AnalysisService(settings=self.settings)
        self.history = history or HistoryRepository()

    def verify(self, entrada: str) -> AnalysisResult:
        """
        Perform complete verification of a news item.

        This is the main entry point that:
        1. Parses input (URL or text)
        2. Extracts content if URL
        3. Performs initial web searches for verification
        4. Runs AI analysis with search capability
        5. Generates verification queries
        6. Saves to history
        7. Returns complete analysis result

        Args:
            entrada: User input - can be URL or plain text.

        Returns:
            AnalysisResult with complete verification data.
        """
        timestamp = datetime.now()

        # Step 1: Parse input and extract content
        content = self.scraper.parse_input(entrada)

        if content.extraction_error and content.is_url:
            return self._create_error_result(
                entrada, content.extraction_error, timestamp
            )

        if not content.content:
            return self._create_error_result(
                entrada, "No se pudo extraer contenido suficiente", timestamp
            )

        # Step 2: Pre-fetch sources if search is enabled
        pre_search_sources: list[SourceInfo] = []
        if self.search.is_enabled():
            # Search for the news title/content to find origin and other sources
            query = content.title if content.title else content.content[:200]
            initial_search = self.search.search(f"{query} verificación fuentes")
            pre_search_sources = initial_search.sources

        # Step 3: Run AI analysis with search callback
        def search_callback(query: str, num_results: int):
            return self.search.search(query, num_results)

        full_analysis = self.analysis.analyze_veracidad(
            content=content,
            search_callback=search_callback if self.search.is_enabled() else None,
            additional_sources=pre_search_sources,
        )

        # Step 4: Extract structured data from analysis
        score = self.analysis.extract_score(full_analysis)
        verdict = self.analysis.extract_verdict(full_analysis)
        semaphore, semaphore_label = self.analysis.determine_semaphore(score)
        claims = self.analysis.extract_claims(full_analysis)
        alert_signals = self.analysis.extract_alert_signals(full_analysis)
        recommendations = self.analysis.extract_recommendations(full_analysis)

        # Step 5: Generate additional verification queries
        search_queries = self.analysis.generate_search_queries(
            claims=claims,
            title=content.title or content.content[:200],
            num_queries=3,
        )

        # Step 6: Collect all sources found
        all_sources = pre_search_sources.copy()

        # Add sources from any searches during analysis
        last_search_snippets = self.analysis.get_last_search_results()
        if last_search_snippets:
            additional_urls = SearchService.extract_links_from_snippets(
                last_search_snippets
            )
            for url in additional_urls:
                if not any(s.url == url for s in all_sources):
                    all_sources.append(SourceInfo(title="", url=url, snippet=""))

        # Step 7: Create result object
        result = AnalysisResult(
            input_text=entrada[:100] + "..." if len(entrada) > 100 else entrada,
            title=content.title or "Texto directo",
            domain=content.domain,
            url=content.url,
            score=score,
            verdict=verdict,
            semaphore=semaphore,
            semaphore_label=semaphore_label,
            full_analysis=full_analysis,
            alert_signals=alert_signals,
            main_claims=[c.strip() for c in claims.split("\n") if c.strip()],
            recommendations=recommendations,
            search_queries=search_queries,
            sources_found=all_sources,
            timestamp=timestamp,
            model_used=self.settings.model,
        )

        # Step 8: Save to history
        self._save_to_history(result)

        return result

    def _create_error_result(
        self, entrada: str, error: str, timestamp: datetime
    ) -> AnalysisResult:
        """Create an error result when verification fails."""
        return AnalysisResult(
            input_text=entrada[:100] + "..." if len(entrada) > 100 else entrada,
            title="Error",
            domain="",
            url="",
            score=0,
            verdict=f"Error: {error}",
            semaphore="❌",
            semaphore_label="Error",
            full_analysis=error,
            timestamp=timestamp,
            model_used=self.settings.model,
        )

    def _save_to_history(self, result: AnalysisResult):
        """Save analysis result to history database."""
        try:
            sources_json = ",".join([s.url for s in result.sources_found[:10]])
            self.history.save(
                timestamp=result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                entrada=result.input_text,
                titulo=result.title,
                score=result.score,
                semaforo=f"{result.semaphore} {result.semaphore_label}",
                full_analysis=result.full_analysis,
                sources=sources_json,
                url=result.url,
                domain=result.domain,
            )
        except Exception:
            # Don't fail verification if history save fails
            pass

    def get_history(self, limit: int = 10) -> list[list]:
        """Get recent analysis history."""
        return self.history.get_recent(limit)

    def clear_history(self) -> int:
        """Clear all analysis history."""
        return self.history.clear_all()

    def export_history(self) -> list[list]:
        """Export full history for CSV."""
        return self.history.export_to_rows()

    def get_statistics(self) -> dict:
        """Get analysis statistics."""
        return self.history.get_statistics()

    def update_settings(
        self,
        openai_key: Optional[str] = None,
        model: Optional[str] = None,
        use_search: Optional[bool] = None,
        search_provider: Optional[str] = None,
        serpapi_key: Optional[str] = None,
        bing_key: Optional[str] = None,
        google_key: Optional[str] = None,
        google_cx: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Update service settings.

        Returns:
            Tuple of (success, message).
        """
        try:
            # Update settings
            if model:
                self.settings.model = model
            if use_search is not None:
                self.settings.use_search = use_search
            if search_provider:
                # Ensure self.settings is a Settings instance before assigning
                if not isinstance(self.settings, Settings):
                    self.settings = get_settings()
                # Validate provided search_provider against allowed options
                allowed_providers = ("duckduckgo", "serpapi", "bing", "google")
                if search_provider not in allowed_providers:
                    return False, f"Proveedor de búsqueda no válido: {search_provider}"
                # Type-checker aware assignment
                from typing import Literal, cast

                self.settings.search_provider = cast(
                    Literal["duckduckgo", "serpapi", "bing", "google"], search_provider
                )
            if serpapi_key is not None:
                self.settings.serpapi_key = serpapi_key
            if bing_key is not None:
                self.settings.bing_key = bing_key
            if google_key is not None:
                self.settings.google_api_key = google_key
            if google_cx is not None:
                self.settings.google_cx = google_cx

            # Update OpenAI client if key provided
            if openai_key:
                self.analysis.update_client(openai_key)
                self.settings.openai_api_key = openai_key

            # Validate search config
            warnings = self.settings.validate_search_config()
            if warnings:
                return (
                    True,
                    f"Configuración guardada con advertencias: {' | '.join(warnings)}",
                )

            return (
                True,
                f"Configuración guardada — modelo: {self.settings.model}, búsqueda: {self.settings.use_search}",
            )

        except Exception as e:
            return False, f"Error al guardar configuración: {str(e)}"
