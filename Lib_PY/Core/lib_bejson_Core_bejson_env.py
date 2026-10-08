"""
Library:         lib_bejson_Core_bejson_env.py
Family:          Core
Module Purpose:  Implements runtime functionality and logic for lib_bejson_Core_bejson_env.py.
Architecture:    BEJSON Core provides foundational format parsing, schema enforcement, path security, positional field map caching, and multi-format integration across runtime environments.
Version:         2.2.0
Release_Version: 300
Date:            2026-09-13
Author:          Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Format_Creator:  Elton Boehnen
RELATIONAL_ID:   91453b6e-3950-41d9-8a0f-c6a946f54d53
"""

import os
import sys
from pathlib import Path


def _load_env_file(p: Path) -> bool:
    """Applies one env file's contents to the process environment.
    .json files are parsed as BEJSON 104a (Values rows -> os.environ);
    .py files are exec()'d as before. Returns False on any failure."""
    try:
        if p.suffix == ".json":
            import json
            data = json.loads(p.read_text(encoding="utf-8"))
            for row in data.get("Values", []):
                if isinstance(row, list) and len(row) >= 2:
                    var_name, var_val = str(row[0]).strip(), str(row[1]).strip()
                    if var_name and var_val:
                        os.environ[var_name] = var_val
        else:
            exec(p.read_text(encoding="utf-8"), globals())
        return True
    except Exception:
        return False


def source_env(override_path: str = None) -> bool:
    """
    Mandatory Environment Sourcing (Global Operating Rules 4.5).
    Priority: 1. override_path/ENV_FILE_PATH, 2. secure credentials AND user
    paths (both sourced, not either/or), 3. transitory/legacy fallback.
    """
    env_path = override_path or os.environ.get("ENV_FILE_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return _load_env_file(p)

    secure_candidates = [
        Path("/storage/emulated/0/.env/secure/secureenv_file.py"),
        Path("/storage/emulated/0/.env/secure/secureenv_file.json"),
    ]
    user_candidates = [
        Path("/storage/emulated/0/.env/user/paths.py"),
        Path("/storage/emulated/0/.env/user/paths.json"),
    ]

    loaded_any = False
    for p in secure_candidates:
        if p.exists() and _load_env_file(p):
            loaded_any = True
            break
    for p in user_candidates:
        if p.exists() and _load_env_file(p):
            loaded_any = True
            break
    if loaded_any:
        return True

    # Transitory/legacy fallback - only reached if neither mandatory tier exists.
    fallback_candidates = [
        Path("/storage/emulated/0/env_file.py"),
        Path("/storage/emulated/0/env_file.json"),
        Path.home() / "env_file.py",
    ]
    for p in fallback_candidates:
        if p.exists() and _load_env_file(p):
            return True
    return False

def resolve_path(path_str: str) -> str:
    """
    Resolves system placeholders and absolute paths to environment-relative paths.
    Prioritizes environment variables (ADMIN_ROOT, BEJSON_LIB_ROOT, etc).
    """
    if not path_str:
        return path_str
    
    # Define standard roots with defaults
    home = os.environ.get("HOME", os.path.expanduser("~"))
    
    # Storage and Admin Roots
    # Fallback to HOME if storage root is unset to avoid hardcodes.
    storage_root = os.environ.get("BEJSON_STORAGE_ROOT", home)
    admin_root   = os.environ.get("ADMIN_ROOT", os.path.join(storage_root, "Admin"))
    
    # Library Root Resolution (Admin/libraries fallback to ~/libraries)
    lib_root = os.environ.get("BEJSON_LIB_ROOT")
    if not lib_root:
        candidate_admin = os.path.join(admin_root, "libraries")
        candidate_home  = os.path.join(home, "libraries")
        lib_root = candidate_admin if os.path.exists(candidate_admin) else candidate_home
    
    mappings = {
        "{BEJSON_LIB_ROOT}": lib_root,
        "{ADMIN_ROOT}": admin_root,
        "{INTERNAL_STORAGE}": storage_root,
        "{HOME}": home
    }
    
    # Legacy absolute paths to be replaced
    # Only replace if storage_root is explicitly set to avoid "Vanishing Data".
    if os.environ.get("BEJSON_STORAGE_ROOT"):
        mappings["/storage/emulated/0"] = storage_root
        mappings["/data/data/com.termux/files/home"] = home
    
    resolved = str(path_str)
    
    # Sort keys by length descending to avoid partial matches (e.g. {HOME}_STUFF)
    for placeholder in sorted(mappings.keys(), key=len, reverse=True):
        actual = mappings[placeholder]
        if actual:
            resolved = resolved.replace(placeholder, actual)
    
    # Handle home expansion
    resolved = os.path.expanduser(resolved)
    # Handle environment variables in path (e.g. $VAR)
    resolved = os.path.expandvars(resolved)
    
    return os.path.normpath(resolved)

def get_env_path(env_var: str, default: str) -> str:
    """Retrieves an environment variable and resolves it as a path."""
    val = os.getenv(env_var, default)
    return resolve_path(val)