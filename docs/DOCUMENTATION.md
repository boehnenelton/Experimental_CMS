# Experimental CMS — Documentation

**Version:** 3.1.0  
**Author:** Elton Boehnen  
**Contact:** eltonboehnen@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton  
**Updated:** 2026-07-09

---

## What This Is

Experimental CMS (ExpCMS) is a Flask-based, BEJSON-powered static site engine and admin dashboard. It manages content through a two-tier MFDB (Multi-File Database) architecture and compiles it into a deployable HTML site.

It is an isolated sandbox — intentionally separated from the production BEJSON CMS. Changes to ExpCMS never touch production. The production library is the source of truth; ExpCMS consumes frozen copies.

---

## Running It

```bash
# Start the admin dashboard
python3 EXPCMS.py
# → http://0.0.0.0:5005
```

```bash
# Build the static site (can also be triggered from System Tools in the admin)
python3 EXPCMS_Builder.py
# → output at Processing/www/
```

Both scripts self-locate via `Path(__file__)` and inject `Lib_EXPCMS` into `sys.path` at startup. No hardcoded paths, no manual config required.

---

## Project Structure

```
EXPCMS.py             Main Flask admin app (v3.1.0)
EXPCMS_Builder.py         Static site compiler (v3.0.4)

Data/
  workspace/
    db_global/            Global MFDB (site config, media, nav, authors, ads)
      104a.mfdb.bejson    Global manifest
      data/               Entity files
    db_content/           Content MFDB (pages, categories, apps)
      104a.mfdb.bejson    Content manifest
      data/               Entity files
  content_master.mfdb.zip Last known-good content backup
  global_master.mfdb.zip  Last known-good global backup

Lib_EXPCMS/               Isolated library directory (see Library Architecture)
templates/                Jinja2 admin UI templates
HTML_Skeletons/           Static site page templates (Jinja2)
Components/               Reusable HTML component fragments
Processing/www/           Built static site output (generated, not committed)
storage/                  Chunker backups

docs/
  DOCUMENTATION.md        This file
  changelog.md            Full change history
```

---

## MFDB Database Schema

ExpCMS uses two MFDB databases. Each has a manifest (`104a.mfdb.bejson`) pointing to flat entity files (`104`-format BEJSON).

### Global Database (`db_global/`)

Stores site-wide data shared across all content.

| Entity | File | Purpose |
|---|---|---|
| `SiteConfig` | `siteconfig.bejson` | Key/value site settings (title, tagline, landing mode, etc.) |
| `NavLink` | `navlink.bejson` | Navigation menu items |
| `SocialLink` | `sociallink.bejson` | Social profile links |
| `AuthorProfile` | `authorprofile.bejson` | Author bio records |
| `AdUnit` | `adunit.bejson` | Ad rotation units |
| `MediaAsset` | `mediaasset.bejson` | SHA-256-indexed media file registry |
| `VideoAsset` | `videoasset.bejson` | External video links (YouTube) for embedding into pages |

### Content Database (`db_content/`)

Stores all publishable content.

| Entity | File | Purpose |
|---|---|---|
| `Category` | `category.bejson` | Content categories with feed type |
| `Page` | `page.bejson` | Individual content pages |
| `PageContent` | `pagecontent.bejson` | Extended HTML body content blocks |
| `StandaloneApp` | `standaloneapp.bejson` | Embedded app entries |

### Category Feed Types

Categories define how their content renders in the built site:

| Feed Type | Card Style |
|---|---|
| `article` | Blog cards (thumbnail + excerpt) |
| `news` | News items (thumbnail + category tag + excerpt) |
| `product` | Product grid (image + title + CTA button) |
| `masonry` | Masonry grid (image with hover overlay) |
| `gallery` | Image gallery |
| `app` | Standalone app hub |

---

## Admin Routes

All routes are served by `EXPCMS.py` on port `5005`.

### Content

| Route | Method | Description |
|---|---|---|
| `/` | GET | Dashboard — entity counts and quick-action cards |
| `/pages` | GET | Indexed page list |
| `/new` | GET | New page editor |
| `/edit/<uuid>` | GET | Edit existing page by UUID |
| `/save` | POST | Save page (create or update) |
| `/pages/delete/<uuid>` | GET | Delete page |
| `/categories` | GET/POST | Category management |
| `/categories/delete/<slug>` | GET | Delete category |
| `/landing_editor` | GET/POST | Configure homepage landing mode |

### Media & Assets

| Route | Method | Description |
|---|---|---|
| `/media` | GET | Media library grid |
| `/media/upload` | POST | Upload files (single or bulk folder) |
| `/media/serve/<path>` | GET | Serve a media asset |
| `/media/delete/<filename>` | GET | Delete a media asset |
| `/apps` | GET/POST | Standalone app management |
| `/apps/delete/<uuid>` | GET | Delete an app |

