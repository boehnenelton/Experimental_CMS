# Library Bug-Fix Report — lib_bejson_Core_bejson_path_guard.py

**Authorization:** Direct user instruction, this conversation, 2026-08-05 —
"Inspect all database... harden and refine, weed out any bugs." Verified via
reproduction before changing anything, per Section 3.5.2.

**File:** `Lib_PY/Core/lib_bejson_Core_bejson_path_guard.py`
**Version:** 1.0.0 → 1.1.0 (module `VERSION` constant: 1.2.0 → 1.3.0)

## The bug — sibling-directory traversal bypass

`bejson_safe_join()`'s containment check was:

```python
if not str(target_path).startswith(str(base_path)):
    raise ValueError(...)
```

A plain string prefix check. Any resolved path whose string representation
happens to start with `base_dir`'s string is accepted — including a
**sibling** directory that merely shares a name prefix. Example: base_dir
`/x/Data`, and a path that resolves to `/x/Data_secrets/leak.txt`. The
string `"/x/Data_secrets/leak.txt".startswith("/x/Data")` is `True`, so the
old check let it through, even though `/x/Data_secrets` is not inside
`/x/Data` at all.

Reproduced directly against this function: called with a `../Data_secrets/
leak.txt`-style relative path, it returned the resolved path with **no
exception raised**.

This function is the actual traversal guard applied to untrusted zip member
names in two places:
- `MFDBArchive.mount()` in `lib_bejson_Core_mfdb_core.py`, when extracting
  a `.mfdb.zip` archive.
- `CMS_Chunker_Wrapper` / `MFDB_CMS_Manager`'s backup-restore path in
  `lib_bejson_CMS_cms_mfdb.py`, when unpacking an admin-uploaded backup zip.

A crafted archive containing a member name engineered to resolve to a
sibling-prefixed path (e.g. `../Data_backup_evil/...`) could have written
outside the intended extraction root.

## The fix

Replaced the string-prefix check with `Path.relative_to()`, which raises
`ValueError` unless `target_path` is a genuine path-segment descendant of
`base_path` (or equal to it). This correctly rejects sibling-directory
matches while still accepting all legitimate nested paths.

## Verification

- Reproduction case (`../Data_secrets/leak.txt` against base_dir `Data`)
  now correctly raises `ValueError: Path traversal detected`.
- Legitimate nested joins (e.g. `bejson_safe_join(root, "data", "file.bejson")`)
  still resolve normally.
- All three call sites (`mfdb_core.py` zip extraction, and the two backup
  restore call sites in `cms_mfdb.py`) byte-compile and were smoke-tested
  with a normal (non-malicious) backup/restore round-trip.
