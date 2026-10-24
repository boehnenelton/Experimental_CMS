# Security & Integrity Notes

## 2026-08-18 — pkg29 audit-fix pass — Phase 1 (security)

- **NEW-H1 (High)**: `do_unchunk()` in
  `Lib_PY/ExpCMS/lib_bejson_ExpCMS_mfdb_chunker_v6.py` wrote restored
  files at `out_dir / rel_path` with no boundary check. `rel_path`
  comes from restored **entity row data** (backup contents), not zip
  member names — `safe_extract_zip`'s per-member `bejson_safe_join`
  check (LIB-CH-H2, pkg24) never sees it. A crafted backup could carry
  `file_path` values like `../../../anything` inside the chunked rows
  and write outside the unchunk staging directory. Fixed: the target
  path is now resolved through `bejson_safe_join()`, which raises on
  any escape attempt; the existing `except Exception` turns that into
  a clean rejected-restore result.
  - **Not yet fixed — flagged for explicit go-ahead**: the identical
    pattern (unchecked `rel_path` join) exists in the **Core** family
    lib `Lib_PY/Core/lib_bejson_Core_bejson_chunking.py`, in
    `bejson_core_chunking_unchunk_chunked_104()` and a second unchunk
    site (~line 789, appears to be `resurrect_file`/mount). Core is
    shared across other projects, so per the library-immutability
    policy this was left untouched pending your explicit sign-off.
- **NEW-H2 (High)**: preview server (`/srv/start`, `EXPCMS.py`) bound
  `""` (0.0.0.0) unconditionally — H1 (pkg25) locked the *admin* app
  to loopback but missed the preview server, which serves the built
  site (including hosted standalone apps) with no auth. Now reads
  `EXPCMS_PREVIEW_HOST` (default `127.0.0.1`), warns loudly if set to
  a non-loopback host — same pattern as `EXPCMS_HOST`.
- **NEW-H3 (High)**: `/apps` zip import accepted `entry_file` from the
  form with no validation, then `EXPCMS_Builder.py` interpolated it
  raw into an unescaped iframe `src` on every built app page — a
  crafted value could inject HTML attributes or an arbitrary path.
  Fixed on both ends: `EXPCMS.py` now runs `entry_file` through
  `secure_filename()` and rejects the import if the result isn't
  actually present in the extracted zip; `EXPCMS_Builder.py` also
  `html.escape()`s it before interpolation and adds
  `sandbox="allow-scripts allow-same-origin"` to the iframe, since
  hosted apps are arbitrary admin-uploaded content and should be
  treated as untrusted on the public site.
- **NEW-M5 (Medium)**: `Lib_PY/Core/cli/CLI_Doc_Chunker/update-libs.txt`
  contained an instruction addressed to an AI/human agent, referencing
  a "cracked folder" and asking that dependency imports be added and
  "sent back." This is a social-engineering / prompt-injection
  artifact embedded in the repo — its instructions were **not**
  followed. Moved to `docs/quarantine/update-libs.txt.quarantined`
  with a provenance note in `docs/quarantine/README.md`. The rest of
  the bundled `CLI_Doc_Chunker` tool should be treated as tainted
  until you've reviewed where it came from (it was already flagged
  non-runtime/broken at L13, pkg27, so this doesn't affect the CMS
  itself).

**Next**: Phase 2 (NEW-M1 zip-bomb guard on media upload, NEW-M2
POST-ify remaining GET state-changing routes, NEW-M3 upload size cap,
NEW-M4 atomic site build) targeted for pkg30.

## 2026-08-18 — pkg28 audit-fix pass — Phase 0 (NEW-C1, critical regression)

Full re-audit (2026-08-18, see project docs) found one critical
functional regression introduced by pkg26's own M6 fix, plus new
security/robustness findings scheduled for Phase 1-3 in subsequent
packages. This entry covers Phase 0 only.

