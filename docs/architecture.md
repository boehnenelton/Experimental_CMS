# Architecture

## Components

### Admin app — `EXPCMS.py`
Single-file Flask app. Instantiates one `MFDB_CMS_Manager` (`cms`) at
module load against `DATA_ROOT = Data/`, and one `EXPCMS_Builder`
per `/build` request. Owns all 39 routes: dashboard, page/category/author/
app/ad/nav CRUD, media (file + YouTube video), HTML import, widget
picker/renderer, backups, preview server control, and system tools
(build/repack/factory-reset). Also generates the sidebar HTML directly
(`get_sidebar_html()`) rather than delegating to `lib_html3_sidemenu.py`
(that file is unused — see `docs/cleanup-log.md`).

### Static site builder — `EXPCMS_Builder.py`
`EXPCMS_Builder(data_root, skel_dir, output_dir)`. `build_site()`:
1. Loads `Category` and other entities directly via
   `MFDBCore.mfdb_core_load_entity()`.
2. Renders the homepage (`_hero_content()` / `_build_homepage` path).
3. For each category, calls `_build_category()`, which pulls matching
   pages via `cms.get_pages_in_category(category_slug)`, renders each
   into a feed-item card (`Components/body/Template-Feed-Item-*.html`,
   chosen by the category's `feed_type`), and wraps the result in
   `HTML_Skeletons/Category_Feed_Skeleton.html`.
4. Renders individual pages via `HTML_Skeletons/Article_Skeleton.html`.
5. Renders standalone apps (`_copy_apps()`).
6. Writes `sitemap.xml`.

All page rendering funnels through one shared `_render_page(page_context)`
→ `Template(self.global_skel).render(page_context)`, so every generated
page gets the same context keys (`sidebar_block`, `related_block`,
`page_title`, `category_slug`, `category_name`,
`shared_component_css` — see below).

### `Lib_PY/ExpCMS/lib_bejson_ExpCMS_cms_mfdb.py` — `MFDB_CMS_Manager`
The single data-access layer for the whole CMS. Wraps two MFDB
databases (`global_manifest`, `content_manifest`) and exposes typed
CRUD methods per entity (`get_pages_in_category`, `create_page`,
`update_page`, `import_html_as_page`, `add_video_asset`,
`parse_youtube_url`, backup/restore via `MFDBArchive`, etc.). Every
route in `EXPCMS.py` and every read in `EXPCMS_Builder.py` goes through
this class — there is no direct file I/O against the `.bejson` entity
files anywhere else in the app.

### `Lib_PY/Core/lib_bejson_Core_*.py` — canonical frozen BEJSON/MFDB core
Copied verbatim from the production BEJSON CMS repo, kept in its own
`Core` family folder rather than duplicated per-app (as of the 2026-07-31
library push — see `CHANGELOG.md`; previously frozen isolation copies
lived under the retired `Lib_EXPCMS/`). Implements the BEJSON 104/104a
parser/validator, MFDB manifest + entity file I/O, path guarding, and
error types. Never hand-edited here; any real fix belongs upstream.

### `Lib_PY/HTML/lib_bejson_HTML_bejson_html3_component_css.py` /
### `lib_bejson_HTML_bejson_html3_skeletons.py`
Shared CSS component library (`COMPONENT_CSS`) and page-skeleton token
templates (`CSS_CORE_SKELETON`), used to build the admin app's
`becss_css` (`CSS_CORE.format(**COLOR)` in `EXPCMS.py`). Since 2026-07-30,
`EXPCMS_Builder.py` also imports the raw `COMPONENT_CSS` string directly
(de-escaping its doubled `{{`/`}}` braces, since it's normally consumed
through a later `.format()` call) and injects it into every built page
via the `shared_component_css` template variable — this makes components
embedded in page content (e.g. the BEJSON table/combobox widget from
`lib_bejson_HTML_html3_tables.py`) render identically on the live static site as they
do in the admin editor, instead of only in the admin editor.

### `Lib_PY/ExpCMS/lib_bejson_ExpCMS_widgets.py`
Registry of portable, self-contained widgets (Social Links, Call-to-Action
Box, YouTube Video) insertable into any page's body HTML via the widget
picker (`templates/_widget_picker.html`, `/widgets/picker`,
`/widgets/render/<key>`). Each widget's HTML/CSS/JS has zero external
dependencies and CSS scoped under a unique per-instance wrapper class.

### `Lib_PY/ExpCMS/lib_bejson_ExpCMS_chunker_wrapper.py` / `lib_bejson_ExpCMS_mfdb_chunker_v6.py`
Archive/restore engine used by the Backups page (`/backup/create`,
`/backup/restore`) to chunk the MFDB workspace into portable archives.

## Data Flow

```
Admin UI (templates/*.html)
        │  form POST
        ▼
EXPCMS.py routes
        │  cms.<method>()
        ▼
MFDB_CMS_Manager (lib_bejson_ExpCMS_cms_mfdb.py)
        │  reads/writes
        ▼
Data/workspace/db_{global,content}/104a.mfdb.bejson (manifest)
Data/workspace/db_{global,content}/data/*.bejson (entity files)
        │  MFDBArchive.commit() on /repack
        ▼
Data/{global,content}_master.mfdb.zip (archived masters)
```

```
/build route (or `python3 EXPCMS_Builder.py` directly)
        │
        ▼
EXPCMS_Builder.build_site()
        │  MFDBCore.mfdb_core_load_entity() + cms.get_pages_in_category()
        ▼
HTML_Skeletons/*.html + Components/body/Template-Feed-Item-*.html
        │  Template(...).render(page_context)
        ▼
Processing/www/  (static site output, incl. sitemap.xml)
```

Category feed pages depend on every `Page.category_fk` matching a real
`Category.category_slug` exactly — a blank or mismatched `category_fk`
silently drops that page from every feed with no error surfaced anywhere
in the UI. `save_page()` and `import_html_as_page()` both default a blank
category to `'uncategorized'` to guard against this.
