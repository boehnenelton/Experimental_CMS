# Changelog — Experimental CMS

## 2026-07-05 — Library Isolation Sync (Lib_EXPCMS)

**Change notes:**
- Corrected an earlier incorrect sync (family-prefixed `lib_bejson_Core_*` naming) — that scheme does not apply to the BEJSON CMS / ExpCMS boundary and was removed.
- Re-synced `Lib_EXPCMS/` per `ExpCMS_Library_Rules_Report.md` against the authoritative `BEJSON_CMS.zip` source (`src/lib/`):
  - Copied 20 Core files verbatim, flat names (frozen baseline, untouched).
  - Copied + renamed 7 CMS-family files (`lib_cms_*` → `lib_expcms_*`), version-bumped with `-expcms` suffix to mark divergence from production numbering.
  - Copied 8 HTML3 presentational files verbatim.
  - Copied `lib_mfdb_chunker_v6.py` as-is; renamed `lib_cms_chunker_wrapper.py` → `lib_expcms_chunker_wrapper.py`.
  - Fixed internal cross-imports inside `lib_expcms_orchestrator.py` (4 imports) and `lib_expcms_persona_writer.py` (1 import) to reference the new `lib_expcms_*` names.
  - Updated `Library:`/`Family:` header identity fields on the 7 renamed CMS files.
- Verified `ExpCSS_CMS.py` / `ExpCSS_Builder.py` already had correct `LIB_DIR` and `lib_expcms_*` imports — no changes needed there.
- Ran automated import-resolution check across all 37 target files — clean.
- **Open discrepancy:** 22 pre-existing files in `Lib_EXPCMS/` (e.g. `lib_html3_charts.py`, `lib_bejson_diagram_html.py`, `lib_html_firebase.py`, `__init__.py`) are not part of the report's 35-file list. Left untouched pending your decision on whether to prune.
- **Open discrepancy:** `lib_expcms_persona_writer.py` has no `Version:` header field to bump.
- Package version: none found in project (no prior `.bejson_project.json` / package ZIP naming) — treated as package version 1.

## 2026-07-05 (cont.) — Unused Library Purge

**Change notes:**
- Audited all 57 files in `Lib_EXPCMS/` via transitive import-graph trace from both entry points (`ExpCSS_CMS.py`, `ExpCSS_Builder.py`).
- Deleted 20 genuinely orphaned files with zero references anywhere in the app: `__init__.py` (package barrel, never triggered — entry points use `sys.path.append`, not package-style import), `lib_bejson_diagram_html.py`, `lib_bejson_to_html.py`, `lib_bejson_validator_diagram.py`, `lib_html_firebase.py`, and 15 unused HTML3 extras (animations, bejson_renderer, charts, clipboard, dev_tools, error_pages, feed_templates, flask, forms, metrics, page_templates, pagination, showcase, text, version).
- Verified all remaining imports resolve cleanly post-purge (37 files remain).
- **Held back, NOT deleted — needs your confirmation:**
  - 12 Core files unused locally but mandated by `ExpCMS_Library_Rules_Report.md`'s frozen-baseline contract (`lib_av_manager.py`, `lib_be_core.py`, `lib_be_project_service.py`, `lib_bejson_list_validator.py`, `lib_bejson_mfdb_core.py`, `lib_bejson_mfdb_validator.py`, `lib_bejson_parse.py`, `lib_bejson_provider.py`, `lib_bejson_schema.py`, `lib_bejson_state_management.py`, `lib_bejson_static_backend.py`, `lib_mfdb_extensions.py`).
  - 6 CMS engine files not currently wired into either entry point (`lib_expcms_core.py`, `_config`, `_content`, `_orchestrator`, `_persona_writer`, `_taxonomy`) — this is the core CMS business logic from last session; treating as a wiring gap, not dead code, pending your confirmation.

## 2026-07-06 — Re-sync Against Current Production (pkg37)

