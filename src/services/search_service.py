"""
Web search service for fact-checking and source verification.
Supports multiple search providers: SerpAPI, Bing, Google Custom Search.
"""

from abc import ABC, abstractmethod
from typing import Optional

import requests

from src.config import Settings, get_settings
from src.models import SearchResult, SourceInfo


class SearchProvider(ABC):
    """Abstract base class for search providers."""

    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> SearchResult:
        """Execute a search and return results."""
        pass


class SerpAPIProvider(SearchProvider):
    """SerpAPI search provider."""

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://serpapi.com/search.json"

    def search(self, query: str, num_results: int = 5) -> SearchResult:
        if not self.api_key:
            return SearchResult(query=query)

        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "engine": "google",
                    "api_key": self.api_key,
                    "num": num_results,
                },
                timeout=self.timeout,
            )
            data = response.json()

            sources = []
            snippets_text = []

            for result in data.get("organic_results", [])[:num_results]:
                title = result.get("title", "")
                snippet = result.get("snippet", "") or result.get(
                    "rich_snippet", {}
                ).get("top", {}).get("detected_extensions", "")
                link = result.get("link", "")

                sources.append(SourceInfo(title=title, url=link, snippet=snippet))
                snippets_text.append(f"{title}\n{snippet}\n{link}")

            return SearchResult(
                query=query,
                sources=sources,
                raw_snippets="\n\n".join(snippets_text),
            )

        except Exception:
            return SearchResult(query=query)


class BingProvider(SearchProvider):
    """Bing Search API provider."""

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"

    def search(self, query: str, num_results: int = 5) -> SearchResult:
        if not self.api_key:
            return SearchResult(query=query)

        try:
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            response = requests.get(
                self.base_url,
                params={"q": query, "count": num_results},
                headers=headers,
                timeout=self.timeout,
            )
            data = response.json()

            sources = []
            snippets_text = []

            for result in data.get("webPages", {}).get("value", [])[:num_results]:
                title = result.get("name", "")
                snippet = result.get("snippet", "")
                link = result.get("url", "")

                sources.append(SourceInfo(title=title, url=link, snippet=snippet))
                snippets_text.append(f"{title}\n{snippet}\n{link}")

            return SearchResult(
                query=query,
                sources=sources,
                raw_snippets="\n\n".join(snippets_text),
            )

        except Exception:
            return SearchResult(query=query)


class GoogleCSEProvider(SearchProvider):
    """Google Custom Search Engine provider."""

    def __init__(self, api_key: str, cx: str, timeout: int = 10):
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> SearchResult:
        if not self.api_key or not self.cx:
            return SearchResult(query=query)

        try:
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "key": self.api_key,
                    "cx": self.cx,
                    "num": num_results,
                },
                timeout=self.timeout,
            )
            data = response.json()

            sources = []
            snippets_text = []

            for result in data.get("items", [])[:num_results]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")

                sources.append(SourceInfo(title=title, url=link, snippet=snippet))
                snippets_text.append(f"{title}\n{snippet}\n{link}")

            return SearchResult(
                query=query,
                sources=sources,
                raw_snippets="\n\n".join(snippets_text),
            )

        except Exception:
            return SearchResult(query=query)


