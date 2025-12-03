# 🔍 Detector de Fake News

<p align="center">
  <strong>Análisis transparente de noticias con explicaciones y fuentes citadas</strong>
</p>

---

## 📋 Descripción

Herramienta inteligente para detectar desinformación que:

- ✅ Analiza texto o URL de noticias
- ✅ Genera un **score de veracidad** (0-100%)
- ✅ Explica su razonamiento con fuentes citadas
- ✅ Detecta lenguaje manipulador y clickbait
- ✅ Busca el **origen** de la noticia en múltiples fuentes
- ✅ Interfaz tipo **semáforo** (🟢 verde / 🟡 amarillo / 🔴 rojo)
- ✅ Historial de análisis con exportación CSV

## 🚀 Instalación

### Requisitos

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recomendado) o pip

### Con uv (recomendado)

```bash
# Clonar repositorio
cd Fake_News_Detector

# Instalar dependencias
uv sync

# Configurar API key (opcional - también se puede configurar desde la UI)
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY
```

### Con pip

```bash
pip install -r requirements.txt
```

## 🎮 Uso

### Ejecutar la aplicación

```bash
# Con uv
uv run --env-file .env .\Checker.py

# Dev mode
uv run --env-file .env -- gradio .\Checker.py    

# O directamente con Python
python Checker.py
```

La aplicación se abrirá en <http://127.0.0.1:7860>

### Uso básico

1. **Pega texto o URL** de una noticia en el campo de entrada
2. **Haz clic en "Analizar noticia"**
3. **Revisa el resultado**: score, señales de alerta, fuentes encontradas
4. **Usa las búsquedas sugeridas** para verificar por tu cuenta

## 🔧 Configuración

### Variables de entorno (.env)

```env
OPENAI_API_KEY=sk-...

# Opcional - para búsqueda web
SERPAPI_KEY=...
BING_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CX=...
```

### Desde la UI

La pestaña **⚙️ Configuración** permite ajustar:

- API Key de OpenAI
- Modelo a usar (gpt-4o, gpt-4o-mini, etc.)
- Habilitar búsqueda web
- Proveedor de búsqueda (SerpAPI, Bing, Google)

## 📁 Estructura del Proyecto

```plaintext
Fake_News_Detector/
├── Checker.py              # Entry point
├── pyproject.toml          # Dependencias
├── README.md
├── .env                    # Variables de entorno (no commiteado)
├── history.db              # Base de datos SQLite (generado)
└── src/
    ├── __init__.py
    ├── config/             # Configuración
    │   ├── __init__.py
    │   └── settings.py     # Settings singleton
    ├── models/             # Modelos de dominio
    │   ├── __init__.py
    │   └── analysis.py     # AnalysisResult, NewsContent, etc.
    ├── repositories/       # Persistencia de datos
    │   ├── __init__.py
    │   └── history_repository.py
    ├── services/           # Lógica de negocio
    │   ├── __init__.py
    │   ├── scraper_service.py      # Extracción de URLs
    │   ├── search_service.py       # Búsqueda web
    │   ├── analysis_service.py     # Análisis con OpenAI
    │   └── verification_service.py # Orquestador principal
    └── ui/                 # Interfaz Gradio
        ├── __init__.py
        ├── components.py   # Componentes reutilizables
        └── app.py          # Aplicación Gradio
```

## 🏗️ Arquitectura (SOLID)

La aplicación sigue los principios SOLID:

- **S**ingle Responsibility: Cada servicio tiene una única responsabilidad
- **O**pen/Closed: Fácil agregar nuevos proveedores de búsqueda
- **L**iskov Substitution: SearchProvider implementa interfaz común
- **I**nterface Segregation: Interfaces pequeñas y específicas
- **D**ependency Inversion: Servicios inyectados, no hardcodeados

### Flujo de datos

```plaintext
Usuario → UI (Gradio)
           ↓
     VerificationService (orquestador)
           ↓
    ┌──────┴──────┐
    ↓             ↓
ScraperService  SearchService
    ↓             ↓
    └─────┬───────┘
          ↓
    AnalysisService (OpenAI)
          ↓
    HistoryRepository (SQLite)
          ↓
    AnalysisResult → UI
```

## ✨ Características

### Análisis de Veracidad

- Score numérico (0-100%)
- Veredicto textual
- Señales de alerta detectadas
- Claims principales identificados
- Recomendaciones de verificación

### Búsqueda de Fuentes

- Identifica origen de la noticia
- Contrasta con múltiples fuentes
- Cita fuentes en el análisis
- Soporta SerpAPI, Bing y Google

### Detección de Manipulación

- Lenguaje emotivo/sensacionalista
- Clickbait
- Falta de fuentes citadas
- Inconsistencias

### Historial

- Guarda análisis en SQLite
- Exportación a CSV
- Estadísticas agregadas

## 🔌 API de Búsqueda

### SerpAPI (recomendado)

```bash
https://serpapi.com/
```

### Bing Search (Azure)

```bash
https://portal.azure.com/ → Bing Search API
```

### Google Custom Search

```bash
https://programmablesearchengine.google.com/
```

## 📝 Licencia

MIT License

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

<p align="center">
  Desarrollado con ❤️ usando <a href="https://gradio.app">Gradio</a> y <a href="https://openai.com">OpenAI</a>
</p>
