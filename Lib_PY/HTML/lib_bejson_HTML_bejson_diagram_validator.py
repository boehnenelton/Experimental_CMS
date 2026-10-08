"""
Library:        lib_bejson_HTML_bejson_diagram_validator.py
Family:         HTML
Description:    Drop-in replacement for lib_bejson_validator_diagram.py's
                 validation half. Same public function names
                 (bejson_validator_diagram_validate_string,
                 bejson_validator_diagram_validate_file) so existing callers
                 don't need to change their call sites — but the input
                 schema itself has changed (see below), and the logic
                 behind these names is now a real structural check instead
                 of the old no-op.

                 THE BUG THIS REPLACES: the old
                 bejson_validator_diagram_validate_string() called a
                 generic BEJSON syntax checker and then returned True
                 UNCONDITIONALLY, ignoring whatever that checker found. It
                 never validated anything diagram-specific — not anchors,
                 not relational integrity, nothing — despite defining
                 E_DIAGRAM_RELATIONAL_ERROR and E_DIAGRAM_INVALID_ANCHOR
                 error codes that were never referenced anywhere in the
                 file. A diagram with hallucinated connector references, a
                 broken hierarchy, or literally any structural problem
                 would have been reported "valid." See
                 references/BUGFIX_REPORT.md for the full list of issues
                 found and fixed across this update.

                 SCHEMA CHANGE: the old functions expected a BEJSON string
                 in the retired anchor-system / flat x-y-w-h schema
                 (Records_Type: ["Shape","Connector"], fields like s_x/s_y
                 or x_Shape/y_Shape). The new schema is center-point
                 (cx/cy) + sizeClass + kind, with an optional Territory
                 entity — see references/SCHEMA.md in the Diagrammer skill,
                 or the docstrings on lib_bejson_HTML_bejson_diagram_core.
                 The input to these functions is now a JSON string of the
                 ASSEMBLED diagram shape: {"name", "shapes": [...],
                 "connectors": [...], "territories": [...]}. If you're
                 validating a live MFDB folder instead of an assembled
                 JSON string, call bejson_diagram_core.load_mfdb_diagram()
                 directly and pass the result to
                 bejson_diagram_core.validate_diagram() — there's no
                 string-based entry point for that mode since a folder
                 isn't a single string.

Version:        1.0.1
Library_Version: 220
Date:           2026-07-18
Author:          Elton Boehnen
Contact:         eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator:  Elton Boehnen
RELATIONAL_ID:   3e8b1c6f-9a4d-4e2c-b5f7-1d3a6c9e2b80

Changelog:
  1.0.1 - Removed dead E_DIAGRAM_RELATIONAL_ERROR / E_DIAGRAM_INVALID_ANCHOR
          constants (verified unreferenced anywhere in the codebase).
"""

import json
from pathlib import Path

import lib_bejson_HTML_bejson_diagram_core as _core

# DEAD CODE REMOVED (2026-07-18): E_DIAGRAM_RELATIONAL_ERROR (100) and
# E_DIAGRAM_INVALID_ANCHOR (101) were defined here but never raised or
# referenced anywhere in the codebase (verified via full-tree grep). The
# retired anchor system they described no longer exists. Logged in
# BEJSON/MFDB/data/library_changes.bejson.


class DiagramValidationError(ValueError):
    """Raised when a diagram fails structural validation. Carries the full
    list of issues found (not just the first one) via .issues."""
    def __init__(self, issues):
        self.issues = issues
        super().__init__(f"{len(issues)} diagram validation issue(s): " + "; ".join(issues))


def bejson_validator_diagram_validate_string(json_string: str) -> bool:
    """
    Validates a diagram JSON string under the CURRENT schema.

    Unlike the function this replaces, this actually checks structure:
    duplicate shape ids, dangling connector/parentId references, parentId
    cycles, self-loop connectors, duplicate connector pairs, unknown
    sizeClass/kind/flow enum values, and shape/territory overlap.

    Raises DiagramValidationError (with the full issue list on .issues) if
    anything is wrong, or NotADiagramError if the input isn't diagram-shaped
    at all. Returns True only if the diagram is actually clean — this
    function can no longer return True unconditionally.
    """
    data = json.loads(json_string)
    if not isinstance(data, dict) or not any(k in data for k in ("shapes", "connectors", "territories")):
        raise _core.NotADiagramError(
            "Input has none of 'shapes', 'connectors', or 'territories' — not diagram-shaped data."
        )
    diagram = _core._normalize(data)
    issues = _core.validate_diagram(diagram)
    if issues:
        raise DiagramValidationError(issues)
    return True


def bejson_validator_diagram_validate_file(file_path: str) -> bool:
    text = Path(file_path).read_text(encoding="utf-8")
    return bejson_validator_diagram_validate_string(text)


def bejson_validator_diagram_get_issues(json_string: str):
    """
    Non-raising variant: returns the list of issues (empty list = clean)
    instead of raising. Useful when the caller wants to report every
    problem at once rather than handling an exception.
    """
    data = json.loads(json_string)
    if not isinstance(data, dict) or not any(k in data for k in ("shapes", "connectors", "territories")):
        raise _core.NotADiagramError(
            "Input has none of 'shapes', 'connectors', or 'territories' — not diagram-shaped data."
        )
    diagram = _core._normalize(data)
    return _core.validate_diagram(diagram)