class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo search provider - FREE, no API key required."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.base_url = "https://html.duckduckgo.com/html/"

    def search(self, query: str, num_results: int = 5) -> SearchResult:
        try:
            from bs4 import BeautifulSoup
            import urllib.parse
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.post(
                self.base_url,
                data={"q": query, "b": ""},
                headers=headers,
                timeout=self.timeout,
            )
            
            sources = []
            snippets_text = []
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all result divs
            results = soup.find_all("div", class_="result")
            
            for result in results[:num_results]:
                # Extract title and URL
                title_link = result.find("a", class_="result__a")
                if not title_link:
                    continue
                    
                title = title_link.get_text(strip=True)
                href = title_link.get("href", "")
                
                # Extract actual URL from DuckDuckGo redirect
                if "uddg=" in href:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    href = urllib.parse.unquote(parsed.get("uddg", [href])[0])
                
                # Extract snippet
                snippet_elem = result.find("a", class_="result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                if title and href:
                    sources.append(SourceInfo(title=title, url=href, snippet=snippet))
                    snippets_text.append(f"{title}\n{snippet}\n{href}")

            return SearchResult(
                query=query,
                sources=sources,
                raw_snippets="\n\n".join(snippets_text),
            )

        except Exception as e:
            # Return empty result on error
            return SearchResult(query=query)


class SearchService:
    """
    Main search service that routes to appropriate provider.
    Factory pattern for provider selection.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize search service with settings."""
        self.settings = settings or get_settings()
        self._provider: Optional[SearchProvider] = None

    def _get_provider(self) -> SearchProvider:
        """Get or create the appropriate search provider."""
        provider_name = self.settings.search_provider

        if provider_name == "duckduckgo":
            return DuckDuckGoProvider(
                timeout=self.settings.request_timeout,
            )
        elif provider_name == "serpapi":
            return SerpAPIProvider(
                api_key=self.settings.serpapi_key,
                timeout=self.settings.request_timeout,
            )
        elif provider_name == "bing":
            return BingProvider(
                api_key=self.settings.bing_key,
                timeout=self.settings.request_timeout,
            )
        elif provider_name == "google":
            return GoogleCSEProvider(
                api_key=self.settings.google_api_key,
                cx=self.settings.google_cx,
                timeout=self.settings.request_timeout,
            )
        else:
            # Default to DuckDuckGo (free, no API key)
            return DuckDuckGoProvider(
                timeout=self.settings.request_timeout,
            )

    def search(self, query: str, num_results: Optional[int] = None) -> SearchResult:
        """
        Execute a web search using the configured provider.

        Args:
            query: Search query string.
            num_results: Number of results to return.

        Returns:
            SearchResult with sources found.
        """
        if not self.settings.use_search:
            return SearchResult(query=query)

        provider = self._get_provider()
        return provider.search(query, num_results or self.settings.search_results_count)

    def search_multiple_queries(
        self, queries: list[str], num_results: int = 3
    ) -> list[SearchResult]:
        """
        Execute multiple searches and combine results.

        Args:
            queries: List of search queries.
            num_results: Results per query.

        Returns:
            List of SearchResults.
        """
        results = []
        for query in queries:
            result = self.search(query, num_results)
            results.append(result)
        return results

    def get_all_sources(self, results: list[SearchResult]) -> list[SourceInfo]:
        """
        Extract all unique sources from multiple search results.

        Args:
            results: List of SearchResults.

        Returns:
            Deduplicated list of SourceInfo.
        """
        seen_urls = set()
        sources = []

        for result in results:
            for source in result.sources:
                if source.url and source.url not in seen_urls:
                    seen_urls.add(source.url)
                    sources.append(source)

        return sources

    def is_enabled(self) -> bool:
        """Check if search is enabled and configured."""
        if not self.settings.use_search:
            return False

        provider = self.settings.search_provider
        
        # DuckDuckGo doesn't need an API key - always available
        if provider == "duckduckgo":
            return True
        elif provider == "serpapi":
            return bool(self.settings.serpapi_key)
        elif provider == "bing":
            return bool(self.settings.bing_key)
        elif provider == "google":
            return bool(self.settings.google_api_key and self.settings.google_cx)

        return False

    @staticmethod
    def extract_links_from_snippets(snippets: str) -> list[str]:
        """
        Extract URLs from raw snippet text.

        Args:
            snippets: Raw snippets text with URLs.

        Returns:
            List of extracted URLs.
        """
        if not snippets:
            return []

        links = []
        blocks = [b.strip() for b in snippets.split("\n\n") if b.strip()]

        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            for line in reversed(lines):
                if line.startswith("http://") or line.startswith("https://"):
                    links.append(line)
                    break

        return links