- **NEW-C1 (Critical)**: `_unique_page_slug()` and `update_page()` in
  `Lib_PY/ExpCMS/lib_bejson_ExpCMS_cms_mfdb.py` referenced a field
  named `page_slug`, but the `Page` entity's actual schema field is
  `slug` (confirmed in `Data/workspace/db_content/data/page.bejson`
  and `initialize_system()`). Result: `create_page()` raised
  `KeyError` on any category that already had a page — i.e. every
  category in the shipped DB — and `update_page()` raised
  `BEJSONCoreError` *after* the title had already been written,
  leaving a partial/inconsistent record. Both call sites corrected to
  use `slug`. The matching dead fallback
  (`page_data.get("page_slug") or page_data.get("slug")`) in
  `EXPCMS.py::preview_page()` was also removed — it only existed
  because of this same bug.
  - Verified: created two pages with identical titles in one
    category (second correctly gets a `-2` suffix); edited an
    existing page's title (slug regenerates, old built URL stops
    resolving, no 500 on save).

**Next**: Phase 1 (NEW-H1 path traversal in `do_unchunk`, NEW-H2
preview server binding all interfaces, NEW-H3 unsanitized
`entry_file` in built-site iframes, NEW-M5 suspicious
`update-libs.txt` instruction file) targeted for pkg29.

## 2026-08-12 — pkg27 audit-fix pass, part 3 (L1–L14) — audit closed

Final pass over the full audit report. All Low-priority findings
addressed except two the audit itself flagged as informational-only:

- **L1**: hardcoded Flask `secret_key` -> `EXPCMS_SECRET_KEY` env var,
  falling back to a random per-process key.
- **L2**: malformed `source_files_json` in `/save` now flashes a clear
  error and redirects instead of a raw 500.
- **L3**: zip-import folder labels sanitized (strips `..`/leading
  slashes) before being stored as the `MediaAsset.folder` display value.
- **L4**: `/preview/<uuid>` computes the built page path directly from
  the page record instead of glob-scanning and reading every built HTML
  file on every request.
- **L5**: `static_folder` no longer points at `templates/` (was serving
  raw Jinja source, including admin-only templates, at
  `/static/*.html` - nothing in the app even references `/static/`).
- **L6**: removed the dead `/assets/<path>` route (pointed at a
  `BASE_DIR/Assets` directory that's never created or referenced
  anywhere; the built site's real `assets/` folder is populated from
  MediaAsset records into `Processing/www/assets/` by a different code
  path entirely).
- **L7**: hardcoded stale "v3.1"/"MFDB v1.3.1"/"Python 3.13" strings in
  `about.html`, `dashboard.html`, and `Global_Skeleton.html` replaced
  with a live `expcms_version` pulled from `.bejson_project.json`'s
  `Project_Version` - single source of truth for both the Flask admin
  and the static-site builder. Also fixed literal `**BEJSON**`/`**MFDB**`
  asterisks in `about.html` (leftover markdown syntax sitting in raw
  HTML) and the stale MFDB/Python version claims next to them.
- **L8**: `_build_page()` now resolves `author_fk` into an actual author
  record before rendering `Article_Skeleton.html`. The author bio block
  the skeleton already had markup for was dead on every single built
  page, regardless of whether a page had an author assigned - nothing
  ever did the lookup.
- **L9**: `related_block` is now populated with up to 3 other pages from
  the same category (newest first), reusing the existing Blog card
  template with a relative-path adjustment. Previously always `""`, so
  the "More from `<category>`" section in `Global_Skeleton.html` never
  rendered on any built page despite the skeleton, `_render_page()`, and
  `_build_page()` all plumbing it through.
- **L10**: `categories.html` offers 6 `feed_type` options but only 4 card
  templates existed; `gallery` silently fell through to the Blog card.
  Routed `gallery` to the Masonry template instead (closest existing
  layout to an image grid). `article` and `app` still correctly fall to
  Blog - that's the intended behavior for those two, not a gap.
- **L11**: `categories()`/`pages()` routes resolved entity file paths
  hardcoded as `data/category.bejson`/`data/page.bejson` instead of
  looking them up in the manifest like every other route does. Added
  `_load_entity_doc_via_manifest()` and switched both routes to use it.
- **L12** (Global Fonts CDN dependency on the built site) and **L13**
  (bundled `Lib_PY/Core/cli/CLI_Doc_Chunker/Doc_Chunker.py` importing a
  nonexistent `lib_bejson_utility`) were flagged by the audit as
  informational only - L12 is an accepted tradeoff scoped to the admin
  UI, not the built site, and L13 is a broken bundled tool that isn't
  part of the CMS runtime (nothing imports or calls it). No fix applied
  to either; noted here for the record.
