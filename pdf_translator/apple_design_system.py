"""
Apple Design System helpers for Python web UIs (Gradio, http.server, Flask…).

Exposes:
    APPLE_CSS            — full CSS stylesheet as a string
    APPLE_TOKENS         — dict of color / spacing / typography tokens
    gradio_theme()       — returns a gr.themes.Soft() preconfigured to look Apple-ish
    inline_style_tag()   — returns a <style>…</style> block ready to embed in HTML

The CSS is based on Apple Human Interface Guidelines:
    - SF Pro type ramp (Large Title → Caption)
    - System color palette + semantic aliases
    - Light + dark mode via prefers-color-scheme
    - 4pt spacing grid, squircle radii, elevation shadows
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = [
    "APPLE_CSS",
    "APPLE_TOKENS",
    "gradio_theme",
    "inline_style_tag",
    "load_css",
]


APPLE_TOKENS = {
    "color": {
        "blue":   "#0071e3",
        "indigo": "#5856d6",
        "purple": "#af52de",
        "pink":   "#ff2d55",
        "red":    "#ff3b30",
        "orange": "#ff9500",
        "yellow": "#ffcc00",
        "green":  "#34c759",
        "mint":   "#00c7be",
        "teal":   "#30b0c7",
        "cyan":   "#32ade6",
        "brown":  "#a2845e",
        "gray_1": "#8e8e93",
        "gray_2": "#aeaeb2",
        "gray_3": "#c7c7cc",
        "gray_4": "#d1d1d6",
        "gray_5": "#e5e5ea",
        "gray_6": "#f2f2f7",
    },
    "semantic": {
        "bg_primary":    "#f5f5f7",
        "bg_secondary":  "#ffffff",
        "bg_tertiary":   "#f2f2f7",
        "text_primary":  "#1d1d1f",
        "text_secondary":"#86868b",
        "text_tertiary": "#aeaeb2",
        "accent":        "#0071e3",
        "success":       "#34c759",
        "warning":       "#ff9500",
        "danger":        "#ff3b30",
        "separator":     "rgba(60, 60, 67, 0.12)",
    },
    "radius": {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "xxl": 28},
    "space":  {"1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24,
               "7": 32, "8": 40, "9": 48, "10": 64},
    "font": {
        "sans":   ('-apple-system, BlinkMacSystemFont, "SF Pro Display", '
                   '"SF Pro Text", "Helvetica Neue", "PingFang SC", '
                   '"Microsoft YaHei", "Segoe UI", sans-serif'),
        "mono":   ('"SF Mono", SFMono-Regular, ui-monospace, Menlo, Monaco, '
                   "Consolas, monospace"),
        "rounded":'ui-rounded, "SF Pro Rounded", -apple-system, system-ui, sans-serif',
    },
    "type_scale": {
        "large_title": 34, "title_1": 28, "title_2": 22, "title_3": 20,
        "headline":    17, "body":    17, "callout": 16, "subhead": 15,
        "footnote":    13, "caption_1": 12, "caption_2": 11,
    },
    "shadow": {
        "sm": "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)",
        "md": "0 4px 14px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.04)",
        "lg": "0 8px 28px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)",
    },
}


def _locate_css() -> Path:
    """Find apple_design_system.css next to this module or at repo root."""
    here = Path(__file__).resolve().parent
    for candidate in (here / "apple_design_system.css",
                      here.parent / "apple_design_system.css"):
        if candidate.exists():
            return candidate
    return here.parent / "apple_design_system.css"


def load_css() -> str:
    """Read the CSS file from disk (falls back to the embedded copy)."""
    path = _locate_css()
    if path.exists():
        return path.read_text(encoding="utf-8")
    return _EMBEDDED_CSS


def inline_style_tag() -> str:
    """Return a <style>...</style> block for injection into an HTML template."""
    return f"<style>\n{load_css()}\n</style>"


def gradio_theme():
    """Return a Gradio theme approximating Apple's look.

    Falls back silently if gradio isn't installed.
    """
    try:
        import gradio as gr
    except ImportError:  # pragma: no cover
        return None

    t = APPLE_TOKENS
    return gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.slate,
        neutral_hue=gr.themes.colors.gray,
        font=(gr.themes.GoogleFont("Inter"), "ui-sans-serif",
              "system-ui", "-apple-system", "BlinkMacSystemFont",
              "SF Pro Display", "sans-serif"),
        font_mono=(gr.themes.GoogleFont("JetBrains Mono"), "SF Mono",
                   "ui-monospace", "Menlo", "monospace"),
    ).set(
        body_background_fill=t["semantic"]["bg_primary"],
        body_background_fill_dark="#000000",
        background_fill_primary=t["semantic"]["bg_secondary"],
        background_fill_primary_dark="#1c1c1e",
        background_fill_secondary=t["semantic"]["bg_tertiary"],
        background_fill_secondary_dark="#2c2c2e",
        body_text_color=t["semantic"]["text_primary"],
        body_text_color_dark="#f5f5f7",
        body_text_color_subdued=t["semantic"]["text_secondary"],
        button_primary_background_fill=t["semantic"]["accent"],
        button_primary_background_fill_hover="#0077ed",
        button_primary_text_color="#ffffff",
        button_primary_border_color=t["semantic"]["accent"],
        button_secondary_background_fill=t["semantic"]["bg_tertiary"],
        button_secondary_text_color=t["semantic"]["accent"],
        block_background_fill=t["semantic"]["bg_secondary"],
        block_border_width="0.5px",
        block_border_color=t["semantic"]["separator"],
        block_radius="16px",
        block_shadow=t["shadow"]["sm"],
        block_title_text_color=t["semantic"]["text_secondary"],
        block_title_text_weight="600",
        input_background_fill=t["semantic"]["bg_tertiary"],
        input_background_fill_focus=t["semantic"]["bg_secondary"],
        input_border_color="transparent",
        input_border_color_focus=t["semantic"]["accent"],
        input_radius="8px",
        input_shadow="none",
        input_shadow_focus="0 0 0 3px rgba(0, 113, 227, 0.2)",
        slider_color=t["semantic"]["accent"],
        panel_background_fill=t["semantic"]["bg_secondary"],
        layout_gap="16px",
    )


# Minimal embedded fallback in case the external CSS file isn't shipped
# (kept short — the real stylesheet is apple_design_system.css at the repo root)
_EMBEDDED_CSS = """
:root{
    --bg-primary:#f5f5f7;--bg-secondary:#fff;--bg-tertiary:#f2f2f7;
    --text-primary:#1d1d1f;--text-secondary:#86868b;--text-tertiary:#aeaeb2;
    --accent:#0071e3;--accent-hover:#0077ed;--accent-active:#006edb;
    --success:#34c759;--danger:#ff3b30;--warning:#ff9500;
    --separator:rgba(60,60,67,0.12);
    --shadow-sm:0 1px 3px rgba(0,0,0,.04),0 1px 2px rgba(0,0,0,.06);
    --shadow-md:0 4px 14px rgba(0,0,0,.06),0 2px 6px rgba(0,0,0,.04);
    --radius-sm:8px;--radius-md:12px;--radius-lg:16px;
    --font:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text",
          "Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;
}
@media (prefers-color-scheme: dark){
    :root{--bg-primary:#000;--bg-secondary:#1c1c1e;--bg-tertiary:#2c2c2e;
          --text-primary:#f5f5f7;--text-secondary:#98989d;--accent:#0a84ff;}
}
body{font-family:var(--font);background:var(--bg-primary);color:var(--text-primary);
     -webkit-font-smoothing:antialiased;margin:0;}
"""


# Read the CSS once at import so downstream code can use APPLE_CSS directly
APPLE_CSS = load_css()