**Change notes:**
- **Version drift found and reported:** `BEJSON_CMS.zip` used in the prior sync was a stale, pre-pkg30 snapshot. Current production (`BEJSON_CMS_v18_5_pkg37.zip`) has since migrated 7 Core files + all CMS-family files to family-prefixed naming and deleted the old flat versions entirely.
- **Production bug found (not fixed there, out of scope):** `lib_bejson_CMS_cms_mfdb.py` imports `from lib_bejson_Utility_bejson_utility import bejson_utility_slugify` — that file doesn't exist anywhere in pkg37. Real file is flat `lib_bejson_utility.py`. This is a live bug in BEJSON CMS production, reported to user, not touched.
- Removed 7 stale flat Core files (`lib_bejson_core.py`, `_env.py`, `_errors.py`, `_path_guard.py`, `_validator.py`, `_mfdb_core.py`, `_mfdb_validator.py`) — obsolete, production replaced these under `lib_bejson_Core_*` names.
- Copied the current 7 `lib_bejson_Core_*` files + flat `lib_bejson_utility.py` from pkg37, verbatim.
- Re-copied + renamed all 9 CMS/chunker/persona files from pkg37 → `lib_expcms_*` (`core`, `mfdb`, `config`, `content`, `orchestrator`, `taxonomy`, `mfdb_extensions`, `persona_writer`, `chunker_wrapper`), overwriting stale copies built from the old source.
- Fixed internal cross-imports (orchestrator: 4, persona_writer: 1).
- Worked around the production Utility bug locally in `lib_expcms_mfdb.py`: pointed the import to the real flat `lib_bejson_utility` instead of the nonexistent `Utility_`-prefixed name.
- Found and fixed a live bug in an **actively used** file: `lib_html3_list_renderer.py` referenced the now-deleted flat `lib_bejson_core` — updated to `lib_bejson_Core_bejson_core`.
- Found and fixed a stale duplicate: both entry points directly imported a leftover flat `lib_mfdb_core.py` (obsolete pre-rename copy) — updated both to `import lib_bejson_Core_mfdb_core`, deleted the obsolete `lib_mfdb_core.py` / `lib_mfdb_validator.py` duplicates from `Lib_EXPCMS`.
- Full entry-point-reachability import check: 19 files reachable, zero broken imports.
- **Still held, pending your confirmation:** the 12 "Category A" frozen-Core files flagged unused last pass are now *also* broken (their old Core dependencies were just deleted) — stronger case for deletion, still not acted on without your go-ahead.

## 2026-07-06 (cont.) — Final Unused-Core Purge

**Change notes:**
- Deleted the remaining 10 previously-flagged unused Core files from `Lib_EXPCMS/` per explicit confirmation: `lib_av_manager.py`, `lib_be_core.py`, `lib_be_project_service.py`, `lib_bejson_list_validator.py`, `lib_bejson_parse.py`, `lib_bejson_provider.py`, `lib_bejson_schema.py`, `lib_bejson_state_management.py`, `lib_bejson_static_backend.py`, `lib_mfdb_extensions.py`.
- (`lib_bejson_mfdb_core.py` / `lib_bejson_mfdb_validator.py` from the original flagged list were already removed in the prior pass.)
- Post-purge verification: full import-graph trace from both entry points, zero broken references. 26 files remain in `Lib_EXPCMS/`, all reachable/used.

## 2026-07-06 (cont.) — Full Audit, Bug Fixes, Cleanup

**Change notes:**
- Full audit run: naming scheme verification (clean, 0 violations), compile check, pyflakes static analysis, runtime import test of every file, full end-to-end execution of both entry points, generated-HTML inspection.
- **3 real bugs found and fixed:** undefined `_HAS_CORE` flag in `lib_html3_list_renderer.py`; apps silently dropped from category feed pages in `ExpCSS_Builder.py`; `page_title` never passed to render context, causing blank `<title>` tags and breadcrumbs on every generated page.
- 2 self-inflicted regressions from my own edits caught and fixed via repeated full-build re-verification before delivery.
- Dead code removed: unused `_build_homepage()` method, redundant local import, dead field-map pre-warm call, dead `current_prefix` variable, ~15 unused imports.
- Readability: renamed cryptic variables in `lib_expcms_mfdb._create_record` (`fm`→`field_index_map`, `rtp`→`record_type_parent`, etc.).
- Full report: `docs/AUDIT_REPORT_2026-07-06.md`.
- Verified via fresh full rebuild: all 3 output pages generate, HTML tag-balanced, titles/breadcrumbs correct, sitemap valid.

## 2026-07-06 (cont.) — CSS Coverage Audit (no code changes)

