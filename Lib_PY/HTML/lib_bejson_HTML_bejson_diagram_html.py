"""
Library:        lib_bejson_HTML_bejson_diagram_html.py
Family:         HTML
Description:    Drop-in replacement for lib_bejson_diagram_html.py and the
                 export half of lib_bejson_validator_diagram.py. Same
                 public function names (bejson_diagram_export_html,
                 export_high_fidelity_diagram) so existing call sites don't
                 need to change — but two things underneath are different:

                 1. SCHEMA: input is now the assembled diagram shape
                    ({"name", "shapes": [...], "connectors": [...],
                    "territories": [...]}) under the current center-point +
                    sizeClass + kind schema, not the retired anchor-system /
                    flat x-y-w-h schema the old templates expected.

                 2. TEMPLATE: the old CYBERPUNK_TEMPLATE / HI_FI_TEMPLATE
                    defaulted to a dark theme (Orbitron font, glow filters,
                    animated dashed flow lines, #050b17 background) despite
                    the Diagrammer skill's own mandate explicitly banning
                    dark themes for audit diagrams ("I'll use a dark theme
                    for this technical map" was literally listed as a
                    rationalization to STOP on). It needed a bolted-on CSS
                    override block just to become compliant. The new
                    default template *is* the Universal Style Policy: white
                    background, black text/borders, #DE2626 used only
                    sparingly, Inter + Source Code Pro, flat design, no
                    glow, no animation. No override needed, none offered —
                    if a themed viewer is wanted, that's a different,
                    explicitly-requested deliverable, not this one.

Version:        1.0.0
Library_Version: 220
Date:            2026-07-09
Author:          Elton Boehnen
Contact:         eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator:  Elton Boehnen
RELATIONAL_ID:   e5f2a9c7-3b6d-4e1a-9f08-2c5d7a9b3e61
"""

import json

import lib_bejson_HTML_bejson_diagram_core as _core


def bejson_diagram_export_html(json_string: str, output_path: str, title: str = "BEJSON Diagram",
                                 css_sheets=None, internal_css: str = "") -> bool:
    """
    Generates a standalone HTML diagram viewer from a diagram JSON string
    (current schema — see module docstring). css_sheets/internal_css are
    accepted for call-site compatibility with the old signature but are
    currently no-ops: the flat template intentionally doesn't expose theme
    injection points. If external styling is genuinely needed, that's worth
    raising explicitly rather than silently reintroducing the override
    pattern this replacement was written to get rid of.
    """
    data = json.loads(json_string)
    if not isinstance(data, dict) or not any(k in data for k in ("shapes", "connectors", "territories")):
        raise _core.NotADiagramError(
            "Input has none of 'shapes', 'connectors', or 'territories' — not diagram-shaped data."
        )
    diagram = _core._normalize(data)
    _core.export_html(diagram, output_path, title=title)
    return True


def export_high_fidelity_diagram(json_data, output_path: str, title: str = "System Diagram", css_sheets=None) -> bool:
    """
    Legacy alias. json_data may be a dict (current schema) or a JSON string
    of one. Despite the name, this no longer produces the old "high
    fidelity" cyberpunk look — see module docstring for why. Kept as a
    separate name only because that's what the old file called it; behavior
    is identical to bejson_diagram_export_html().
    """
    data = json.loads(json_data) if isinstance(json_data, str) else json_data
    if not isinstance(data, dict) or not any(k in data for k in ("shapes", "connectors", "territories")):
        raise _core.NotADiagramError(
            "Input has none of 'shapes', 'connectors', or 'territories' — not diagram-shaped data."
        )
    diagram = _core._normalize(data)
    _core.export_html(diagram, output_path, title=title)
    return True


def bejson_diagram_export_from_mfdb(mfdb_root: str, output_path: str, title=None) -> bool:
    """
    New entry point (no legacy equivalent existed): exports directly from a
    live MFDB diagram folder instead of requiring an assembled JSON string
    first. Reads the manifest + Board + per-shape entities + Connector +
    Territory files directly.
    """
    diagram = _core.load_mfdb_diagram(mfdb_root)
    _core.export_html(diagram, output_path, title=title or diagram.get("name"))
    return True
