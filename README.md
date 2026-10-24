# Experimental CMS (ExpCMS)

A Flask + MFDB (BEJSON multi-file database) content management system with
a static-site builder. The admin app (`EXPCMS.py`) manages pages, categories,
authors, apps, ads, navigation, and media; `EXPCMS_Builder.py` renders the
managed content into a fully static, self-contained HTML site with no
external CDN dependencies.

## Features

- **Page/content editor** — title, category, author, body HTML, with an
  embeddable widget picker (Social Links, Call-to-Action Box, YouTube Video)
  for inserting portable, self-contained snippets into page content.
- **HTML Import** — bulk-imports existing HTML/Word documents as pages,
  stripping Word cruft, scripts, and AI-tool watermark footers via
  BeautifulSoup.
- **Category feeds** — six feed layouts (blog, news, products, masonry,
  gallery, app) rendered from `HTML_Skeletons/Category_Feed_Skeleton.html`.
- **Standalone App hosting** — import and serve arbitrary HTML/ZIP apps
  under `/apps`.
- **Media Library** — file uploads (single + bulk directory import) and
  YouTube video assets (auto-derived thumbnails, no API key required).
- **Static site builder** — generates a complete static site (with
  sitemap.xml) from the MFDB content database into `Processing/www/`.
- **Preview server**, **backup/restore** (zips the MFDB masters), and a
  **Build & Tools** system page for triggering builds/repacks.
- **MFDB persistence** — all structured data lives in BEJSON 104/104a
  manifest + entity files under `Data/workspace/`, archived to
  `Data/global_master.mfdb.zip` / `Data/content_master.mfdb.zip`.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.10+.

## Usage

Run the admin app (serves on port 5005):

```bash
python3 EXPCMS.py
```

Then open `http://127.0.0.1:5005/` for the admin dashboard.

Build the static site directly (writes to `Processing/www/`), without going
through the admin UI's `/build` route:

```bash
python3 EXPCMS_Builder.py
```

The admin app's **Build & Tools** page (`/system`) exposes the same build
step, plus **Repack** (re-archives the MFDB workspace into the two master
`.zip` files) and **Factory Reset**.

## Project Structure

```
EXPCMS.py                    Admin Flask app — all routes, sidebar, config
EXPCMS_Builder.py             Static site generator (reads MFDB, writes Processing/www/)
Lib_PY/Core/                  Canonical frozen BEJSON/MFDB core (bejson_core, mfdb_core, path_guard, validators, errors)
Lib_PY/HTML/                  lib_bejson_HTML_*.py — shared component CSS, skeleton tokens, html3 body/table/widget renderers
Lib_PY/ExpCMS/                lib_bejson_ExpCMS_cms_mfdb.py — MFDB_CMS_Manager, all CMS data access (pages, categories, media, etc.)
                               lib_bejson_ExpCMS_widgets.py — embeddable widget registry (Social Links, CTA, YouTube)
                               lib_bejson_ExpCMS_chunker_wrapper.py / lib_bejson_ExpCMS_mfdb_chunker_v6.py — archive/restore
templates/                    Jinja2 templates for the admin app
Components/                   Jinja2 components injected into built static pages
HTML_Skeletons/                Global/Article/Category page skeletons for the built site
Data/                         MFDB workspace + archived master databases (never delete)
docs/                         Project documentation (this doc set)
```

## License

This project is licensed under PolyForm Noncommercial 1.0.0 — free for
personal, educational, research, and non-commercial use. Commercial use
requires a separate agreement with the copyright holder. See `LICENSE`.
