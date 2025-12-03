"""
Yefry Shephard de Jesus
22-SISN-2-020

Web scraping service for extracting content from news URLs.
"""

from urllib.parse import urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup

from src.config import get_settings
from src.models import NewsContent


class ScraperService:
    """Service for extracting content from news URLs."""

    # Known reliable news domains for credibility hints
    RELIABLE_DOMAINS = {
        "bbc.com",
        "bbc.co.uk",
        "reuters.com",
        "apnews.com",
        "nytimes.com",
        "washingtonpost.com",
        "theguardian.com",
        "npr.org",
        "pbs.org",
        "cnn.com",
        "nbcnews.com",
        "abcnews.go.com",
        "cbsnews.com",
        "factcheck.org",
        "snopes.com",
        "politifact.com",
        "un.org",
        "news.un.org",
    }

    # Known unreliable or satire domains
    UNRELIABLE_DOMAINS = {
        "theonion.com",
        "babylonbee.com",
        "clickhole.com",
    }

    def __init__(self, timeout: Optional[int] = None):
        """Initialize scraper with configuration."""
        settings = get_settings()
        self.timeout = timeout or settings.request_timeout
        self.max_content_length = settings.max_content_length
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5,es;q=0.3",
        }

    def extract_content(self, url: str) -> NewsContent:
        """
        Extract content from a news URL.

        Args:
            url: The URL to extract content from.

        Returns:
            NewsContent object with extracted data.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Try to detect encoding
            response.encoding = response.apparent_encoding or 'utf-8'

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove non-content elements
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside", "noscript", "iframe", "form"]
            ):
                element.decompose()

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_content(soup)

            # Extract domain
            domain = urlparse(url).netloc

            if not content or len(content.strip()) < 100:
                # Fallback: try to get all text from body
                content = self._fallback_extract(soup)
                
            if not content or len(content.strip()) < 50:
                return NewsContent.from_url_data(
                    url=url,
                    content="",
                    title=title,
                    domain=domain,
                    error="Could not extract sufficient content from URL",
                )

            return NewsContent.from_url_data(
                url=url,
                content=content[: self.max_content_length],
                title=title,
                domain=domain,
            )

            return NewsContent.from_url_data(
                url=url,
                content=content[: self.max_content_length],
                title=title,
                domain=domain,
            )

        except requests.exceptions.Timeout:
            return NewsContent.from_url_data(
                url=url, content="", error="Request timed out"
            )
        except requests.exceptions.RequestException as e:
            return NewsContent.from_url_data(
                url=url, content="", error=f"Error fetching URL: {str(e)}"
            )
        except Exception as e:
            return NewsContent.from_url_data(
                url=url, content="", error=f"Error extracting content: {str(e)}"
            )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the main title from the page."""
        # Try common title patterns
        selectors = [
            "h1.article-title",
            "h1.entry-title",
            "h1.post-title",
            "h1.headline",
            "h1[itemprop='headline']",
            "h1.story-body__h1",
            ".article-header h1",
            ".story-title",
            ".news-title",
            "article h1",
            "main h1",
            ".content h1",
            "h1",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10:
                    return title

        # Try og:title meta tag
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Fallback to page title
        if soup.title:
            return soup.title.get_text(strip=True)

        return ""

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the main article content."""
        # Try to find article body with many selectors
        article_selectors = [
            "article",
            ".article-body",
            ".article-content",
            ".article__body",
            ".story-body",
            ".story-body__inner",
            ".entry-content",
            ".post-content",
            ".news-body",
            ".content-body",
            "[itemprop='articleBody']",
            "[role='article']",
            ".field-name-body",
            ".text-long",
            ".body-content",
            "main article",
            "main .content",
            "main",
            "#content",
            ".content",
        ]

        article = None
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                # Check if it has meaningful content
                text = article.get_text(strip=True)
                if len(text) > 200:
                    break
                article = None

        # Extract paragraphs
        if article:
            paragraphs = article.find_all(["p", "div.paragraph", "span.text"])
        else:
            paragraphs = soup.find_all("p")

        # Filter and join content
        content_parts = []
        for p in paragraphs:
            text = p.get_text(separator=" ", strip=True)
            # Filter out short paragraphs (likely navigation/ads)
            if len(text) > 30:
                content_parts.append(text)

        return " ".join(content_parts)
    
    def _fallback_extract(self, soup: BeautifulSoup) -> str:
        """Fallback extraction method - get all text from body."""
        body = soup.find("body")
        if not body:
            return ""
        
        # Get all text with proper spacing
        text = body.get_text(separator=" ", strip=True)
        
        # Clean up excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def get_domain_credibility(self, domain: str) -> str:
        """
        Get a basic credibility assessment for a domain.

        Args:
            domain: The domain to assess.

        Returns:
            Credibility level: "high", "low", or "unknown"
        """
        # Clean domain
        clean_domain = domain.lower().replace("www.", "")

        if any(d in clean_domain for d in self.RELIABLE_DOMAINS):
            return "high"
        if any(d in clean_domain for d in self.UNRELIABLE_DOMAINS):
            return "low"
        return "unknown"

    def is_url(self, text: str) -> bool:
        """Check if the input text is a URL."""
        text = text.strip()
        return text.startswith("http://") or text.startswith("https://")

    def parse_input(self, entrada: str) -> NewsContent:
        """
        Parse user input and return appropriate NewsContent.

        Args:
            entrada: User input (URL or text).

        Returns:
            NewsContent object.
        """
        if self.is_url(entrada):
            return self.extract_content(entrada)
        return NewsContent.from_text(entrada)
