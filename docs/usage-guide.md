# Usage Guide

## Admin App Routes (`EXPCMS.py`, served on `http://127.0.0.1:5005`)

### Dashboard & static content
| Route | Method | Function | What it does |
|---|---|---|---|
| `/` | GET | `dashboard()` | Admin dashboard — stat cards, quick links |
| `/about` | GET | `about()` | About page |
| `/assets/<path:filename>` | GET | `serve_assets(filename)` | Serves files from the assets directory |
| `/landing_editor` | GET/POST | `landing_editor()` | Edit the site's homepage/landing content (hero, mode) |
| `/config` | GET/POST | `config()` | Global `SiteConfig` editor |

### Pages
| Route | Method | Function | What it does |
|---|---|---|---|
| `/pages` | GET | `pages()` | List all pages |
| `/new` | GET | `new_page()` | New page editor form; defaults `category_fk='uncategorized'` |
| `/edit/<uuid>` | GET | `edit_page(uuid)` | Edit an existing page |
| `/save` | POST | `save_page()` | Create/update a page. Form fields: `page_uuid` (blank = create), `title`, `category_fk` (falls back to `'uncategorized'` if blank — see Architectural Rules in `AGENTS.md`), `page_type`, body HTML, `author_fk`, `featured_img` |
| `/pages/delete/<uuid>` | GET | `page_delete(uuid)` | Delete a page |
| `/preview/<uuid>` | GET | `preview_page(uuid)` | Serves the matching built page from `Processing/www/` by scanning for the UUID, or redirects to `/build` with a flash message if not yet built |

### HTML Import
| Route | Method | Function | What it does |
|---|---|---|---|
| `/import` | GET | `import_html_index()` | Bulk HTML/Word import form |
| `/import` | POST | `import_html_submit()` | Per-file import; params: uploaded files, `category` (falls back to `'uncategorized'` if blank), `author_uuid`. Uses BeautifulSoup to strip scripts/styles/Word cruft/AI-tool watermark footers before saving each as a page. Falls back to plain regex extraction if `beautifulsoup4` isn't installed |

### Categories
| Route | Method | Function | What it does |
|---|---|---|---|
| `/categories` | GET/POST | `categories()` | List/create/update categories. `feed_type` options: `article`/`gallery`/`app`/`news`/`products`/`masonry`. Create-vs-update is decided server-side by checking whether the slug already exists (not by a trusted client-supplied flag) |
| `/categories/delete/<slug>` | GET | `category_delete(slug)` | Delete a category |

### Standalone Apps
| Route | Method | Function | What it does |
|---|---|---|---|
| `/apps` | GET/POST | `apps()` | List/import standalone HTML/ZIP apps |
| `/apps/delete/<uuid>` | GET | `app_delete(uuid)` | Delete a standalone app |

### Media Library
| Route | Method | Function | What it does |
|---|---|---|---|
| `/media` | GET | `media_library()` | File + YouTube video grid |
| `/media/upload` | POST | `media_upload()` | Single or bulk (`webkitdirectory`) file upload. Content-type is always resolved via `mimetypes.guess_type(filename)` as a fallback when the browser sends `None`/empty (reliable on bulk directory uploads); non-ASCII filenames that `secure_filename()` empties out fall back to `asset_{hash8}{ext}`; each file is wrapped in its own `try/except` so one bad file doesn't abort the batch |
| `/media/serve/<path:filename>` | GET | `serve_media(filename)` | Serves an uploaded media file |
| `/media/delete/<filename>` | GET | `media_delete(filename)` | Delete an uploaded file |
| `/media/video/add` | POST | `media_video_add()` | Add a YouTube video asset by URL — `parse_youtube_url()` extracts the video ID from any common URL shape (`watch?v=`, `youtu.be/`, `embed/`, `shorts/`); thumbnail is derived from `i.ytimg.com`, no API key needed |
| `/media/video/delete/<video_uuid>` | GET | `media_video_delete(video_uuid)` | Delete a YouTube video asset |

