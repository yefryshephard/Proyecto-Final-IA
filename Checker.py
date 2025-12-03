"""
Fake News Detector - Entry Point
================================

A transparent fake news detection tool that:
- Analyzes text or URL input for veracity
- Provides a 0-100% credibility score
- Explains reasoning with cited sources
- Detects manipulative language and clickbait
- Searches multiple sources for verification
- Maintains analysis history

Usage:
    python Checker.py

Or with uv:
    uv run Checker.py
"""

import gradio as gr
from src.ui import create_app


def main():
    """Launch the Fake News Detector application."""
    # Create and launch the application
    demo = create_app()

    # Launch with custom configuration and theme
    demo.launch(
        theme=gr.themes.Soft(),
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )


if __name__ == "__main__":
    main()
