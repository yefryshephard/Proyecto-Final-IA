"""
Yefry Shephard de Jesus
22-SISN-2-020

Main Gradio application builder.
Creates and configures the complete UI.
"""

import csv
import os
import tempfile
from typing import Optional

import gradio as gr

from src.config import Settings, get_settings
from src.services import VerificationService
from .components import (
    EXAMPLE_CHOICES,
    create_about_content,
    create_analyzer_intro,
    create_footer,
    create_header,
    create_history_header,
    create_info_sidebar,
    create_tips_section,
    get_example_text,
)


def create_app(settings: Optional[Settings] = None) -> gr.Blocks:
    """
    Create and configure the Gradio application.

    Args:
        settings: Optional settings instance. If None, uses global settings.

    Returns:
        Configured Gradio Blocks application.
    """
    settings = settings or get_settings()
    service = VerificationService(settings=settings)

    with gr.Blocks(
        title="Detector de Fake News",
    ) as demo:
        # Inject styles via an HTML <style> block for compatibility with older Gradio
        # Minimal global styles: only center the container and style result card
        gr.HTML(
            """
            <style>
            /* Center the app and limit max width for readability */
            .gradio-container { max-width: 1200px !important; margin: 24px auto !important; }

            /* Result card minimal styling (leave component inline styles intact) */
            .result-card { border-radius: 12px; padding: 16px; }
            </style>
            """
        )
        # Header
        create_header()

        with gr.Tabs() as tabs:
            # ============ ANALYZER TAB ============
            with gr.Tab("📝 Analizar", id="analyzer"):
                create_analyzer_intro()

                with gr.Row():
                    # Main input column
                    with gr.Column(scale=2):
                        entrada = gr.Textbox(
                            label="🔎 Texto de la Noticia o URL",
                            placeholder="Pega aquí el contenido de la noticia o la URL completa (https://...)",
                            lines=8,
                            max_lines=15,
                        )

                        with gr.Row():
                            examples_dropdown = gr.Dropdown(
                                choices=EXAMPLE_CHOICES,
                                label="📋 Cargar ejemplo",
                                value=EXAMPLE_CHOICES[0],
                                scale=3,
                            )
                            load_btn = gr.Button(
                                "📥 Cargar", variant="secondary", scale=1
                            )

                        analyze_btn = gr.Button(
                            "🔎 Analizar noticia",
                            variant="primary",
                            size="lg",
                        )

                        # Score and semaphore display
                        with gr.Row():
                            score_display = gr.Textbox(
                                label="📊 Score de Veracidad",
                                interactive=False,
                                scale=1,
                            )
                            semaphore_display = gr.Textbox(
                                label="🚦 Evaluación",
                                interactive=False,
                                scale=2,
                                visible=False,
                            )

                    # Info sidebar
                    with gr.Column(scale=1):
                        info_title, info_content = create_info_sidebar()

                gr.Markdown("---")

                # Results section
                with gr.Row():
                    with gr.Column(scale=1):
                        result_card = gr.Markdown(
                            label="Resultado",
                            elem_classes=["result-card"],
                        )

                    with gr.Column(scale=1):
                        with gr.Accordion("📋 Análisis completo", open=False):
                            full_analysis_md = gr.Markdown()

                        with gr.Accordion("🔎 Búsquedas sugeridas", open=False):
                            search_queries_md = gr.Markdown()

                        with gr.Accordion("🌐 Fuentes encontradas", open=False):
                            sources_md = gr.Markdown()

                # Tips section
                with gr.Accordion("💡 Consejos para verificar noticias", open=False):
                    create_tips_section()

            # ============ HISTORY TAB ============
            with gr.Tab("📜 Historial", id="history"):
                create_history_header()

                with gr.Row():
                    with gr.Column():
                        history_df = gr.Dataframe(
                            value=service.get_history(),
                            headers=["Fecha", "Título", "Score", "Semáforo"],
                            interactive=False,
                            wrap=True,
                        )

                        with gr.Row():
                            refresh_btn = gr.Button(
                                "🔄 Actualizar", variant="secondary"
                            )
                            clear_btn = gr.Button(
                                "🧹 Limpiar historial", variant="secondary"
                            )
                            export_btn = gr.Button(
                                "📥 Exportar CSV", variant="secondary"
                            )

                        export_file = gr.File(
                            label="Archivo exportado",
                            visible=False,
                        )

                # Statistics
                with gr.Accordion("📊 Estadísticas", open=False):
                    stats_md = gr.Markdown()

            # ============ ABOUT TAB ============
            with gr.Tab("ℹ️ Acerca", id="about"):
                create_about_content()

                gr.Markdown(
                    """
### 🎯 Por qué es útil:
- **Educación:** Aprende a identificar señales de desinformación
- **Verificación rápida:** Analiza noticias en segundos antes de compartir
- **Fuentes confiables:** Te conecta con fact-checkers reconocidos
- **Transparencia:** Explica el razonamiento detrás de cada evaluación

### 🔧 Tecnología:
- **OpenAI GPT:** Análisis de lenguaje y detección de patrones manipuladores
- **Web Scraping:** Extracción automática de contenido desde URLs
- **Búsqueda Web:** Verificación cruzada con múltiples fuentes (SerpAPI, Bing, Google, DuckDuckGo)
- **SQLite:** Almacenamiento local del historial de análisis
- **Gradio:** Interfaz web interactiva y accesible
                    """
                )

            # ============ SETTINGS TAB ============
            with gr.Tab("⚙️ Configuración", id="settings"):
                gr.Markdown("### ⚙️ Ajustes y API keys")

                with gr.Row():
                    with gr.Column():
                        openai_key_input = gr.Textbox(
                            label="OpenAI API Key",
                            placeholder="sk-...",
                            type="password",
                        )
                        model_select = gr.Dropdown(
                            choices=[
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-4-turbo",
                                "gpt-3.5-turbo",
                            ],
                            value=settings.model,
                            label="Modelo a usar",
                        )

                    with gr.Column():
                        use_search_cb = gr.Checkbox(
                            label="Habilitar búsqueda web para verificación",
                            value=settings.use_search,
                        )
                        provider_select = gr.Dropdown(
                            choices=["duckduckgo", "serpapi", "bing", "google"],
                            value=settings.search_provider,
                            label="Proveedor de búsqueda",
                            info="DuckDuckGo no requiere API key",
                        )

                gr.Markdown("### 🔑 API Keys de búsqueda (opcional)")

                with gr.Row():
                    serpapi_input = gr.Textbox(
                        label="SerpAPI Key",
                        placeholder="SERPAPI_KEY...",
                        type="password",
                    )
                    bing_input = gr.Textbox(
                        label="Bing (Azure) Key",
                        placeholder="BING_KEY...",
                        type="password",
                    )

                with gr.Row():
                    google_key_input = gr.Textbox(
                        label="Google API Key",
                        placeholder="GOOGLE_KEY...",
                        type="password",
                    )
                    google_cx_input = gr.Textbox(
                        label="Google CX / Search Engine ID",
                        placeholder="GOOGLE_CX...",
                    )

                save_config_btn = gr.Button(
                    "💾 Guardar configuración", variant="primary"
                )
                config_status = gr.Textbox(
                    label="Estado",
                    interactive=False,
                )

        # Footer
        create_footer()

        # ============ EVENT HANDLERS ============

        def load_example(selection: str) -> str:
            """Load example text into input."""
            if selection == EXAMPLE_CHOICES[0]:
                return ""
            if selection.startswith("https://"):
                return selection.split(" ")[0]
            return get_example_text(selection)

        def process_news(text: str):
            """Process news and return all UI updates."""
            if not text or not text.strip():
                return (
                    "⚠️ Por favor ingresa texto o una URL para analizar.",
                    [],
                    "",
                    gr.update(visible=False),
                    "",
                    "",
                    "",
                )

            result = service.verify(text)

            # Check for error
            if result.semaphore == "❌":
                return (
                    f"❌ **Error:** {result.verdict}",
                    service.get_history(),
                    f"Score: {result.score}/100",
                    gr.update(visible=False),
                    result.full_analysis,
                    "",
                    "",
                )

            # Format sources
            sources_formatted = ""
            if result.sources_found:
                sources_formatted = "### Fuentes encontradas:\n\n"
                for i, source in enumerate(result.sources_found[:8], 1):
                    title = source.title or source.domain or f"Fuente {i}"
                    sources_formatted += f"**{i}. [{title}]({source.url})**\n"
                    if source.snippet:
                        sources_formatted += f"> {source.snippet[:150]}...\n\n"
                    else:
                        sources_formatted += "\n"

            return (
                result.get_summary_card(),
                service.get_history(),
                f"Score: {result.score}/100",
                gr.update(
                    visible=True, value=f"{result.semaphore} {result.semaphore_label}"
                ),
                result.full_analysis,
                result.get_search_queries_md(),
                sources_formatted,
            )

        def refresh_history():
            """Refresh history dataframe."""
            return service.get_history()

        def clear_history():
            """Clear all history."""
            service.clear_history()
            return []

        def export_history():
            """Export history to CSV file."""
            rows = service.export_history()
            fd, path = tempfile.mkstemp(prefix="historial_fakenews_", suffix=".csv")
            os.close(fd)

            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Título", "Score", "Semáforo"])
                for row in rows:
                    writer.writerow(row)

            return gr.update(value=path, visible=True)

        def get_stats():
            """Get statistics markdown."""
            stats = service.get_statistics()
            if not stats or stats.get("total", 0) == 0:
                return "No hay análisis registrados aún."

            return f"""
### 📈 Estadísticas de análisis

| Métrica | Valor |
|---------|-------|
| Total de análisis | {stats["total"]} |
| Score promedio | {stats["avg_score"]}% |
| Score mínimo | {stats["min_score"]}% |
| Score máximo | {stats["max_score"]}% |
| 🟢 Confiables | {stats["reliable_count"]} |
| 🟡 Dudosos | {stats["suspicious_count"]} |
| 🔴 Probable desinformación | {stats["fake_count"]} |
            """

        def save_settings(
            openai_key,
            model,
            use_search,
            provider,
            serpapi,
            bing,
            google_key,
            google_cx,
        ):
            """Save configuration settings."""
            success, message = service.update_settings(
                openai_key=openai_key or None,
                model=model,
                use_search=use_search,
                search_provider=provider,
                serpapi_key=serpapi or None,
                bing_key=bing or None,
                google_key=google_key or None,
                google_cx=google_cx or None,
            )
            return message

        # Connect events
        load_btn.click(fn=load_example, inputs=[examples_dropdown], outputs=[entrada])

        analyze_btn.click(
            fn=process_news,
            inputs=[entrada],
            outputs=[
                result_card,
                history_df,
                score_display,
                semaphore_display,
                full_analysis_md,
                search_queries_md,
                sources_md,
            ],
        )

        refresh_btn.click(fn=refresh_history, outputs=[history_df])
        clear_btn.click(fn=clear_history, outputs=[history_df])
        export_btn.click(fn=export_history, outputs=[export_file])

        # Update stats when history tab is selected
        tabs.select(
            fn=lambda: get_stats(),
            outputs=[stats_md],
        )

        save_config_btn.click(
            fn=save_settings,
            inputs=[
                openai_key_input,
                model_select,
                use_search_cb,
                provider_select,
                serpapi_input,
                bing_input,
                google_key_input,
                google_cx_input,
            ],
            outputs=[config_status],
        )

    return demo


def launch_app(
    settings: Optional[Settings] = None,
    share: bool = False,
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
):
    """
    Create and launch the application.

    Args:
        settings: Optional settings instance.
        share: Whether to create a public share link.
        server_name: Server host address.
        server_port: Server port number.
    """
    demo = create_app(settings)
    demo.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
    )
