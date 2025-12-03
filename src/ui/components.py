"""
Yefry Shephard de Jesus
22-SISN-2-020

UI components for the Fake News Detector.
Contains reusable Gradio component builders.
"""

import gradio as gr


def create_header() -> gr.HTML:
    """Create the application header."""
    return gr.HTML(
        """
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                    padding: 24px; border-radius: 16px; text-align: center; margin-bottom: 16px; 
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">
            <h1 style="margin: 0; color: #ffffff; font-family: 'Segoe UI', Roboto, Arial; 
                       font-size: 2.2em; font-weight: 700; letter-spacing: -0.5px;">
                🔍 Detector de Fake News
            </h1>
            <p style="margin: 8px 0 0; color: rgba(255,255,255,0.85); font-size: 1.1em;">
                Análisis transparente con explicaciones y fuentes citadas
            </p>
        </div>
        """
    )


def create_analyzer_intro() -> gr.HTML:
    """Create intro box for analyzer tab."""
    return gr.HTML(
        '''
        <div style="background:#e3f2fd; padding:16px 20px; border-radius:10px; margin-bottom:14px; border-left:4px solid #1976d2;">
            <p style="margin:0; color:#000; font-size:15px;">
                <b style="color:#000;">🔎 Cómo usar:</b> Pega el texto de una noticia o su URL y pulsa <i style="color:#000;">Analizar noticia</i>. Obtendrás:
            </p>
            <ul style="margin:10px 0 0 0; padding-left:24px;">
                <li style="color:#000; font-size:14px; margin:4px 0;">Score de veracidad (0-100%)</li>
                <li style="color:#000; font-size:14px; margin:4px 0;">Señales de alerta detectadas</li>
                <li style="color:#000; font-size:14px; margin:4px 0;">Fuentes para verificar</li>
                <li style="color:#000; font-size:14px; margin:4px 0;">Recomendaciones accionables</li>
            </ul>
        </div>
        '''
    )


def create_info_sidebar() -> tuple[gr.Markdown, gr.Markdown]:
    """Create info sidebar content."""
    info_title = gr.Markdown("### ℹ️ Sobre esta herramienta")
    info_content = gr.Markdown(
        """
La herramienta evalúa múltiples factores para estimar la probabilidad de desinformación.

**Criterios evaluados:**
- Señales de lenguaje manipulador
- Presencia de fuentes verificables
- Uso de clickbait
- Credibilidad del medio
- Consistencia con otras fuentes

**Leyenda del semáforo:**
- 🟢 = Probablemente confiable (70-100%)
- 🟡 = Dudoso, verificar (40-69%)
- 🔴 = Probable desinformación (0-39%)

Usa las búsquedas sugeridas para verificar claims en fuentes reconocidas.
        """
    )
    return info_title, info_content


def create_history_header() -> gr.HTML:
    """Create header for history tab."""
    return gr.HTML(
        '''
        <div style="background:#fff9c4; padding:12px 16px; border-radius:10px; margin-bottom:12px; border-left:4px solid #ffc107;">
            <p style="margin:0; color:#000; font-size:15px;">
                <b style="color:#000;">📚 Historial:</b> Revisa tus últimos análisis aquí. Puedes exportar a CSV para respaldo.
            </p>
        </div>
        '''
    )


def create_about_content() -> gr.HTML:
    """Create about section content."""
    return gr.HTML(
        '''
        <div style="background:#fff; padding:24px; border-radius:12px; border:1px solid #ddd;">
            <h2 style="margin:0 0 16px 0; color:#000; font-size:1.5em;">
                🔎 Detector de Fake News — Explicaciones Transparentes
            </h2>
            <p style="margin:0 0 16px 0; color:#000; font-size:15px; line-height:1.6;">
                <b style="color:#000;">Problema:</b> Distinguir noticias reales de falsas es difícil para el público general. 
                Esta herramienta combina análisis de lenguaje y verificación web para ofrecer un 
                <b style="color:#000;">score de veracidad</b> (0-100%) y explica su razonamiento con fuentes citadas.
            </p>
            
            <div style="background:#f5f5f5; padding:16px; border-radius:8px; margin-bottom:16px;">
                <h3 style="margin:0 0 12px 0; color:#000; font-size:1.1em;">✨ Características principales:</h3>
                <ul style="margin:0; padding-left:24px;">
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Análisis de texto/URL:</b> Extrae y analiza contenido automáticamente</li>
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Búsqueda de origen:</b> Identifica de dónde viene la noticia</li>
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Múltiples fuentes:</b> Contrasta con fuentes confiables</li>
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Detección de manipulación:</b> Identifica clickbait y lenguaje emotivo</li>
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Explicación educativa:</b> Enseña cómo verificar información</li>
                    <li style="color:#000; font-size:14px; margin:6px 0;"><b style="color:#000;">Historial:</b> Guarda análisis previos con exportación CSV</li>
                </ul>
            </div>
        </div>
        '''
    )


