"""
Yefry Shephard de Jesus
22-SISN-2-020

Analysis service for veracity assessment using OpenAI.
Handles all LLM-based analysis including fact-checking and claim extraction.
"""

import json
import re
from typing import Optional

from openai import OpenAI

from ..config import Settings, get_settings
from ..models import NewsContent, SourceInfo


class AnalysisService:
    """Service for AI-powered news analysis."""

    # System prompt for the fact-checker persona
    SYSTEM_PROMPT = """Eres un verificador de hechos experto, objetivo y riguroso. 
Tu análisis debe ser claro, específico y educativo.
Siempre cita fuentes cuando sea posible y explica tu razonamiento."""

    # Analysis prompt template
    ANALYSIS_PROMPT = """Eres un experto verificador de hechos y detector de desinformación. Analiza la siguiente noticia con criterio profesional.

{title_section}
{domain_section}
{sources_section}

Contenido:
{content}

Proporciona un análisis estructurado en este formato EXACTO:

SCORE: [número del 0 al 100, donde 0 es completamente falso y 100 es completamente verificable]

VEREDICTO: [Una frase corta: "Probablemente falsa", "Dudosa", "Probablemente verdadera", "Verificada", etc.]

SEÑALES DE ALERTA:
[Lista las señales específicas de manipulación, clickbait, lenguaje emotivo, falta de fuentes, etc. Si no hay señales significativas, indica "No se detectan señales de alerta significativas"]

CLAIMS PRINCIPALES:
[Lista los 2-3 claims o afirmaciones principales que pueden verificarse]

ORIGEN Y FUENTES:
[Identifica el origen probable de la información. Si hay fuentes citadas, evalúa su credibilidad. Menciona si encontraste la misma información en otras fuentes.]

RECOMENDACIONES:
[Qué debería verificar el usuario y cómo hacerlo - sé específico con sitios de fact-checking]

ANÁLISIS DEL DOMINIO:
[Si conoces el dominio, comenta sobre su reputación. Si no, indica que debe investigarse]"""

    # Tool definition for web search
    SEARCH_TOOL = {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Realiza una búsqueda web para verificar información y encontrar fuentes",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Términos de búsqueda para verificar claims",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Número de resultados (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    }

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        settings: Optional[Settings] = None,
    ):
        """Initialize analysis service."""
        self.settings = settings or get_settings()
        self.client = client or self._create_client()
        self._last_search_results: str = ""

    def _create_client(self) -> OpenAI:
        """Create OpenAI client with configured API key."""
        if self.settings.openai_api_key:
            return OpenAI(api_key=self.settings.openai_api_key)
        return OpenAI()

    def update_client(self, api_key: Optional[str] = None):
        """Update the OpenAI client with a new API key."""
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.settings.openai_api_key = api_key
        else:
            self.client = OpenAI()

    def analyze_veracidad(
        self,
        content: NewsContent,
        search_callback=None,
        additional_sources: Optional[list[SourceInfo]] = None,
    ) -> str:
        """
        Perform veracity analysis on news content.

        Args:
            content: NewsContent object with the text to analyze.
            search_callback: Optional callback function for web searches.
            additional_sources: Pre-fetched sources to include in analysis.

        Returns:
            Full analysis text from the model.
        """
        # Build prompt sections
        title_section = f"Título: {content.title}" if content.title else ""
        domain_section = f"Dominio: {content.domain}" if content.domain else ""

        # Include any pre-fetched sources
        sources_section = ""
        if additional_sources:
            sources_text = "\n".join(
                [f"- {s.title}: {s.snippet} ({s.url})" for s in additional_sources[:5]]
            )
            sources_section = f"Fuentes encontradas previamente:\n{sources_text}"

        prompt = self.ANALYSIS_PROMPT.format(
            title_section=title_section,
            domain_section=domain_section,
            sources_section=sources_section,
            content=content.content[:2500],
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        model = self.settings.model

        try:
            if self.settings.use_search and search_callback:
                # Use tools for search capability
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=[self.SEARCH_TOOL],
                    tool_choice="auto",
                    temperature=0.4,
                )

                message = response.choices[0].message

                # Handle tool calls if the model wants to search
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        if tool_call.function.name == "search_web":
                            args = json.loads(tool_call.function.arguments)
                            query = args.get("query", "")
                            num_results = args.get("num_results", 5)

                            # Execute search via callback
                            search_result = search_callback(query, num_results)
                            self._last_search_results = search_result.raw_snippets

                            # Continue conversation with search results
                            messages.append(message)
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": search_result.raw_snippets
                                    or "No results found",
                                }
                            )

                    # Get final response with search context
                    final_response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.4,
                    )
                    return final_response.choices[0].message.content or ""

                return message.content or ""
            else:
                # Simple completion without tools
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.4,
                )
                return response.choices[0].message.content or ""

        except Exception as e:
            return f"Error en el análisis: {str(e)}"

    def generate_search_queries(
        self, claims: str, title: str, num_queries: int = 3
    ) -> list[str]:
        """
        Generate search queries to verify the main claims.

        Args:
            claims: Main claims extracted from the news.
            title: News title.
            num_queries: Number of queries to generate.

        Returns:
            List of search query strings.
        """
        prompt = f"""Basándote en esta noticia y sus claims principales, genera {num_queries} búsquedas específicas en Google que ayudarían a verificar la información.

Título: {title}
Claims: {claims}

IMPORTANTE: Las búsquedas deben:
1. Buscar el origen de la noticia
2. Verificar en múltiples fuentes confiables
3. Buscar fact-checks existentes

Formato: Devuelve solo las {num_queries} búsquedas, una por línea, sin numeración ni explicaciones adicionales."""

        try:
            response = self.client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            queries = response.choices[0].message.content.strip().split("\n")
            return [q.strip() for q in queries if q.strip()][:num_queries]
        except Exception:
            return ["Verificación de información no disponible"]

    def get_last_search_results(self) -> str:
        """Get the last search results used in analysis."""
        return self._last_search_results

    @staticmethod
    def extract_score(analysis_text: str) -> int:
        """
        Extract the numeric score from analysis text.

        Args:
            analysis_text: Full analysis text from model.

        Returns:
            Score between 0-100, defaults to 50 if not found.
        """
        match = re.search(r"SCORE:\s*(\d+)", analysis_text)
        if match:
            score = int(match.group(1))
            return max(0, min(100, score))  # Clamp to 0-100
        return 50

    @staticmethod
    def extract_claims(analysis_text: str) -> str:
        """
        Extract main claims section from analysis text.

        Args:
            analysis_text: Full analysis text.

        Returns:
            Claims text or default message.
        """
        match = re.search(
            r"CLAIMS PRINCIPALES:(.*?)(?=ORIGEN Y FUENTES:|RECOMENDACIONES:|ANÁLISIS DEL DOMINIO:|$)",
            analysis_text,
            re.DOTALL,
        )
        if match:
            return match.group(1).strip()
        return "No se pudieron extraer claims específicos"

    @staticmethod
    def extract_verdict(analysis_text: str) -> str:
        """Extract verdict from analysis text."""
        match = re.search(r"VEREDICTO:\s*(.+?)(?:\n|$)", analysis_text)
        if match:
            return match.group(1).strip()
        return "Sin veredicto"

    @staticmethod
    def extract_alert_signals(analysis_text: str) -> list[str]:
        """Extract alert signals as a list."""
        match = re.search(
            r"SEÑALES DE ALERTA:(.*?)(?=CLAIMS PRINCIPALES:|$)",
            analysis_text,
            re.DOTALL,
        )
        if match:
            signals_text = match.group(1).strip()
            signals = [
                s.strip().lstrip("-•") for s in signals_text.split("\n") if s.strip()
            ]
            return [s.strip() for s in signals if s.strip()]
        return []

    @staticmethod
    def extract_recommendations(analysis_text: str) -> list[str]:
        """Extract recommendations as a list."""
        match = re.search(
            r"RECOMENDACIONES:(.*?)(?=ANÁLISIS DEL DOMINIO:|$)",
            analysis_text,
            re.DOTALL,
        )
        if match:
            recs_text = match.group(1).strip()
            recs = [r.strip().lstrip("-•") for r in recs_text.split("\n") if r.strip()]
            return [r.strip() for r in recs if r.strip()]
        return []

    @staticmethod
    def determine_semaphore(score: int) -> tuple[str, str]:
        """
        Determine semaphore color and label based on score.

        Args:
            score: Veracity score (0-100).

        Returns:
            Tuple of (emoji, label).
        """
        if score >= 70:
            return "🟢", "VERDE - Probablemente Confiable"
        elif score >= 40:
            return "🟡", "AMARILLO - Dudoso / Verificar"
        else:
            return "🔴", "ROJO - Alta Probabilidad de Desinformación"
