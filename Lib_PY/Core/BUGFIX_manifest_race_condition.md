# Library Bug-Fix Report — lib_bejson_Core_mfdb_core.py

**Authorization:** Direct user instruction, this conversation, 2026-08-05 —
"Inspect all database... harden and refine, weed out any bugs." Verified via
reproduction before changing anything, per Section 3.5.2.

**File:** `Lib_PY/Core/lib_bejson_Core_mfdb_core.py`
**Version:** 2.3.0 → 2.3.1

## The bug — manifest `record_count` lost-update race

`mfdb_core_add_entity_record()`, `mfdb_core_remove_entity_record()`, and the
update functions each take a `ResilientPIDLock` on the **entity file's own
path** for their read-modify-write cycle — correct, and sufficient to protect
the entity file itself. But every one of them finishes by calling
`_update_manifest_record_count(manifest_path, ...)`, which does its own
separate read-modify-write of the **shared manifest file** — previously with
no lock of any kind.

Two different entities under the same manifest (e.g. adding a `NavLink` and
adding an `AuthorProfile` at the same time) lock two *different* entity
files, so neither blocks the other. Both then race into the unlocked
manifest read-modify-write: both read the same starting manifest doc,
each mutates only its own entity's row in memory, and whichever call's
`_write_manifest_doc()` lands last overwrites the file with its own
in-memory copy — silently discarding the other write's `record_count`
update. The entity data files themselves stay correct; only the manifest's
cached `record_count` column (used for dashboard stats) can drift, which is
exactly the class of problem `mfdb_core_sync_all_counts()` exists to repair
after the fact rather than prevent at the source.

Not currently triggerable in Experimental CMS's own deployment (Flask dev
server runs single-threaded), but it is a real defect in a shared library
used across other projects, and would activate the moment any caller runs
multi-threaded or multi-process.

## The fix

`_update_manifest_record_count()` now wraps its full read-modify-write in
`ResilientPIDLock(manifest_path, timeout_seconds=10)`. Verified no existing
call site ever holds a lock on `manifest_path` before calling this function
(the four CRUD functions lock `entity_path`, a different file), so this
introduces no reentrancy/deadlock risk against current callers.

## Verification

- Full test tree in `Lib_PY/Core/` byte-compiles clean.
- `mfdb_core_add_entity_record`, `remove`, and bulk-update smoke-tested
  individually post-change — all still commit correctly.
- No behavior change for the existing single-threaded call pattern; this is
  a pure hardening fix for concurrent access.
