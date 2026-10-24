"""
Library:        lib_bejson_Core_bejson_path_guard.py
Family:         Core
Description:    Secure path resolver and boundary protection logic.
Version:        1.4.0
Date:           2026-08-08
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  324449f9-54ee-4634-8fe1-ac064eba4d25

RECONCILE (2026-08-08): Cross-checked against libraries.zip's Core-family
update package (dated 2026-08-07), which independently fixed the same
sibling-directory bypass using Path.is_relative_to() with a pre-3.9
fallback. This file's existing fix (Path.relative_to() in a try/except
ValueError) is functionally equivalent and sufficient - is_relative_to()
is implemented the same way internally, and the pre-3.9 fallback branch
is dead code under this project's Python >=3.10 floor. Kept this file's
implementation as canonical.
Also fixed a pre-existing drift bug in this file: the header Version
field said 1.1.0 while the internal VERSION constant at the bottom of
the file said 1.3.0 - two different numbers for the same file, in
violation of policy. Both now read 1.4.0.

BUGFIX (2026-08-05): bejson_safe_join()'s traversal check was a string
.startswith() comparison, bypassable via a sibling directory sharing a
name prefix with base_dir. Fixed using Path.relative_to() for real
path-segment containment. See BUGFIX_path_guard_traversal.md.
"""

import os
from pathlib import Path

def bejson_safe_join(base_dir: str, *paths: str) -> str:
    """
    Safely join paths and ensure the result is within the base_dir.
    Mitigates path traversal attacks (Phase 2).

    BUGFIX (2026-08-05): the containment check used to be a plain string
    `.startswith()` comparison, which is bypassable by any sibling directory
    that happens to share the same name prefix - e.g. base_dir "/x/Data" vs
    a crafted path resolving to "/x/Data_secrets/leak.txt": the string
    "/x/Data_secrets/leak.txt".startswith("/x/Data") is True even though
    that path is not inside base_dir at all. Reproduced against this exact
    function with base_dir="Data" and a '../Data_secrets/leak.txt' style
    target - it resolved and returned with no exception raised. This guard
    is the actual traversal check used when extracting untrusted zip member
    names during MFDBArchive.mount() and CMS backup restore, so a crafted
    archive with a sibling-prefixed member name could have written outside
    the intended root. Fixed by using Path.relative_to(), which checks real
    path-segment containment instead of a string prefix.
    """
    base_path = Path(base_dir).resolve()
    # Handle environment variables in paths if any
    resolved_paths = [os.path.expandvars(p) for p in paths]
    target_path = base_path.joinpath(*resolved_paths).resolve()

    try:
        target_path.relative_to(base_path)
    except ValueError:
        raise ValueError(f"Path traversal detected: {target_path} is outside of {base_path}")

    return str(target_path)

def resolve_storage_path(path: str) -> str:
    """
    Standardized resolve_path utility for environment abstraction (Phase 1).
    Prioritizes $BEJSON_STORAGE_ROOT.
    """
    storage_root = os.environ.get("BEJSON_STORAGE_ROOT")
    if not storage_root:
        # Fallback to local home if storage root is unknown
        storage_root = os.path.expanduser("~")
        
    if not path:
        return storage_root

    # Standardize absolute paths from legacy hardcoding (if encountered)
    if path.startswith("/storage/emulated/0"):
        return path.replace("/storage/emulated/0", storage_root)
        
    return path

def _bejson_mfdb_escapes_root(relative_path: str) -> bool:
    """
    Relative-depth path traversal check.  Normalizes separators then counts
    directory depth segment by segment.  Returns True (path is unsafe) if any
    '..' segment attempts to drop the depth below 0, indicating an escape
    above the MFDB root.

    Mirrors _escapesRoot in lib_bejson_Core_mfdb_validators.ts exactly
    (Remediation NEW-08).

    Args:
        relative_path: A relative path string, e.g. '../104a.mfdb.bejson'.

    Returns:
        True  — path escapes root (unsafe, reject).
        False — path stays within root (safe).
    """
    normalized = relative_path.replace("\\", "/")
    parts = normalized.split("/")
    depth = 0
    for part in parts:
        if part == "..":
            depth -= 1
            if depth < 0:
                return True
        elif part != "." and part != "":
            depth += 1
    return False


VERSION = "1.4.0"