### Widgets
| Route | Method | Function | What it does |
|---|---|---|---|
| `/widgets/picker` | GET | `widgets_picker()` | Returns the widget picker modal fragment |
| `/widgets/render/<widget_key>` | POST | `widgets_render(widget_key)` | Renders one widget with submitted params, returns raw HTML for direct textarea insertion. Never raises on bad input — unknown keys/malformed params return an HTML comment marker |

### Site Management
| Route | Method | Function | What it does |
|---|---|---|---|
| `/navigation` | GET/POST | `navigation()` | Manage nav links |
| `/navigation/delete/<label>` | GET | `navigation_delete(label)` | Delete a nav link |
| `/authors` | GET/POST | `authors()` | Manage author profiles |
| `/authors/delete/<uuid>` | GET | `author_delete(uuid)` | Delete an author |
| `/ads` | GET/POST | `ads()` | Manage ad units |
| `/ads/delete/<uuid>` | GET | `ad_delete(uuid)` | Delete an ad unit |

### System / Build & Tools (`/system`)
| Route | Method | Function | What it does |
|---|---|---|---|
| `/system` | GET | `system_tools()` | Build & Tools page: Build Site, Repack, Factory Reset action cards |
| `/build` | GET | `build_site()` | Runs `EXPCMS_Builder` in-process (not a subprocess) and writes `Processing/www/`. Exceptions go through `app.logger.exception()` |
| `/repack` | GET | `repack_system()` | Re-archives the MFDB workspace into `global_master.mfdb.zip` / `content_master.mfdb.zip` |
| `/factory_reset` | GET | `reset_system()` | Resets the MFDB workspace |
| `/preview_srv` | GET | `preview_manager()` | Preview server control page |
| `/srv/start` | GET | `srv_start()` | Starts the static-site preview server |
| `/srv/stop` | GET | `srv_stop()` | Stops the static-site preview server |

### Backups
| Route | Method | Function | What it does |
|---|---|---|---|
| `/backups` | GET | `backups()` | Backup list/management page |
| `/backup/create` | POST | `backup_create()` | Chunks the MFDB workspace into a portable archive |
| `/backup/restore` | POST | `backup_restore()` | Restores from a chunked archive |
| `/backup/download/<filename>` | GET | `backup_download(filename)` | Downloads a backup file |

## CLI Entry Points

### `python3 EXPCMS.py`
Starts the Flask dev server: `app.run(host='0.0.0.0', port=5005, debug=True)`.

### `python3 EXPCMS_Builder.py`
Runs the static site builder directly, independent of the admin app:
```python
builder = EXPCMS_Builder(
    data_root=os.path.join(BASE_DIR, "Data"),
    skel_dir=os.path.join(BASE_DIR, "HTML_Skeletons"),
    output_dir=os.path.join(BASE_DIR, "Processing", "www"),
)
builder.build_site()
```

## Key Public Functions (`Lib_PY/ExpCMS/lib_bejson_ExpCMS_cms_mfdb.py` — `MFDB_CMS_Manager`)

| Function | Params | What it does |
|---|---|---|
| `get_pages_in_category(category_slug)` | category slug | Returns all `Page` records whose `category_fk` matches exactly |
| `create_page(...)` / `update_page(...)` | page fields | Write a `Page` entity record |
| `import_html_as_page(file_path, title='', category='', author_uuid='')` | file path + metadata | Extracts and cleans HTML (BeautifulSoup), defaults `category` to `'uncategorized'` if blank, saves as a page |
| `parse_youtube_url(url)` | any YouTube URL shape | Returns the 11-char video ID |
| `add_video_asset(...)` / `get_video_assets()` / `get_video_asset(uuid)` / `delete_video_asset(uuid)` | — | `VideoAsset` entity CRUD |

## Production Deployment Security

When deploying Experimental CMS to a production environment, you **must** set the `EXPCMS_SECRET_KEY` environment variable.

If this variable is not set, the application will fallback to generating a random per-process secret key. While this is secure against hardcoded key attacks, it means that any user sessions (and session cookies) will become invalid and log users out every time the application process is restarted. Setting a strong, persistent `EXPCMS_SECRET_KEY` is required for reliable operational security and user experience.
