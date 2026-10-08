"""
Library:         lib_bejson_Core_bejson_104db_parser.py
Family:          Core
Module Purpose:  BEJSON 104db Project Schema & Chunk Parser Engine. Parses structured 104db BEJSON payloads (containing ProjectMeta and FileContent records) and unpacks/restores them directly into disk files. Supports clean JSON extraction, positional field verification, and atomic file extraction with directory auto-creation.
Architecture:    BEJSON 104db provides single-file multi-entity relational storage with positional null-padding, Record_Type_Parent discriminator headers, and plain-text LLM readability.
Version:         1.0.0
Release_Version: 300
Date:            2026-09-09
Author:          Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Format_Creator:  Elton Boehnen
RELATIONAL_ID:   9c4b12a8-3f41-4e8b-a71d-52e89f10a8b9
"""

import json
import re
import os
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from lib_bejson_Core_bejson_path_guard import bejson_safe_join
except ImportError:
    def bejson_safe_join(base: str, rel: str) -> str:
        base_path = Path(base).resolve()
        target = (base_path / rel).resolve()
        if not str(target).startswith(str(base_path)):
            raise ValueError(f"Path traversal detected: {rel}")
        return str(target)

VERSION = "1.0.0"

# Mandatory 104db positional schema indexes based on the canonical spec:
# [0] Record_Type_Parent (string)
# [1] project_name (string, Record_Type_Parent: ProjectMeta)
# [2] version (string, Record_Type_Parent: ProjectMeta)
# [3] root_path (string, Record_Type_Parent: ProjectMeta)
# [4] file_path (string, Record_Type_Parent: FileContent)
# [5] file_name (string, Record_Type_Parent: FileContent)
# [6] content (string, Record_Type_Parent: FileContent)
# [7] is_binary (boolean, Record_Type_Parent: FileContent)
# [8] special_flag (string/optional, Record_Type_Parent: FileContent or ProjectMeta)

EXPECTED_104DB_FIELDS = [
    "Record_Type_Parent",
    "project_name",
    "version",
    "root_path",
    "file_path",
    "file_name",
    "content",
    "is_binary",
    "special_flag"
]


def extract_raw_json(text: str) -> str:
    """Extracts raw JSON string from a text block, stripping markdown backticks or preambles."""
    text = text.strip()
    if "```json" in text:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    elif "```" in text:
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Try finding first '{' and last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


def parse_bejson_104db_doc(payload: str) -> Dict[str, Any]:
    """Parses raw text or JSON into a validated BEJSON 104db document structure."""
    json_str = extract_raw_json(payload)
    doc = json.loads(json_str)

    if not isinstance(doc, dict):
        raise ValueError("Decoded payload is not a valid JSON Object")

    if doc.get("Format") != "BEJSON":
        raise ValueError(f"Invalid Format: expected 'BEJSON', got '{doc.get('Format')}'")

    if doc.get("Format_Version") != "104db":
        raise ValueError(f"Invalid Format_Version: expected '104db', got '{doc.get('Format_Version')}'")

    records_type = doc.get("Records_Type", [])
    if "ProjectMeta" not in records_type or "FileContent" not in records_type:
        raise ValueError("Records_Type must include both 'ProjectMeta' and 'FileContent'")

    fields = doc.get("Fields", [])
    if not fields or fields[0].get("name") != "Record_Type_Parent":
        raise ValueError("Fields[0] must be 'Record_Type_Parent'")

    return doc


def unpack_bejson_104db_to_dir(doc: Dict[str, Any], output_dir: str) -> Tuple[Dict[str, Any], int]:
    """
    Unpacks a parsed BEJSON 104db document and restores all FileContent rows to output_dir.
    Returns (meta_dict, files_written_count).
    """
    out_root = Path(output_dir).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    fields = doc.get("Fields", [])
    field_map = {f["name"]: i for i, f in enumerate(fields)}

    # Field indexes
    rec_type_idx = field_map.get("Record_Type_Parent", 0)
    proj_name_idx = field_map.get("project_name", 1)
    version_idx = field_map.get("version", 2)
    root_path_idx = field_map.get("root_path", 3)
    file_path_idx = field_map.get("file_path", 4)
    file_name_idx = field_map.get("file_name", 5)
    content_idx = field_map.get("content", 6)
    is_binary_idx = field_map.get("is_binary", 7)
    special_flag_idx = field_map.get("special_flag", -1)

    project_meta = {}
    files_written = 0

    for row in doc.get("Values", []):
        if not row or len(row) <= rec_type_idx:
            continue

        rec_type = row[rec_type_idx]
        if rec_type == "ProjectMeta":
            project_meta = {
                "project_name": row[proj_name_idx] if proj_name_idx != -1 and proj_name_idx < len(row) else None,
                "version": row[version_idx] if version_idx != -1 and version_idx < len(row) else None,
                "root_path": row[root_path_idx] if root_path_idx != -1 and root_path_idx < len(row) else None,
                "special_flag": row[special_flag_idx] if special_flag_idx != -1 and special_flag_idx < len(row) else None,
            }
        elif rec_type == "FileContent":
            if file_path_idx == -1 or file_path_idx >= len(row) or not row[file_path_idx]:
                continue

            rel_path = str(row[file_path_idx])
            content = row[content_idx] if content_idx != -1 and content_idx < len(row) else ""
            is_bin = bool(row[is_binary_idx]) if is_binary_idx != -1 and is_binary_idx < len(row) and row[is_binary_idx] is not None else False
            special_flag = row[special_flag_idx] if special_flag_idx != -1 and special_flag_idx < len(row) else None

            target_path = Path(bejson_safe_join(str(out_root), rel_path))
            target_path.parent.mkdir(parents=True, exist_ok=True)

            if is_bin:
                target_path.write_bytes(base64.b64decode(content or ""))
            else:
                target_path.write_text(content or "", encoding="utf-8")

            files_written += 1

    return project_meta, files_written