### Site Management

| Route | Method | Description |
|---|---|---|
| `/navigation` | GET/POST | Nav link management |
| `/navigation/delete/<label>` | GET | Delete a nav link |
| `/authors` | GET/POST | Author profile management |
| `/authors/delete/<uuid>` | GET | Delete an author |
| `/ads` | GET/POST | Ad unit management |
| `/ads/delete/<uuid>` | GET | Delete an ad unit |

### System

| Route | Method | Description |
|---|---|---|
| `/config` | GET/POST | Global key/value configuration |
| `/system` | GET | System Tools page (build, repack, factory reset) |
| `/build` | GET | Triggers full static site build |
| `/repack` | GET | Re-indexes MFDB entity files and reconciles manifests |
| `/factory_reset` | GET | Wipes all MFDB content and reinitializes |
| `/preview/<uuid>` | GET | Preview a specific built page by UUID |
| `/preview_srv` | GET | Preview server manager |
| `/srv/start` | GET | Start the built-site preview HTTP server |
| `/srv/stop` | GET | Stop the preview server |
| `/backups` | GET | Site backup manager |
| `/backup/create` | POST | Create a new MFDB-compliant zip backup |
| `/backup/restore` | POST | Restore from a backup (wipes current `/www`) |
| `/backup/download/<filename>` | GET | Download a backup file |
| `/about` | GET | About / system info page |
| `/assets/<path>` | GET | Serve static admin assets |

---

## Admin UI

The admin UI is built with the BECSS design system (white/black/`#DE2626` palette, Inter + Source Code Pro fonts, mobile-first). All pages extend `admin_base.html`.

### Sidebar

The sidebar is organized into four collapsible groups, collapsed by default. The current page's group auto-expands on load.

| Group | Pages |
|---|---|
| **Content** | Dashboard, Pages, New Page, Categories, Landing Page |
| **Media & Assets** | Media Library, Standalone Apps |
| **Site Management** | Navigation, Authors, Ad Rotator |
| **System** | Global Config, Backups, Preview Server, Build & Tools, About |

Build Site, Repack, and Factory Reset have no sidebar links. They exist only as action buttons on the **Build & Tools** page (`/system`) to prevent accidental triggering from navigation.

### CSS Architecture

All admin CSS is served from a single `context_processor` that injects `becss_css` globally via Jinja2's template inheritance. The CSS is built at request time from:

```
lib_bejson_html3_component_css.py   Component registry (COMPONENT_CSS string)
    ↓ imported by
lib_bejson_html3_skeletons.py       Assembles CSS_CORE and CSS_BRUTAL
    ↓ injected by
EXPCMS.py (@context_processor)  Renders CSS_CORE.format(**COLOR) → becss_css
    ↓ received by
admin_base.html                     {{ becss_css | safe }} in <style> tag
    ↓ inherited by
all templates
```

Individual templates may also include their own `<style>` blocks for page-specific overrides.

---

## Static Site Builder

`EXPCMS_Builder.py` compiles MFDB content into a fully static HTML site.

### Build output (`Processing/www/`)

```
index.html              Homepage (hero or custom landing depending on SiteConfig)
sitemap.xml             Auto-generated sitemap
<category_slug>/
  index.html            Category feed page (blog/news/product/masonry cards)
  <page_slug>/
    index.html          Individual content page
```

### Build process

1. Loads `SiteConfig` from the global database
2. Generates the homepage (hero image or custom landing HTML from `SiteConfig`)
3. For each `Category`: renders a feed page using the category's `feed_type`
4. For each `Page` in the category: renders an individual article/content page
5. For each `StandaloneApp` in the category: renders an iframe-wrapped app page
6. Generates `sitemap.xml` from all built URLs

### Site templates

| Template | Used for |
|---|---|
| `HTML_Skeletons/Global_Skeleton.html` | Wrapper for all pages (header, sidebar, nav, footer) |
| `HTML_Skeletons/Category_Feed_Skeleton.html` | Category index feed |
| `HTML_Skeletons/Article_Skeleton.html` | Individual page / article |
| `Components/body/Template-Standard-Hero-Section-body-component.html` | Homepage hero |
| `Components/footers/Template-Footer-Status-Feed.html` | Footer |
| `Components/headers/Template-Header-Telemetry-HUD.html` | Header |

---

## Library Architecture

ExpCMS uses a physically isolated library directory (`Lib_EXPCMS/`) that never shares files with the production BEJSON CMS. This eliminates the naming collision problem that existed in earlier versions.