def create_tips_section() -> gr.Markdown:
    """Create tips section for verification."""
    return gr.Markdown(
        """
## 💡 Consejos para Verificar Noticias

Para evaluar la veracidad de cualquier noticia, considera verificar los siguientes aspectos:

| Aspecto | Qué verificar |
|---------|---------------|
| **Fuente original** | ¿Quién publicó primero? ¿Tiene reputación? |
| **Fuentes citadas** | ¿Se citan fuentes primarias verificables? |
| **Múltiples medios** | ¿Otros medios confiables reportan lo mismo? |
| **Fecha** | ¿Es actual o está descontextualizada? |
| **Imágenes** | Usa búsqueda inversa para verificar origen |
| **Lenguaje** | ¿Usa titulares sensacionalistas? |

### 🌐 Sitios de Fact-Checking recomendados:
- [Snopes](https://www.snopes.com/)
- [FactCheck.org](https://www.factcheck.org/)
- [PolitiFact](https://www.politifact.com/)
- [AFP Factual](https://factual.afp.com/)
- [Maldita.es](https://maldita.es/) (Español)
        """
    )


def create_footer() -> gr.Markdown:
    """Create application footer."""
    return gr.Markdown(
        """
---
**Nota:** Esta herramienta es orientativa y educativa. Siempre verifica la información en múltiples fuentes confiables antes de compartirla.

*Desarrollado con ❤️ usando Gradio y OpenAI*
        """
    )


# Example data for quick testing
EXAMPLE_CHOICES = [
    "-- Seleccionar ejemplo --",
    "[Ejemplo] Vacunas causan autismo según estudio reciente",
    "[Ejemplo] Científicos descubren cura milagrosa contra el cáncer",
    "[Ejemplo] Político promete eliminar todos los impuestos si gana",
    "https://www.bbc.com/news/world (URL de ejemplo)",
    "https://www.reuters.com/world/ (URL de ejemplo)",
]


def get_example_text(selection: str) -> str:
    """Get example text based on selection."""
    examples = {
        "[Ejemplo] Vacunas causan autismo según estudio reciente": """URGENTE: Nuevo estudio DEMUESTRA que las vacunas causan autismo

Un grupo de científicos independientes ha publicado un estudio revolucionario que confirma lo que muchos padres sospechaban: existe una conexión directa entre las vacunas infantiles y el autismo.

El Dr. John Smith, líder del estudio, afirma: "Los datos son irrefutables. Hemos encontrado una correlación del 100% entre la vacunación y los casos de autismo."

Miles de padres están exigiendo respuestas a las autoridades sanitarias. ¡Comparte esta información antes de que la censuren!""",
        "[Ejemplo] Científicos descubren cura milagrosa contra el cáncer": """INCREÍBLE: Científicos descubren fruta amazónica que CURA el cáncer en 3 días

Investigadores brasileños han encontrado una fruta en lo profundo del Amazonas que elimina completamente las células cancerígenas.

"Big Pharma no quiere que sepas esto", declara el investigador principal. "Esta fruta podría acabar con su negocio de miles de millones."

El tratamiento consiste en tomar el jugo de esta fruta milagrosa tres veces al día. Los resultados son instantáneos y sin efectos secundarios.

¡Las farmacéuticas están intentando silenciar este descubrimiento!""",
        "[Ejemplo] Político promete eliminar todos los impuestos si gana": """EXCLUSIVA: Candidato promete eliminar TODOS los impuestos y duplicar salarios

En una entrevista exclusiva, el candidato presidencial Juan Pérez ha prometido que si gana las elecciones eliminará completamente todos los impuestos del país.

"No más IRPF, no más IVA, no más impuestos de ningún tipo", declaró. "Además, duplicaré el salario de todos los trabajadores en mi primer mes de gobierno."

Según sus cálculos, esto es perfectamente viable gracias a un "plan económico secreto" que revelará después de ganar.

Los economistas tradicionales están "celosos" de su genialidad, según afirmó.""",
    }
    return examples.get(selection, "")