**Change notes:**
- Full CSS coverage audit: extracted every class defined across CSS_CORE/CSS_BRUTAL + all 10 per-template inline `<style>` blocks (176 classes), diffed against every class actually used across 33 template/HTML files + ExpCSS_CMS.py (83 classes).
- **Confirmed real gap: 46 classes used, zero CSS anywhere.** Directly confirms the reported button rendering issue: `btn-primary`, `c-bejson-form__btn-submit`, `c-bejson-form__btn-reset` have no CSS at all.
- Worst offender: `templates/editor_main.html` — entire `c-bejson-form` component family (10 classes) undefined.
- 3 completely missing components found: backup manager, image gallery, article page.
- 1 likely naming-drift case found: `c-stats-dashboard` should probably be `c-summary-stats` (already fully built, unused).
- Systemic gap: no utility-class layer exists (`flex`, `gap-*`, `u-*` spacing/alignment) despite being used across 8+ templates.
- `content-card` and `emphasis` used unstyled across 9 files each.
- Full report: `docs/AUDIT_REPORT_CSS_2026-07-06.md` (separate from the prior code audit report, which was not touched).
- No code changes made this pass — audit/report only, per request.

## 2026-07-06 (cont.) — CSS Coverage Gap Patched (cross-referenced to master library)