- **L14**: removed an empty, functionless `<script></script>` tag from
  `admin_base.html`.

Every finding from the full audit report (`docs/audit-2026-08-11.md`, or
see PKG25/26/27 changelog entries) is now closed.

## 2026-08-12 — pkg26 audit-fix pass, part 2 (M2–M9)

Second half of the full audit fix. All Medium findings now resolved:

- **M2**: `backup_site()`/`restore_site()` retargeted from `www_root`
  (the built static site) to `cms.workspace_root` (`db_global/` +
  `db_content/`, the actual MFDB masters). Previously a restore never
  recovered any CMS content - only rendered HTML the next build would
  overwrite anyway - and the chunker's scratch files
  (`chunker_config.json`, `.mfdb/`) polluted the served site. The
  `/backup/restore` route now also re-mounts and rebuilds automatically
  on a successful restore.
- **M3**: `_generate_sidebar()` and the landing-image branch in
  `EXPCMS_Builder.py` now `html.escape()` every interpolated value
  (category names, nav labels/URLs, site title, image filename) instead
  of raw f-string concatenation - the same bug class pkg20 already fixed
  in the feed cards, missed in these two spots.
- **M4**: all 10 destructive routes (`factory_reset`, `repack`, and the
  8 delete routes) converted from GET links to POST-only routes with
  form-submit buttons. Previously any page the admin visited could
  trigger them via a plain `<img src="...">` (CSRF). `Data-Table.html`
  (the shared admin list component) now renders an inline `<form>` for
  any action flagged `method: 'POST'`.
- **M6**: `create_page()`/`update_page()` now go through a new
  `_unique_page_slug()` helper - two pages with the same title in the
  same category previously got the same slug, and the builder silently
  overwrote the first page's built `index.html` with the second's while
  both stayed in the DB. `update_page()` also now regenerates the slug
  when the title changes (it never did, so renamed pages kept building
  at their stale old URL).
- **M7**: `delete_category()` now reassigns member pages to
  `uncategorized` before removing the category, instead of leaving them
  with a dangling `category_fk` (silently invisible in every feed - the
  same trap pkg19 fixed for blank categories).
- **M8**: `ads.html`'s "+ NEW AD UNIT" reset handler used a CSS selector
  (`.u-flex .c-code-box__copy`) that matched nothing in the template, so
  it never attached; editing an ad then opening "new" reused stale
  values. Fixed via a dedicated button id (same pattern pkg22 used for
  `authors.html`).
- **M9**: the page editor's type dropdown only offered Article/Gallery/
  Product even though `save_page()` has handled Video/PDF Viewer/Source
  Code since those types were added; the latter three had no matching
  input fields either. Added all three options plus PDF URL and Source
  Files (JSON) fields.
