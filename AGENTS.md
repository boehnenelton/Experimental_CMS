# AGENTS.md

## Build / Lint / Test / Run

No test suite, linter, or build tool config (`Makefile`, `tox.ini`,
`package.json`, etc.) is present in this repo — none of those commands
exist to run. What's actually here:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the admin app (Flask dev server, port 5005, debug=True)
python3 EXPCMS.py

# Run the static site builder directly
python3 EXPCMS_Builder.py

# Syntax-check a file without running it
python3 -c "import ast; ast.parse(open('EXPCMS.py').read())"
```

## Code Style & Conventions

- **Library naming:** frozen BEJSON/MFDB core files use the
  `lib_bejson_Core_<name>.py` family prefix and are treated as an
  untouched, verbatim baseline — copied from the production BEJSON CMS
  repo, not hand-edited here. This project does not use the `CMS` family
  (that belongs to the separate production BEJSON CMS product) — all
  Experimental-CMS-specific application libraries use the
  `lib_bejson_ExpCMS_<name>.py` prefix under `Lib_PY/ExpCMS/`;
  presentational/HTML3 helpers use `lib_bejson_HTML_<name>.py` under
  `Lib_PY/HTML/`.
- **Entry points import libraries via `sys.path` manipulation**
  (`sys.path.append`/`sys.path.insert`), not package-style
  (`Lib_PY/Core/`, `Lib_PY/HTML/`, `Lib_PY/ExpCMS/` each have
  no `__init__.py`). Don't add one without checking
  every import site still resolves.
- **MFDB primary keys:** every entity's `primary_key` field is declared
  explicitly in its schema (e.g. `Category.primary_key = "category_slug"`,
  `Page.primary_key = "page_uuid"`). Foreign keys follow a `_fk` suffix
  convention (`category_fk`, `author_fk`) and store the *primary key
  value* of the referenced entity, not a raw index.
- **Templates:** every admin template `{% extends "admin_base.html" %}`.
  Component CSS classes use the `c-` prefix (e.g. `c-sidebar__link`,
  `c-bejson-form__input`); utility classes use `u-` (e.g. `u-badge`).
- **Static-site vs. admin theming are two independent token sets.**
  The admin app's CSS (`lib_bejson_HTML_bejson_html3_component_css.py`,
  `lib_bejson_HTML_bejson_html3_skeletons.py`) defines `--bg-page`, `--bg-alt`,
  `--text-main`, etc. The exported static site (`Global_Skeleton.html`)
  defines its own dark-theme tokens (`--bg`, `--surface`, `--text`, etc.)
  with `--bg-page`/`--bg-alt`/`--text-main` aliased onto them so shared
  components (e.g. the BEJSON table/combobox widget) render identically
  in both places. Keep that alias block in sync if the site's token names
  ever change.
- **Widgets are fully portable snippets** (`lib_bejson_ExpCMS_widgets.py`): no
  external CDN dependencies, CSS scoped under a unique per-instance
  wrapper class, any JS wrapped in an IIFE. Follow this contract for any
  new widget so it renders identically in the admin preview, the built
  static site, and if pasted anywhere else.
- **Jinja2 `Template()` calls in the builder must keep autoescaping on**
  (`EXPCMS_Builder.py` wraps all template rendering through a single
  autoescape-enabled constructor) — `jinja2.Template()` has autoescaping
  off by default, unlike Flask's `render_template()`.

## Architectural Rules

- **MFDB databases are permanent** — `Data/workspace/db_*/104a.mfdb.bejson`
  (manifests) and `Data/workspace/db_*/data/*.bejson` (entity files) are
  the actual data store. `Data/global_master.mfdb.zip` /
  `Data/content_master.mfdb.zip` are the archived masters that
  `MFDBArchive.mount()`/`.commit()` sync the workspace against. Never
  delete any of these, regardless of apparent staleness.
- **`.mfdb_lock` files under each workspace db are transient runtime
  state** — written on mount, self-regenerate on the next
  `MFDBArchive.mount()` call. Safe to delete if stale; not part of the
  actual data.
- **Empty foreign keys must fall back to a real default, never be saved
  as `""`.** A page saved with `category_fk=""` matches no `Category`
  record and silently disappears from every feed — always default to
  `'uncategorized'` when a form field comes back blank (see `save_page()`
  and `import_html_as_page()` in `EXPCMS.py`/`lib_bejson_ExpCMS_cms_mfdb.py`).

## Directory Map

| Path | Contents |
|---|---|
| `EXPCMS.py` | Admin Flask app: all routes, sidebar HTML generator, app config, `MFDB_CMS_Manager` instantiation |
| `EXPCMS_Builder.py` | Static site builder: reads the content MFDB, renders `HTML_Skeletons/` + `Components/` into `Processing/www/` |
| `Lib_PY/Core/` | Canonical frozen BEJSON/MFDB core |
| `Lib_PY/HTML/` | Shared component CSS, skeleton tokens, html3 body/table/widget renderers |
| `Lib_PY/ExpCMS/` | `lib_bejson_ExpCMS_cms_mfdb.py` — `MFDB_CMS_Manager`, all CMS data access; widget registry; chunker/archive wrapper |
| `templates/` | Admin app Jinja2 templates (extend `admin_base.html`) |
| `templates/components/backend/` | Reusable admin UI fragments (Data-Table, Form-Row) |
| `Components/` | Jinja2 components injected into the *built static site* (feed item cards, hero section, footer/header — some historically dead, see `docs/cleanup-log.md`) |
| `HTML_Skeletons/` | Page shells for the built static site (`Global_Skeleton.html`, `Article_Skeleton.html`, `Category_Feed_Skeleton.html`) |
| `Data/workspace/db_global/` | Global MFDB: ads, authors, media, nav links, site config, social links, video assets |
| `Data/workspace/db_content/` | Content MFDB: categories, pages, page content, standalone apps |
| `Data/*.mfdb.zip` | Archived MFDB masters (backup/restore target) |
| `docs/` | This documentation set |