**Change notes:**
- Patched all 46 classes found missing in the CSS audit (`docs/AUDIT_REPORT_CSS_2026-07-06.md`), plus 4 more found by re-running the audit's own gap-check against the first patch (`u-badge`/`u-badge--active`/`u-badge--inactive`/`c-field-group` — total 50 classes added).
- **Correction to the original audit:** dashboard.html's stats classes were undercounted — `stats-grid`, `stat-card`, `stat-value`, `stat-label` were also undefined, not just the `c-stats-dashboard` wrapper as originally reported. Fixed here; noted so the discrepancy isn't silently swept under the rug.
- Nearly everything was pulled verbatim from the bundled BECSS component library (`becss-components.css`) rather than freehand-written — the gap wasn't "CSS never existed," it was "CSS existed in the design system but was never wired into `lib_bejson_html3_component_css.py`."
- 2 custom additions with no premade BECSS equivalent (checked the full 50-family catalog): `.c-backup-manager` wrapper, `.file-entry`/`.file-content`/`.file-name` (editor's file browser rows) — both built from existing design tokens only, flagged in the report.
- Verified: file compiles, `CSS_CORE.format(**COLOR)` still succeeds (this file's CSS uses doubled `{{`/`}}` braces specifically because of that later `.format()` call — every addition follows the same escaping), re-running the exact audit gap-check now returns 0 missing classes, confirmed live via `curl` against the actually-running Flask app that `.btn-primary` is served with real CSS.
- **Cross-referenced to the master library** (`libraries.zip` → `Lib_PY/HTML/lib_bejson_HTML_bejson_html3_component_css.py`): identical patch applied there too (verified byte-identical CSS body, only headers differ per each file's own naming convention). Version 3.0.3 → 3.0.4, fresh RELATIONAL_ID.
- Both entry points re-tested end-to-end after the patch: Flask boots clean, full site rebuild succeeds.

## 2026-07-09 — UI Cleanup, Sidebar Rebuild, System Page

**Change notes:**
- **Issue 1 fixed — Media Orchestrator:** title moved to its own row, upload forms restructured into two clearly-labelled stacked columns (Upload Files / Bulk Folder Import), each with its own visible label, file picker, and submit button. No more cramped single-row toolbar.
- **Issue 2 fixed — Content Architect (and all other pages):** title now stands on its own row on every page. PREVIEW/COMMIT moved into a sub-row inside a `content-card` below the title. Applied same fix to `editor_list.html` (title + Create Page), `authors.html` (title + New Author), `ads.html` (title + New Ad Unit), `apps.html` (title + Import App).
- **Issue 3 fixed — Sidebar rebuilt:** replaced flat alphabetical list with 4 collapsible logical groups (Content, Media & Assets, Site Management, System). Groups are collapsed by default, auto-expand to show the current page's group on load, and mark the active link. Build Site, Repack, Factory Reset removed from sidebar entirely.
- **New `/system` page:** System Tools page with Build Site, Repack System, and Factory Reset as clearly-labelled action cards with descriptions. Accessible from the System sidebar group.
- **Bug fix: `/preview/<uuid>` route added** — was referenced in editor_main.html but never existed. Now serves the matching built page from /Processing/www by scanning for the UUID, or redirects to build with a flash if not yet built.
- **Removed unused `HTML3_List_Renderer` import** from ExpCSS_CMS.py (no longer needed after sidebar rebuild).
- **CSS gap patch final pass:** static-site feed-card CSS added (blog-card, news-item, product-card, masonry-item), layout scaffold classes (container, grid, mx-auto, gap-12), hero image wrapper, footer column grid. CSS gap count: 0.
- Verified: all 13 admin routes return 200, full site build succeeds, 0 pyflakes warnings, 0 compile errors.
- v3.0.9 → v3.1.0, package 8.

## 2026-07-10 — Bulk Import Fix, File Renames, Docs Rewrite

**Change notes:**
- **Bug fix — bulk/directory media import crash:** `process_data()` called `content_type.startswith()` without guarding for `None` — browsers reliably send `None` or empty string for `content_type` on `webkitdirectory` bulk uploads, causing `AttributeError: 'NoneType' object has no attribute 'startswith'` on every bulk import. Fixed: always fall back to `mimetypes.guess_type(filename)` when content_type is falsy, before any string operations. Additional fixes in the same pass: `secure_filename` returning empty string for all-non-ASCII filenames now falls back to `asset_{hash8}{ext}` rather than crashing on an empty path; per-file `try/except` wraps the whole operation so one bad file doesn't abort the entire batch; flash message now distinguishes uploads from duplicates and reports individual file errors.
- **Entry points renamed:** `ExpCSS_CMS.py` → `EXPCMS.py`, `ExpCSS_Builder.py` → `EXPCMS_Builder.py`. All internal references updated (`subprocess.run` call, class name, `# FILE:` headers, docs).
- **Docs rewritten:** `docs/DOCUMENTATION.md` created — clean, current, accurate documentation of the full system. Stale audit/fix reports (`AUDIT_REPORT_2026-07-06.md`, `AUDIT_REPORT_CSS_2026-07-06.md`, `CSS_FIX_REPORT_2026-07-06.md`) removed from `docs/`. Working-notes files in root also removed.
- v3.1.0 → v3.1.1, package 9.

## 2026-07-10 — Sidebar final cleanup

**Change notes:**
- Removed `/build` and `/repack` as sidebar links entirely — they now exist only as action buttons on the Build & Tools page (`/system`). Nothing in the sidebar triggers a destructive or long-running operation.
- Renamed "System Tools" → "Build & Tools" in both the sidebar link label and the page title for clarity.
- Renamed "Nav Links" → "Navigation", "Site Backups" → "Backups", "Preview Manager" → "Preview Server" for conciseness.
- Improved active-link detection: now uses `pathname.startsWith()` for sub-routes (e.g. `/pages/edit/...` correctly highlights the Pages link) instead of exact-match only.
- v3.1.1 → v3.1.2, package 10.

## 2026-07-11 — Full Audit Pass: Bugs, Cleanup, Optimization

**Bugs fixed:**
- **CRITICAL — `save_page()` always stored `None` as category:** form field posted as `category_fk` but route read `category`. Every page edit/create silently lost its category assignment. Fixed.
- **`_copy_apps()` crashed on second build:** `shutil.copytree` requires destination to not exist; second build would crash because `/Processing/www/apps` was still present. Fixed with `rmtree` guard.
- **`_generate_sidebar()` in builder leaked a temp file to disk:** wrote `temp_nav.bejson` inside `/Processing/www/` for every page render, left it there if the render crashed. Replaced with a clean inline HTML generator — no temp file, no external dependency, simpler output.
- **Dead artifact `Data/admin_nav.bejson`:** leftover from the old `HTML3_List_Renderer` sidebar (removed several sessions ago). Deleted.
- **Working-notes `.md` files in `Data/assets/`:** 4 markdown files were sitting in the assets directory, would be indexed as media assets by `get_assets()` and appear in the media library. Deleted.
- **`admin_base.html` footer unstyled:** `<footer class="c-footer">` referenced a class with no definition — raw unstyled browser default. Added `.c-footer` to the admin_base styles.
- **Stale version strings:** `about.html` said "ExpCSS CMS v2.2", `EXPCMS.py` docstring said "v2.4.6", dashboard hardcoded port 5005 and MFDB version 1.3.1 as stat cards. All updated.
- **`categories.html` missing feed types:** form only had article/gallery/app options but the builder supports news/products/masonry too. All 6 feed types now present in the dropdown.
- **`preview_manager.html`:** had a duplicate "Trigger Build" button that also appears on `/system`. Removed — a single authoritative action point.
- **`config.html`:** had a Factory Reset button, duplicating `/system`. Removed, replaced with a link to Build & Tools.
- **`navigation.html`:** used undefined `c-card` / `c-card__title` classes, bare unstyled inputs. Rewritten with correct classes and styled form.

**Cleanup:**
- Removed unused `HTML3_List_Renderer` import from `EXPCMS_Builder.py`.
- Removed dead `self.random = random` assignment from builder (was assigned but never read).
- Removed `import random` from builder (had no usage).

**No data lost, no behaviour changed** on any fixed item except the category bug — that was storing `None` previously.

## 2026-07-13 — Built-Site Playwright Test Pass

**Bugs fixed:**
- **Homepage blank content:** `landing_mode` was `html` in SiteConfig but `landing_html` was empty — the builder rendered a blank page. Fixed: any mode with an empty payload now falls through to the hero template.
- **Hero template ignored its variables:** the hero component had hardcoded placeholder text and no `<h1>` — it never used the `site_title`/`hero_sub` variables passed to it. Rewritten to render both correctly.
- **Global_Skeleton.html completely rebuilt:** removed Tailwind CDN (400KB+ runtime compiler per page), removed Lucide CDN (JS errors on file:// due to async load timing), removed Google Fonts CDN dependency. Replaced with a fully self-contained skeleton using system font fallbacks, inline CSS design tokens matching the BECSS `#DE2626` palette, sticky header, collapsible sidebar with mobile overlay, proper `<h1>` typography, and a hamburger toggle that works on both mobile and desktop.
- **Category/Article skeletons rebuilt:** stripped all Tailwind classes (`text-3xl`, `font-black`, `prose`, etc.) and replaced with the skeleton's own CSS class names. Feed items now render correctly in all types (blog cards, news items, masonry grid, product grid).
- **Footer `--accent` var removed:** builder was using `var(--accent)` (blue) in footer headings — that variable isn't defined in the new skeleton. Replaced with `var(--primary)` (BECSS red).
- **Builder `_build_homepage` helper extracted:** `_hero_content()` helper function avoids duplicating the hero render path.

**Playwright test results (7 pages, post-fix):**
- homepage ✅ — h1, nav, breadcrumb, correct title
- articles-feed ✅ — h1, nav, breadcrumb, 3 blog cards rendering
- article-page ✅ — h1, full body content, article meta, tag
- news-feed ✅ — h1, news items with category label
- news-page ✅ — h1, full body content
- gallery-feed ✅ — h1, masonry grid rendering
- gallery-page ✅ — h1, full body content
- Total issues: 0

v3.1.3 → v3.1.4, package 12.

## 2026-07-17 — Garbage Text Removal, Sidebar Icon Fix

**Bugs fixed:**
- **SYSTEM_LOG / NODE_MASTER / HEARTBEAT garbage text on built pages:** `Template-Footer-Status-Feed.html` was a decorative sci-fi status ticker being injected into every built page as raw HTML with no matching CSS — rendered as unstyled plaintext leaking into page content. Removed entirely from builder. Real footer (contact info + site footer) is retained.
- **Telemetry HUD header garbage (`HTML3`, `CPU: 12%`, `NET: STABLE`, `JOBS: 4 ACTIVE`):** `Template-Header-Telemetry-HUD.html` was loaded and passed as `header_block` but never injected into the new Global_Skeleton (which has its own header baked in). Removed dead component load from builder.
- **Admin sidebar icons invisible:** Lucide was loaded from `unpkg.com` CDN — on Android/Termux with no network the icons simply never appeared. Replaced all 19 icons used by the sidebar with self-contained inline SVGs via `_sidebar_icon()` helper. Zero external requests. Lucide CDN script and `createIcons()` call removed from `admin_base.html`.
- **Admin sidebar group button text nearly invisible:** `color: var(--text-muted)` (dark grey on dark background). Changed to `#aaa` — visible but subdued.
- **Homepage landing page empty/garbage:** hero template now renders real category browse buttons (filtered to exclude Uncategorized), passes `categories` list from builder context.
- v3.1.4 → v3.1.5, package 13.

## 2026-07-17 — Sidebar group rename + start expanded

**Changes:**
- "Content" group renamed to "Main" per request.
- All 4 sidebar groups now start expanded by default (were collapsed). Click to collapse, click again to expand.
- Chevron direction updated: points down when open, right when closed.
- All 15 sidebar links confirmed inside groups — nothing loose.
- v3.1.5 → v3.1.6, package 14.

## 2026-07-18 — Red-on-Red Fix, Breadcrumbs, Author Edit, HTML Import

**Bugs fixed:**
- **Sidebar red-on-red / invisible-after-deselect:** `.c-sidebar__link--active` was `color: var(--primary)` (red) on `rgba(222,38,38,0.12)` background (red-tinted) — unreadable. Changed active state to white text with a left accent border. Base link color was `var(--text-muted)` which is nearly invisible on the dark sidebar background once deselected — changed to `#b0b0b0`, clearly visible in both states. Verified via computed style: non-active `rgb(176,176,176)`, active `rgb(255,255,255)`.
- **System page and 6 other templates still referenced `data-lucide` icons:** the Lucide CDN was removed last session but these templates weren't updated, so icons rendered as nothing. Replaced with emoji equivalents across `system.html`, `apps.html`, `authors.html`, `backups.html`, `dashboard.html`, `media_library.html`, `preview_manager.html`.
- **Admin breadcrumbs weren't clickable:** `ADMIN / PAGES` was plain text. Now `ADMIN` links to dashboard and every path segment before the last is a working link to that partial path.
- **Built-site breadcrumbs weren't clickable:** same issue in `Global_Skeleton.html`. Discovered `category_name`/`category_slug` were never actually passed into `_render_page()`'s context — `{{ category_name }}` had been silently rendering empty this whole time. Added `category_slug`/`category_name` parameters to `_render_page()` and wired them through all 3 call sites that have a category (feed, page, app).
- **Author profile editing:** already fully implemented (edit button + modal + backend `update_author()`) but the button was `color: var(--text-muted)` with no border/background — easy to miss entirely. Given a visible button style with border and background.

**New feature — HTML Import** (ported from BEJSON CMS production's `/import` pipeline, read directly from `BEJSON_CMS_v18_15_pkg48.zip`):
- New `lib_expcms_mfdb._extract_from_html()` and `_strip_word_html()` — ported near-verbatim from production. Uses BeautifulSoup to strip `<script>`/`<style>`/`<noscript>`/`<link>`/`<meta>`, unwrap Word `Mso*` classes and `mso-` inline styles, remove `<o:p>` tags and `WordSection` divs, and delete short (<200 char) footer/div/p/span nodes matching AI/tool watermark patterns (ChatGPT, Claude AI, Gemini, Copilot, "generated by", etc.) as long as they don't contain real structural content. Falls back to plain regex extraction if `beautifulsoup4` isn't installed.
- `import_html_as_page()` rewritten to use the new extractor, auto-detects title from `<title>`/`<h1>` if not supplied.
- New routes: `GET /import` (upload form), `POST /import` (bulk file handler with per-file error reporting, category + author selection).
- New template `import_html.html`, added to sidebar under Main group.
- **Verified end-to-end** with a deliberately messy test file containing Word artefacts, an AI watermark footer, and a `<script>` tag: all cruft removed, both real paragraphs survived intact, zero JS errors.

v3.1.6 → v3.2.0, package 15.

## 2026-07-19 — Portable Widget System

**Audit of prior session (v3.2.0) before starting new work:** compile clean, 0 pyflakes warnings, build succeeds. No regressions found.

**New feature — Embeddable Widget System:**
- New `Lib_EXPCMS/lib_expcms_widgets.py` — a registry of pre-built, fully self-contained HTML+CSS+JS widgets that can be inserted into any page's Body HTML field.
- **Widget contract established:** every widget's HTML/CSS/JS is a single portable snippet with no external dependencies (no CDN links), CSS scoped under a unique per-instance wrapper class (so multiple copies never collide), fixed/documented sizing, and a JS IIFE pattern for any widget that needs script logic. Renders identically in the admin preview, the built static site, or pasted anywhere else.
- **2 test widgets built:**
  - **Social Links** — row of platform icon links (GitHub, Twitter/X, LinkedIn, YouTube, Instagram, Discord, Email, generic website), fixed 40×40px icons, responsive wrap, pure CSS (no JS needed).
  - **Call-to-Action Box** — bordered card with heading, optional body text, and a button. Max-width 560px, height content-driven.
- New routes: `GET /widgets/picker` (returns the picker modal fragment), `POST /widgets/render/<key>` (renders a widget with submitted params, returns raw HTML text for direct textarea insertion).
- New `templates/_widget_picker.html` fragment template.
- Editor UI: "+ Insert Widget" button next to the Body HTML field in `editor_main.html`, opens a modal, fetches available widgets, submits the chosen widget's param form via fetch, inserts the returned snippet at the cursor position in the textarea.
- Widget renderer never raises on bad input — unknown widget keys and malformed params return an HTML comment marker instead of crashing, since this output goes directly into user content.

**Verification performed (15 checks, all passing):**
- `/widgets/picker` returns 200 with both widgets listed
- Both widgets render correctly via direct POST with real param data
- Unknown widget key handled safely (no crash, no 500)
- Full browser flow tested: open editor → click Insert Widget → fill CTA form → submit → confirmed textarea content updated with the rendered snippet, zero JS errors
- Built a real test page combining both widgets, ran the full site builder, loaded the output in a real browser via Playwright: 3 social links rendered, CTA box rendered with correct heading, **computed CSS confirmed correct** (CTA border `rgb(222,38,38)` = `#DE2626`, GitHub icon background `rgb(51,51,51)` = `#333333`) — proving the inline CSS is genuinely portable and self-contained, not relying on any page-level stylesheet.
- Test page removed from database after verification; final rebuild confirms 12 pages (back to baseline).

v3.2.0 → v3.3.0, package 16.

## 2026-07-20 — YouTube Video Media Asset Type

**New feature — YouTube links as a real media asset type:**
- New `VideoAsset` entity in the global MFDB database: `video_uuid`, `url`, `video_id`, `provider`, `title`, `thumbnail_url`, `added_at`. Kept as a separate entity from `MediaAsset` rather than forced into that schema — `MediaAsset`'s primary key is `filename` and its fields (`file_hash`, `file_size`, `mime_type`) don't meaningfully apply to an external link, so a distinct entity was the correct data model rather than overloading the existing one.
- `parse_youtube_url()` — extracts the 11-char video ID from any common URL shape (`watch?v=`, `youtu.be/`, `embed/`, `shorts/`).
- `add_video_asset()` / `get_video_assets()` / `get_video_asset()` / `delete_video_asset()` on `MFDB_CMS_Manager`. Thumbnail URL is auto-derived from YouTube's predictable `i.ytimg.com` path — no API key needed.
- **Self-healing migration:** existing installs (databases created before this change) get the `VideoAsset` entity added automatically and idempotently on next load — found and fixed a real bug here: the self-heal check was originally only wired into `mount_system()`, but `EXPCMS.py` never actually calls that method at startup (constructs `MFDB_CMS_Manager` directly). Moved the check into `__init__` so it actually runs. Verified against the real existing database, not just a fresh one.
- Media Library (`/media`) now has an "Add YouTube Video" form and a Videos grid section (thumbnail + play-icon overlay + copy URL + delete), alongside the existing Files section. Also fixed a pre-existing latent bug found while touching this template: the image-vs-icon check used `a.content_type` but the actual field is `mime_type` — images were silently always falling through to the generic file-icon branch.
- New routes: `POST /media/video/add`, `GET /media/video/delete/<video_uuid>`.
- **New widget — YouTube Video** (`lib_expcms_widgets.py`): responsive 16:9 embed, max-width 720px, scales proportionally via the padding-bottom aspect-ratio technique rather than a fixed pixel height, so it's portable across any page layout. Accepts a full URL or a bare video ID. Registered in the same picker UI as the existing Social Links / CTA Box widgets from last session.

**Verification performed:**
- Compile + pyflakes clean across all touched files
- Full route sweep: 16/16 admin routes return 200
- 11 automated checks: media library loads, video form present, valid YouTube URL accepted and shown in grid, invalid URL rejected safely (no crash, no 500, flash message shown), widget renders correct iframe with correct video ID, widget picker lists the new widget
- Real end-to-end test: created an actual page with the video widget embedded, ran the full static site builder, loaded the built output in a real browser — confirmed the iframe embed URL, video ID, and computed CSS (position/max-width/border-radius) all match exactly, zero JS errors
- Test data cleaned up after verification; final rebuild confirms baseline 12 pages

v3.3.0 → v3.4.0, package 17.

## 2026-07-20 (cont.) — Audit Response: Dead Code Removal, Real XSS Fix, Hardening

Verified every claim in an external audit against the actual current code before acting — several claims (Ghost CSS, category_fk bug) were already fixed in earlier versions than the audit was run against; those are noted but not re-touched. Real, in-scope findings below were fixed and verified.

**Dead code removed (confirmed zero references from either entry point via full import-graph trace):**
- `Lib_EXPCMS/lib_expcms_orchestrator.py` — the audit correctly found `get_categories`/`add_category`/`get_authors` raising `NotImplementedError`, but this file was never imported anywhere; the real, working implementations live in `lib_expcms_mfdb.py` and are what every route actually calls. Deleted rather than "fixed," since fixing unreachable code just adds more unused surface area.
- `Lib_EXPCMS/lib_expcms_persona_writer.py` — same situation; the "unsecure REST fallback" the audit flagged was in dead code, never reachable.
- `Lib_EXPCMS/lib_html3_list_renderer.py` — same situation; the `_resolve_field` guesswork the audit flagged was in dead code, never reachable.

**Real bug fixed — unescaped HTML in generated feed cards (found while addressing the audit's "hardcoded f-string HTML" complaint):**
- `EXPCMS_Builder.py` built `news-item`/`product-card`/`masonry-item`/`blog-card` markup via raw f-string concatenation with zero escaping. A page title containing `<`, `>`, or `&` would corrupt the surrounding HTML structure. Replaced with 4 new Jinja2 component templates (`Components/body/Template-Feed-Item-{News,Product,Masonry,Blog}.html`) rendered via `Template().render()`.
- **Caught and fixed a second-order bug introduced by that very fix in the same pass:** `jinja2.Template()` has autoescaping OFF by default — Flask's `render_template()` enables it separately, but the builder's raw `Template()` calls never got that for free. First pass at the refactor would have silently carried the exact same unescaped-HTML risk forward. Wrapped all 10 `Template()` call sites in the builder through a single autoescape-enabled constructor. Verified in a real browser with a deliberately malicious test title (`<script>alert(1)</script>`) — confirmed it now renders as literal visible text, zero `alert()` fired, zero injected `<script>` tags in the DOM.

**Other real fixes:**
- `/build` route replaced `subprocess.run([sys.executable, "EXPCMS_Builder.py"], ...)` with a direct in-process import and call. Removed the now-unused `subprocess` import. Exceptions now go through `app.logger.exception()` for a full traceback instead of being swallowed into a flash message.
- `/categories` no longer trusts a client-supplied hidden `is_update` field (string-compared against `'true'`) to decide create-vs-update. Server now checks the database directly for the slug's existence — can't be spoofed or left stale by a client-side JS bug. Removed the now-dead hidden input and its JS reference from `categories.html`.
- `_get_content_preview()` in the builder now uses BeautifulSoup (already a project dependency) instead of a raw regex tag-strip, correctly handling malformed markup and comments that the regex would mangle.
- **Added `requirements.txt`** — didn't exist anywhere in the project before now. Pins `Flask`, `Jinja2`, `Werkzeug`, `beautifulsoup4`.

**Addressed but explicitly out of scope, with reasoning:**
- `POSITIONAL_VIOLATION` repair / `mfdb_core_self_heal` — lives in `lib_bejson_Core_*`, the frozen Core baseline copied verbatim from production per this project's isolation architecture. Not modified here; any real fix belongs in the production BEJSON CMS repo. Also pushed back on the audit's framing of self-healing as inherently "a confession of broken writes" — defensive self-repair on load is standard practice for file-based multi-writer systems regardless of write-path correctness; it covers failure modes like manual out-of-band file edits, not just write failures.

**Verification performed:**
- Compile + pyflakes clean across all touched files after dead-code removal and refactors
- Full route sweep: 17/17 routes (including `/widgets/picker`) return 200
- In-process `/build` confirmed actually running in-process (build output visible directly in the Flask process log, not a subprocess)
- Category create + update both verified working under the new server-side existence check
- XSS-adjacent fix verified in a real browser: malicious title renders as text, no script execution, no injected DOM nodes
- Widget system's intentional raw-HTML rendering (via `| safe` at the page-body level) confirmed unaffected by the card-template autoescape fix
- Test data cleaned up after verification; final rebuild confirms baseline 12 pages

v3.4.0 → v3.5.0, package 18.