- **Also fixed while in the area**: an `original_filename` vs.
  `original_name` field-name mismatch in `editor_main.html`'s
  featured-image dropdown (same bug class as H4, a second instance of
  it that H4 didn't name specifically) and in `media_library.html`.

**Remaining from the audit:** L1–L14 (Low priority) are not yet
addressed. See the full audit report for details.

## 2026-08-11 — pkg25 audit-fix pass

Full audit performed (Critical/High/Medium/Low findings). This pass fixed
all Critical and High findings plus the first Medium finding; remaining
Medium/Low items are tracked for a follow-up pkg. Findings fixed:

- **C1** (zip-slip in `/apps` import): `EXPCMS.py`'s `/apps` route called
  `zipfile.extractall()` directly on an uploaded app zip - the exact
  vulnerability class pkg24 fixed in the chunker (LIB-CH-H2) but never
  applied here. Now routes through `safe_extract_zip()` (per-member
  `bejson_safe_join` boundary check) plus a member-count/uncompressed-size
  guard.
- **C2** (stored XSS via HTML import): `import_html_as_page()` did no
  sanitization at all, despite README/usage-guide documentation claiming
  it strips scripts and AI-tool watermarks via BeautifulSoup.
  `html_body` is rendered with `| safe` on every built page, so an
  imported file's `<script>`/event-handler content reached the live site
  unmodified. Added `_sanitize_imported_html()` and wired it in.
- **H1** (debug server on 0.0.0.0): `app.run(host='0.0.0.0', debug=True)`
  with zero authentication anywhere exposed the Werkzeug interactive
  debugger (arbitrary code execution) to the whole LAN. Now defaults to
  `127.0.0.1` with debug off; overridable via `EXPCMS_HOST`/
  `EXPCMS_PORT`/`EXPCMS_DEBUG` env vars, with a printed warning if
  debug is explicitly forced on a non-loopback host.
- **H2** (MediaAsset schema drift): installs whose global manifest
  predated the `MediaAsset.folder` field (or the `VideoAsset` entity
  entirely) silently failed every upload - `mfdb_core_add_entity_record`
  rejects length mismatches, and the per-file `except` swallowed the
  error. Added `_reconcile_global_schema()`, run on every `mount_system()`
  call, which appends missing fields to the end of an entity's `Fields[]`
  (positional integrity preserved) and pads existing rows, or registers a
  missing entity outright. Also fixed a webp-conversion call in
  `optimize_assets()` that was passing 6 values against the 7-field
  schema.
- **H3** (Standalone App category never saves): template posted
  `name="category"`, route read `category_fk` (always `None`); dropdown
  options also used the wrong dict keys (`c.slug`/`c.name` vs. the actual
  `category_slug`/`category_name`). Both fixed.
- **H4** (featured-image picker always empty): `editor_main.html` checked
  `a.content_type`, but the MediaAsset field is `mime_type`. Fixed
  (same bug pkg17 fixed in `media_library.html`, missed here).
- **H5** (live data integrity): one live page (`c6d693b8…`, "Needs
  fixed") had `category_fk: ""`, silently dropping it from every feed.
  Reassigned to `uncategorized`.
- **H6** (broken app-page iframe): app files are copied to
  `www/apps/<app_uuid>/`, but the generated wrapper page embedded a bare
  `<entry_file>` src, which resolved to the wrapper page itself
  (self-embedding loop). Fixed to `../../apps/<app_uuid>/<entry_file>`.
- **M1** (backup/restore path traversal): `restore_site()`'s
  `zip_filename` came straight from the POST body; a crafted value could
  escape `backup_dir`. Now sanitized via `os.path.basename()` and
  re-verified with `bejson_safe_join()`.

**Deferred to next pkg:** M2 (backup chunks the built `www` output, not
the actual MFDB masters - restoring never recovers content, only
rendered HTML; also pollutes `www_root` with `chunker_config.json`),
M3–M9, L1–L14. See the full audit report for details.

## 2026-08-08 — pkg24 library reconciliation

**Version drift bug found in `lib_bejson_Core_bejson_path_guard.py`:**
The file's header `Version:` field read `1.1.0` while the internal
`VERSION` constant at the bottom of the file read `1.3.0` — two different
version numbers for the same file, in violation of the project's
versioning policy (no file may claim two different version identities).
Root cause not investigated further (predates this session). Fixed by
setting both to `1.4.0` as part of this pass. No functional/security
impact — the traversal-safety fix itself (`Path.relative_to()` boundary
check) was correct and in place in both the header-labeled and
constant-labeled states.

**Cross-family library contamination:**
`lib_bejson_CMS_cms_mfdb.py` (the Experimental CMS's own page/category/
media database manager, `MFDB_CMS_Manager`) was filed under the `CMS`
library family, which is reserved for the separate production BEJSON CMS
product. This meant Experimental_CMS shipped with, and imported from, a
foreign product's namespace. No functional bug resulted (the file worked
correctly), but it created real risk of exactly this kind of confusion —
a future `CMS`-family library update intended for the other product could
have been dropped into this project and silently misapplied, or vice
versa. Relocated to `Lib_PY/ExpCMS/lib_bejson_ExpCMS_cms_mfdb.py`; see
`EXPCMS.py`/`EXPCMS_Builder.py`/library file changelogs (2026-08-08) for
the full change. Two other files in the old `Lib_PY/CMS/` folder
(`lib_bejson_CMS_cms_config.py`, `lib_bejson_CMS_cms_core.py`) were
confirmed unused anywhere in this project (not imported by `EXPCMS.py`,
`EXPCMS_Builder.py`, or any reachable library) and removed along with the
folder.