### Library layers in `Lib_EXPCMS/`

**Frozen Core (`lib_bejson_Core_*`)** — verbatim copies from production, never modified here. Updates flow downstream from production only.

| File | Version | Role |
|---|---|---|
| `lib_bejson_Core_bejson_core.py` | 2.x | Atomic I/O, field map, BEJSON primitives |
| `lib_bejson_Core_bejson_env.py` | 2.x | Path resolution |
| `lib_bejson_Core_bejson_errors.py` | 2.x | Error codes and exception classes |
| `lib_bejson_Core_bejson_path_guard.py` | 1.2 | Path traversal security guard |
| `lib_bejson_Core_bejson_validator.py` | 2.x | Structural BEJSON validation |
| `lib_bejson_Core_mfdb_core.py` | 2.x | MFDB manifest/entity orchestrator |
| `lib_bejson_Core_mfdb_validator.py` | 2.x | Bidirectional MFDB validation |

**Utility (flat, per production convention)**

| File | Role |
|---|---|
| `lib_bejson_utility.py` | Slugify, general BEJSON utilities |

**HTML3 Presentational (verbatim, never modified)**

| File | Role |
|---|---|
| `lib_bejson_html3_component_css.py` | BECSS component registry |
| `lib_bejson_html3_skeletons.py` | CSS_CORE/CSS_BRUTAL assembly + COLOR tokens |
| `lib_html3_app_layout.py` | App layout renderer |
| `lib_html3_body.py` | Body content renderer |
| `lib_html3_sidemenu.py` | Sidebar HTML utilities |
| `lib_html3_tables.py` | Table renderer |
| `lib_html3_widgets.py` | Widget components |

**ExpCMS-Owned CMS Layer (`lib_expcms_*`)** — renamed copies of production CMS libs. These are free to diverge; they will never collide with production's `lib_bejson_CMS_*` or `lib_cms_*` names.

| File | Version | Role |
|---|---|---|
| `lib_expcms_core.py` | 18.0.1-expcms | Primary CMS engine |
| `lib_expcms_mfdb.py` | 2.0.5-expcms | MFDB CRUD operations layer |
| `lib_expcms_config.py` | 2.0.2-expcms | Config key/value management |
| `lib_expcms_content.py` | 2.1.1-expcms | Content handler |
| `lib_expcms_taxonomy.py` | 2.0.2-expcms | Tag and category manager |
| `lib_expcms_mfdb_extensions.py` | 2.0.x | MFDB join/aggregation extensions |
| `lib_expcms_chunker_wrapper.py` | — | MFDB chunker integration |

**Widget System**

| File | Role |
|---|---|
| `lib_expcms_widgets.py` | Registry of pre-built, self-contained embeddable widgets (Social Links, Call-to-Action Box, YouTube Video). Each widget's HTML/CSS/JS is a single portable snippet, scoped per-instance, zero external dependencies. |

**MFDB Chunker**

| File | Role |
|---|---|
| `lib_mfdb_chunker_v6.py` | Core MFDB zip/chunk packaging engine |

### The isolation rule

> Core libraries are never modified in this sandbox. If something is missing from Core, add it in a `lib_expcms_*` file. If an ExpCMS file needs to diverge from its production counterpart, it already has — under the `lib_expcms_` prefix.

---

## Development Policy

Elton's standard dev policy applies. Key points relevant to this project:

- Every file must have a header with `SCRIPT_NAME`, `VERSION`, `DATE`, `RELATIONAL_ID`
- `RELATIONAL_ID` must be a fresh UUID on every modification — even a one-line change
- Package version bumps before every delivery (`bejson_project.json` + ZIP filename)
- Atomic file writes for all MFDB operations
- No hardcoded paths — all paths resolve from `Path(__file__)`
- Mobile-first layouts, hamburger navigation, BECSS palette only
- No `render_template_string` — always `render_template`
- Never modify Core libraries; refactor app code instead

---

## Known Limitations

- The preview server (`/srv/start`) runs as a daemon thread — it does not survive a CMS restart.
- `/preview/<uuid>` scans the built HTML directory for a matching UUID. If the site hasn't been built yet, it redirects to the build trigger.
- Dead code removed 2026-07-20: `lib_expcms_orchestrator.py`, `lib_expcms_persona_writer.py`, `lib_html3_list_renderer.py` were shipped but never imported by either entry point. All working category/author/page logic lives in `lib_expcms_mfdb.py`.
- `SiteConfig` landing mode `image` requires an asset to be uploaded to the media library and its filename set in `SiteConfig.landing_image` — there is no UI picker for this yet; it must be set via the Config page.

---

*Elton Boehnen · eltonboehnen@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton*
