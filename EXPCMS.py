# RELATIONAL_GUID: 26838dbe-6b80-4528-afd4-4afa0ce31c09
# VERSION: v3.11.0
# CREDITS: Elton Boehnen (github.com/boehnenelton)
# FILE: EXPCMS.py
# DATE: 2026-08-18
# CHANGE (2026-08-18): pkg29 audit-fix pass, Phase 1 (security). NEW-H2:
#   preview server (/srv/start) was hardcoded to bind "" (0.0.0.0) - H1
#   (pkg25) locked the admin app to loopback but missed this one, which
#   serves the built site + hosted apps with no auth. Now env-driven via
#   EXPCMS_PREVIEW_HOST, loopback default, warns loudly if overridden.
#   NEW-H3: /apps zip-import entry_file was accepted from the form with
#   no validation against the zip's actual contents, then interpolated
#   raw into an unescaped iframe src on every built app page (fixed on
#   the builder side too, see EXPCMS_Builder.py changelog). Now run
#   through secure_filename() and required to exist in the extracted
#   zip, or the import is rejected.
# CHANGE (2026-08-18): pkg28 audit-fix pass, Phase 0 (NEW-C1 regression
#   fix). preview_page()'s page_data.get("page_slug") or ...get("slug")
#   fallback removed - "page_slug" was never a real field, it only
#   existed because of the same M6 bug fixed in
#   lib_bejson_ExpCMS_cms_mfdb.py this pass. Now reads "slug" directly.
# CHANGE (2026-08-12): pkg27 audit-fix pass, part 3 (L1-L14 from the full
#   audit, all now addressed except L12/L13 which the audit itself flagged
#   as informational-only, no fix needed). L1: hardcoded Flask secret_key
#   replaced with env-var/random fallback. L2: malformed source_files_json
#   now flashes an error instead of a raw 500. L3: zip-import folder
#   labels sanitized. L4: /preview/<uuid> computes its built path directly
#   instead of scanning every built HTML file per request. L5:
#   static_folder no longer points at templates/ (was serving raw Jinja
#   source at /static/*.html). L6: removed the dead /assets/<path> route.
#   L7: hardcoded stale "v3.1" strings replaced with a live
#   expcms_version pulled from .bejson_project.json. L11:
#   categories()/pages() now resolve entity file paths via the manifest
#   instead of hardcoded 'data/category.bejson'/'data/page.bejson'.
#   See EXPCMS_Builder.py changelog for L8/L9/L10.
# CHANGE (2026-08-12): pkg26 audit-fix pass, part 2 (M2-M9 from the full
#   audit; C1/C2/H1-H6/M1 were pkg25). M2: backup/restore now target the
#   real MFDB workspace instead of the built site (see chunker_wrapper.py
#   changelog); /backup/restore now re-mounts and rebuilds automatically
#   on success. M4: factory_reset and repack converted to POST-only routes
#   with form-submit buttons (was GET links, CSRF-triggerable via <img>).
#   See templates/*.html and lib_bejson_ExpCMS_cms_mfdb.py changelogs for
#   M3/M6/M7/M8/M9/M4 (other 8 routes)/H2-followup-original_name fixes.
# CHANGE (2026-08-11): pkg25 audit-fix pass (see docs/security-notes.md
#   for the full audit trace). C1: /apps zip import now routes through
#   safe_extract_zip (per-member bejson_safe_join check) plus a member
#   count/size guard, instead of raw zipfile.extractall(). H1: app.run()
#   now defaults to 127.0.0.1 with debug off; host/port/debug are
#   env-driven (EXPCMS_HOST/EXPCMS_PORT/EXPCMS_DEBUG). H3: /apps route
#   reads request.form.get('category') to match the actual form field
#   name (was reading 'category_fk', always None).
# CHANGE (2026-08-08): pkg24 library reconciliation against updated
#   libraries.zip. Dropped "CMS" from the Lib_PY family sys.path list and
#   switched the MFDB_CMS_Manager import from lib_bejson_CMS_cms_mfdb (CMS
#   family - belongs to a different CMS product) to lib_bejson_ExpCMS_cms_mfdb
#   (ExpCMS family - relocated file, same class/logic). Experimental CMS no
#   longer depends on the CMS family at all.
# CHANGE (2026-08-05): pkg23 database audit. Removed the separate
#   cms.initialize_system() call before mount_system() at startup -
#   mount_system() now needs to see whether the manifest existed BEFORE
#   it ran, to tell a true fresh install apart from live data. Calling
#   both in sequence made every boot look like "live data already
#   exists," which (combined with the pkg21 mount_system() rewrite)
#   silently skipped creating the initial backup archive on fresh
#   installs. mount_system() calls initialize_system() internally at
#   the correct point now - see lib_bejson_CMS_cms_mfdb.py.

"""
Experimental CMS v3.1 — Unified Administrative Dashboard
Description: Flask-based admin dashboard and MFDB content manager for the ExpCMS static site engine.
             Built on the canonical Lib_PY family libraries (Core, HTML, ExpCMS),
             replacing the retired Lib_EXPCMS frozen isolation copies as of 2026-07-31.
"""
import os
import sys
import uuid
import shutil
import collections
import threading
import http.server
import socketserver
import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Add Lib to path — migrated off the frozen Lib_EXPCMS isolation copies onto
# the canonical Lib_PY family folders per APP_LIBRARY_PUSH_LIST.md (2026-07-31)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PY_DIR = os.path.join(BASE_DIR, "Lib_PY")
for _family in ("Core", "HTML", "ExpCMS"):
    _family_dir = os.path.join(LIB_PY_DIR, _family)
    if _family_dir not in sys.path:
        sys.path.append(_family_dir)

from lib_bejson_ExpCMS_cms_mfdb import MFDB_CMS_Manager
from lib_bejson_ExpCMS_widgets import WIDGETS, render_widget
from lib_bejson_ExpCMS_html import COLOR, CSS_CORE
from lib_bejson_ExpCMS_html import html_card, html_stats_bar, html_code_box, html_brutal_table
from lib_bejson_ExpCMS_html import html_table
from lib_bejson_ExpCMS_html import html_widget, html_info_box
from lib_bejson_ExpCMS_chunker_wrapper import CMS_Chunker_Wrapper
from lib_bejson_ExpCMS_mfdb_chunker_v6 import safe_extract_zip
import lib_bejson_Core_mfdb_core as MFDBCore

# --- Flask App Initialization ---
import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

app = Flask(__name__,
            # BUGFIX (2026-08-12, audit L5): this pointed static_folder
            # directly at templates/, so every raw .html template (Jinja
            # source, admin-only markup/logic) was servable verbatim at
            # /static/<name>.html - nothing in this app actually
            # references /static/ at all, so it was pure unintended
            # exposure. Points at a real (currently empty) static/ dir.
            static_folder=os.path.join(BASE_DIR, "static"),
            static_url_path='/static')
# BUGFIX (2026-08-12, audit L1): hardcoded secret_key means every
# install shares the same Flask session-signing key, which lets anyone
# who reads this source forge session cookies against any deployment.
# Falls back to a random per-process key if EXPCMS_SECRET_KEY isn't set,
# so flash messages/sessions still work out of the box, but a real
# deployment should set the env var to something persistent.
app.secret_key = os.environ.get("EXPCMS_SECRET_KEY") or uuid.uuid4().hex
app.jinja_env.add_extension('jinja2.ext.do')

# BUGFIX (2026-08-12, audit L7): version strings were hardcoded and
# stale in three separate templates ("3.1" while the project was
# actually 3.9.0). Single source of truth now: Project_Version from
# .bejson_project.json (the project-wide version, not this one file's
# own header version), exposed to every template.
def _get_expcms_version() -> str:
    try:
        with open(os.path.join(BASE_DIR, ".bejson_project.json"), encoding="utf-8") as _f:
            return json.load(_f).get("Project_Version", "unknown")
    except Exception:
        return "unknown"

EXPCMS_VERSION = _get_expcms_version()

@app.context_processor
def inject_html3():
    # Render master CSS
    becss_css = CSS_CORE.format(**COLOR)
    return dict(
        becss_css=becss_css,
        sidebar_html=get_sidebar_html(),
        html_card=html_card,
        html_stats_bar=html_stats_bar,
        html_code_box=html_code_box,
        html_brutal_table=html_brutal_table,
        html_table=html_table,
        html_widget=html_widget,
        html_info_box=html_info_box,
        expcms_version=EXPCMS_VERSION
    )

# BUGFIX (2026-08-12, audit L6): removed serve_assets()/'/assets/<path>' -
# it pointed at BASE_DIR/Assets, a directory that is never created by any
# code path here and isn't referenced by any template. The built site's
# own "assets/" folder (referenced by EXPCMS_Builder's "../assets/{...}"
# URLs) is populated from MediaAsset records via _copy_assets() into
# Processing/www/assets/, and is served by the preview server, not this
# admin app - this route was dead on arrival, not a stale duplicate of
# something still in use.
DATA_ROOT = os.path.join(BASE_DIR, "Data")
WWW_ROOT = os.path.join(BASE_DIR, "Processing", "www")
cms = MFDB_CMS_Manager(DATA_ROOT)
chunker = CMS_Chunker_Wrapper(cms)

# Mount the workspace at startup: creates the schema on a true fresh
# install, extracts from a .mfdb.zip if only an archive exists, or simply
# ensures a lock session exists if live data is already on disk. Calls
# initialize_system() internally at the correct point - do not call it
# separately here, or mount_system() can no longer tell a fresh install
# apart from live data that was just initialized moments ago, and skips
# creating the initial backup archive.
with app.app_context():
    cms.mount_system()

# --- Preview Server State ---
_preview_srv = {
    "thread": None,
    "httpd": None,
    "port": 8080,
    "running": False
}

@app.route('/')
def dashboard():
    global_stats = MFDBCore.mfdb_core_get_stats(cms.global_manifest)
    content_stats = MFDBCore.mfdb_core_get_stats(cms.content_manifest)
    return render_template("dashboard.html", g_stats=global_stats, c_stats=content_stats)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/landing_editor', methods=['GET', 'POST'])
def landing_editor():
    if request.method == 'POST':
        cms.add_global_config("landing_mode", request.form.get('landing_mode'))
        cms.add_global_config("landing_html", request.form.get('landing_html'))
        cms.add_global_config("landing_image", request.form.get('landing_image'))
        flash('Landing page configuration updated')
        return redirect(url_for('landing_editor'))
    
    configs = cms.get_global_configs()
    assets = cms.get_assets()
    return render_template("landing_editor.html", configs=configs, assets=assets)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        for key, value in request.form.items():
            cms.add_global_config(key, value)
        flash('Configuration updated')
        return redirect(url_for('config'))
    
    configs = cms.get_global_configs()
    return render_template("config.html", configs=configs)

@app.route('/factory_reset', methods=['POST'])
def reset_system():
    cms.factory_reset()
    cms.initialize_system()
    flash("System has been factory reset.")
    return redirect(url_for('dashboard'))

@app.route('/repack', methods=['POST'])
def repack_system():
    cms.repack_system()
    flash("System repacked and changes committed.")
    return redirect(url_for('dashboard'))

# =============================================================================
# MEDIA LIBRARY
# =============================================================================

@app.route('/media')
def media_library():
    all_assets = cms.get_assets()
    grouped = collections.defaultdict(list)
    for a in all_assets:
        folder = a.get('folder') or 'Root'
        grouped[folder].append(a)
    
    sorted_groups = sorted(grouped.items())
    videos = cms.get_video_assets()
    return render_template("media_library.html", groups=sorted_groups, videos=videos)

@app.route('/media/video/add', methods=['POST'])
def media_video_add():
    url = request.form.get('video_url', '').strip()
    title = request.form.get('video_title', '').strip()
    if not url:
        flash("Please enter a YouTube URL.")
        return redirect(url_for('media_library'))
    result = cms.add_video_asset(url, title)
    if result:
        flash("Video added to library.")
    else:
        flash("Couldn't parse that as a YouTube URL. Supported formats: youtube.com/watch?v=..., youtu.be/..., youtube.com/shorts/...")
    return redirect(url_for('media_library'))

@app.route('/media/video/delete/<video_uuid>', methods=['POST'])
def media_video_delete(video_uuid):
    if cms.delete_video_asset(video_uuid):
        flash("Video removed from library.")
    return redirect(url_for('media_library'))

@app.route('/media/upload', methods=['POST'])
def media_upload():
    import zipfile
    files = request.files.getlist('files')
    uploaded = 0
    skipped = 0
    errors = []

    def process_file(data: bytes, original_filename: str, content_type: str, folder: str = "") -> bool:
        """Process a single file into the media asset registry. Returns True on success."""
        nonlocal uploaded, skipped

        if not original_filename:
            skipped += 1
            return False

        # Normalise content_type — browser often sends None or '' for bulk dir uploads
        if not content_type:
            content_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

        # Deduplication by SHA-256 hash
        file_hash = cms.get_file_hash(data)
        if cms.get_asset_by_hash(file_hash):
            skipped += 1
            return False

        # Safe filename — handle unicode/special-char filenames from mobile
        safe_name = secure_filename(original_filename)
        if not safe_name:
            # secure_filename strips everything if name is all non-ASCII;
            # fall back to hash-based name with extension preserved
            ext = os.path.splitext(original_filename)[-1].lower() or '.bin'
            safe_name = f"asset_{file_hash[:8]}{ext}"

        # Avoid collisions on disk
        if os.path.exists(os.path.join(cms.assets_dir, safe_name)):
            base, ext = os.path.splitext(safe_name)
            safe_name = f"{base}_{uuid.uuid4().hex[:4]}{ext}"

        with open(os.path.join(cms.assets_dir, safe_name), "wb") as wf:
            wf.write(data)

        cms.add_asset(safe_name, original_filename, file_hash, len(data), content_type, folder)
        uploaded += 1
        return True

    def _sanitize_folder_label(raw_folder: str) -> str:
        """BUGFIX (2026-08-12, audit L3): folder is stored purely as a
        UI grouping label (never used in filesystem path construction -
        files are always written under assets_dir using safe_name), so
        this was flagged as hygiene rather than a path-traversal bug.
        Still worth normalizing: strips '..' components and leading
        slashes so a crafted zip member name like '../../etc/whatever'
        doesn't end up displayed/stored as a folder label verbatim."""
        parts = [p for p in raw_folder.replace("\\", "/").split("/") if p not in ("", ".", "..")]
        return "/".join(parts)

    for f in files:
        if not f or not f.filename:
            continue
        try:
            if f.filename.endswith('.zip'):
                # Zip bundle import
                with zipfile.ZipFile(f, 'r') as z:
                    for name in z.namelist():
                        if name.startswith('__MACOSX') or name.endswith('/'):
                            continue
                        folder = _sanitize_folder_label(os.path.dirname(name))
                        data = z.read(name)
                        ct = mimetypes.guess_type(name)[0] or 'application/octet-stream'
                        process_file(data, os.path.basename(name), ct, folder)
            else:
                # Single file or webkitdirectory bulk upload
                # Browser sends full relative path in f.filename for dir uploads
                folder = _sanitize_folder_label(os.path.dirname(f.filename))
                base_name = os.path.basename(f.filename)
                # content_type from browser is unreliable for bulk dir uploads — always supplement
                ct = f.content_type or mimetypes.guess_type(f.filename)[0] or 'application/octet-stream'
                process_file(f.read(), base_name, ct, folder)
        except Exception as exc:
            errors.append(f"{f.filename}: {exc}")

    msg = f"Uploaded {uploaded}"
    if skipped:
        msg += f", {skipped} skipped (duplicates)"
    if errors:
        msg += f", {len(errors)} failed"
        for e in errors:
            flash(e, 'error')
    flash(msg)
    return redirect(url_for('media_library'))

@app.route('/media/serve/<path:filename>')
def serve_media(filename):
    # Try exact path first (in case of hierarchy on disk)
    if os.path.exists(os.path.join(cms.assets_dir, filename)):
        return send_from_directory(cms.assets_dir, filename)
    # Fallback to flat lookup (organized by folder in DB but flat on disk)
    base = os.path.basename(filename)
    return send_from_directory(cms.assets_dir, base)

@app.route('/media/delete/<filename>', methods=['POST'])
def media_delete(filename):
    if cms.delete_asset(filename):
        flash("Asset deleted")
    return redirect(url_for('media_library'))

# =============================================================================
# CONTENT & CATEGORIES
# =============================================================================

# BUGFIX (2026-08-12, audit L11): categories()/pages() hardcoded
# 'data/category.bejson'/'data/page.bejson' instead of resolving the
# actual current file_path from the manifest - if an entity's on-disk
# filename ever changed (manifest reorganization, schema migration),
# these two routes would silently read a stale/nonexistent file while
# every other route (which goes through MFDBCore.mfdb_core_load_entity)
# would keep working correctly.
def _load_entity_doc_via_manifest(manifest_path: str, entity_name: str) -> dict:
    manifest_rows = MFDBCore.mfdb_core_load_manifest(manifest_path)
    entry = next((r for r in manifest_rows if r["entity_name"] == entity_name), None)
    if not entry:
        raise ValueError(f"Entity '{entity_name}' not found in manifest: {manifest_path}")
    entity_path = os.path.normpath(os.path.join(os.path.dirname(manifest_path), entry["file_path"]))
    return MFDBCore.bejson_core_load_file(entity_path)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        desc = request.form.get('description')
        feed = request.form.get('feed_type')

        existing = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
        is_update = any(c["category_slug"] == slug for c in existing)

        if is_update:
            cms.update_category(slug, name, desc, feed)
            flash('Category updated')
        else:
            cms.add_category(name, slug, desc, feed)
            flash('Category added successfully')
        return redirect(url_for('categories'))

    cats_doc = _load_entity_doc_via_manifest(cms.content_manifest, "Category")
    return render_template("categories.html", cats_doc=cats_doc)

@app.route('/categories/delete/<slug>', methods=['POST'])
def category_delete(slug):
    if slug == "uncategorized":
        flash('Cannot delete the default category.')
    else:
        cms.delete_category(slug)
        flash('Category deleted')
    return redirect(url_for('categories'))

@app.route('/pages')
def pages():
    pages_doc = _load_entity_doc_via_manifest(cms.content_manifest, "Page")
    return render_template("editor_list.html", pages_doc=pages_doc)

@app.route('/new')
def new_page():
    p = {
        "page_uuid": "", "title": "", "page_type": "article", 
        "category_fk": "uncategorized", "author_fk": "", 
        "featured_img": "", "html_body": "", "video_url": "", 
        "pdf_url": "", "source_files": []
    }
    return edit_page_view(p)

@app.route('/edit/<uuid>')
def edit_page(uuid):
    page_data = cms.get_full_page_data(uuid)
    if not page_data: return "Page not found", 404
    return edit_page_view(page_data)

@app.route('/widgets/picker')
def widgets_picker():
    """Returns the widget picker modal contents as an HTML fragment for the editor."""
    return render_template("_widget_picker.html", widgets=WIDGETS)

@app.route('/widgets/render/<widget_key>', methods=['POST'])
def widgets_render(widget_key):
    """Renders a widget with submitted form params and returns raw HTML snippet
    (not JSON — the editor JS inserts this directly as text into the textarea)."""
    html = render_widget(widget_key, request.form.to_dict())
    return html, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/import', methods=['GET'])
def import_html_index():
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    authors = cms.get_authors()
    return render_template("import_html.html", cats=cats, authors=authors)

@app.route('/import', methods=['POST'])
def import_html_submit():
    import tempfile
    files = request.files.getlist('html_files')
    category = request.form.get('category', '').strip() or 'uncategorized'
    author_uuid = request.form.get('author_uuid', '').strip()

    if not files or not files[0].filename:
        flash('Please select at least one HTML file.')
        return redirect(url_for('import_html_index'))

    success = 0
    errors = []
    for f in files:
        if not f.filename:
            continue
        fname = secure_filename(f.filename)
        if not fname.lower().endswith(('.html', '.htm')):
            errors.append(f"{f.filename}: not an HTML file, skipped")
            continue
        try:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name
            fallback_title = os.path.splitext(fname)[0].replace('_', ' ').replace('-', ' ').strip()
            result = cms.import_html_as_page(tmp_path, category=category, author_uuid=author_uuid, fallback_title=fallback_title)
            os.unlink(tmp_path)
            if result:
                success += 1
            else:
                errors.append(f"{f.filename}: import failed")
        except Exception as exc:
            errors.append(f"{f.filename}: {exc}")

    msg = f"Imported {success} page(s)."
    if errors:
        msg += f" {len(errors)} failed."
        for e in errors:
            flash(e)
    flash(msg)
    return redirect(url_for('pages'))

def edit_page_view(p):
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    authors = cms.get_authors()
    assets = cms.get_assets()
    return render_template("editor_main.html", p=p, cats=cats, authors=authors, assets=assets)

@app.route('/save', methods=['POST'])
def save_page():
    uuid_val = request.form.get('page_uuid')
    title = request.form.get('title')
    # BUGFIX: an unselected/blank category previously saved as category_fk=""
    # which matches no Category record, silently dropping the page from every
    # feed on the exported site. Fall back to 'uncategorized' like /import does.
    cat = request.form.get('category_fk', '').strip() or 'uncategorized'
    ptype = request.form.get('page_type')
    html_body = request.form.get('html_body')
    if html_body:
        html_body = MFDB_CMS_Manager._sanitize_imported_html(html_body)
    
    content_data = {"html_body": html_body}
    if ptype == 'video':
        content_data["video_url"] = request.form.get('video_url')
    elif ptype == 'pdf-viewer':
        content_data["pdf_url"] = request.form.get('pdf_url')
    elif ptype == 'source-code':
        source_files_json = request.form.get('source_files_json')
        if source_files_json:
            # BUGFIX (2026-08-12, audit L2): malformed JSON here (e.g. a
            # stray edit to the textarea) previously raised
            # json.JSONDecodeError straight out of the view, returning a
            # raw 500 instead of a usable error.
            try:
                content_data["source_files"] = json.loads(source_files_json)
            except json.JSONDecodeError as exc:
                flash(f"Source Files field is not valid JSON ({exc}); page not saved.")
                return redirect(url_for('edit_page', uuid=uuid_val) if uuid_val else url_for('new_page'))
        else:
            content_data["source_files"] = []
            
    content_data["author_fk"] = request.form.get('author_fk')
    content_data["featured_img"] = request.form.get('featured_img')

    if uuid_val:
        cms.update_page(uuid_val, title, cat, ptype, content_data)
        flash("Page updated successfully")
    else:
        cms.create_page(title, cat, ptype, content_data)
        flash("New page created")
        
    return redirect(url_for('pages'))

@app.route('/pages/delete/<uuid>', methods=['POST'])
def page_delete(uuid):
    cms.delete_page(uuid)
    flash("Page deleted")
    return redirect(url_for('pages'))

# =============================================================================
# APPS & NAVIGATION
# =============================================================================

@app.route('/apps', methods=['GET', 'POST'])
def apps():
    import zipfile
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        cat = request.form.get('category')
        feat_img = request.form.get('featured_img')
        entry = request.form.get('entry_file', 'index.html')
        
        app_file = request.files.get('app_file')
        app_uuid = str(uuid.uuid4())
        app_dir = os.path.join(cms.apps_dir, app_uuid)
        os.makedirs(app_dir, exist_ok=True)

        if app_file:
            fname = secure_filename(app_file.filename)
            fpath = os.path.join(app_dir, fname)
            app_file.save(fpath)
            
            if fname.endswith('.zip'):
                MAX_APP_ZIP_MEMBERS = 2000
                MAX_APP_ZIP_UNCOMPRESSED = 200 * 1024 * 1024  # 200MB
                try:
                    with zipfile.ZipFile(fpath, 'r') as z:
                        infos = z.infolist()
                        if len(infos) > MAX_APP_ZIP_MEMBERS:
                            raise ValueError(f"App zip has too many entries ({len(infos)})")
                        total_size = sum(i.file_size for i in infos)
                        if total_size > MAX_APP_ZIP_UNCOMPRESSED:
                            raise ValueError(f"App zip is too large uncompressed ({total_size} bytes)")
                        # LIB-CH-H2 pattern: extract via safe_extract_zip, never raw
                        # extractall() - guards every member against path traversal.
                        safe_extract_zip(z, Path(app_dir))
                    os.remove(fpath)
                    # BUGFIX (2026-08-18, audit NEW-H3): entry_file (line 567)
                    # came straight from the form and was never checked against
                    # what the zip actually contained, then got interpolated raw
                    # into an unescaped iframe src in EXPCMS_Builder.py - a value
                    # like '" onload="alert(1)' or '../../index.html' injects
                    # attributes/paths into every built app page. secure_filename
                    # strips path-traversal/quote characters, and requiring the
                    # result to actually exist in the extracted zip means an
                    # attacker can't point the iframe at an arbitrary path.
                    entry = secure_filename(entry) or "index.html"
                    if not (Path(app_dir) / entry).is_file():
                        os.remove(fpath) if os.path.exists(fpath) else None
                        shutil.rmtree(app_dir, ignore_errors=True)
                        flash(f"App import rejected: entry file '{entry}' not found in zip")
                        return redirect(url_for('apps'))
                except (ValueError, zipfile.BadZipFile) as exc:
                    os.remove(fpath)
                    flash(f"App import rejected: {exc}")
                    return redirect(url_for('apps'))
            else:
                entry = fname
                
        cms.create_app(name, desc, cat, feat_img, entry)
        flash("App imported successfully")
        return redirect(url_for('apps'))

    apps_list = cms.get_apps()
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    assets = cms.get_assets()
    return render_template("apps.html", apps=apps_list, cats=cats, assets=assets)

@app.route('/apps/delete/<uuid>', methods=['POST'])
def app_delete(uuid):
    cms.delete_app(uuid)
    flash("App deleted")
    return redirect(url_for('apps'))

@app.route('/navigation', methods=['GET', 'POST'])
def navigation():
    if request.method == 'POST':
        label = request.form.get('label')
        url = request.form.get('url')
        cms.add_nav_link(label, url)
        flash('Navigation link added')
        return redirect(url_for('navigation'))
    
    links = cms.get_nav_links()
    return render_template("navigation.html", links=links)

@app.route('/navigation/delete/<label>', methods=['POST'])
def navigation_delete(label):
    cms.delete_nav_link(label)
    return redirect(url_for('navigation'))

# =============================================================================
# AUTHORS & ADS
# =============================================================================

@app.route('/authors', methods=['GET', 'POST'])
def authors():
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        img = request.form.get('image_url')
        uuid_val = request.form.get('author_uuid')
        
        if uuid_val:
            cms.update_author(uuid_val, name, bio, img)
            flash('Author updated')
        else:
            cms.add_author(name, bio, img)
            flash('Author added')
        return redirect(url_for('authors'))
    
    authors_list = cms.get_authors()
    assets = cms.get_assets()
    return render_template("authors.html", authors=authors_list, assets=assets)

@app.route('/authors/delete/<uuid>', methods=['POST'])
def author_delete(uuid):
    cms.delete_author(uuid)
    flash("Author deleted")
    return redirect(url_for('authors'))

@app.route('/ads', methods=['GET', 'POST'])
def ads():
    if request.method == 'POST':
        name = request.form.get('name')
        img = request.form.get('image_url')
        link = request.form.get('link_url')
        zone = request.form.get('zone')
        uuid_val = request.form.get('ad_uuid')
        active = request.form.get('active') == 'true'
        
        if uuid_val:
            cms.update_ad(uuid_val, name, img, link, zone, active)
            flash('Ad updated')
        else:
            cms.add_ad(name, img, link, zone, active)
            flash('Ad added')
        return redirect(url_for('ads'))

    ads_list = cms.get_ads()
    assets = cms.get_assets()
    return render_template("ads.html", ads=ads_list, assets=assets)

@app.route('/ads/delete/<uuid>', methods=['POST'])
def ad_delete(uuid):
    cms.delete_ad(uuid)
    flash('Ad deleted')
    return redirect(url_for('ads'))

# =============================================================================
# BUILD & PREVIEW
# =============================================================================

@app.route('/system')
def system_tools():
    return render_template("system.html")

@app.route('/preview/<uuid>')
def preview_page(uuid):
    """Serve a preview of a specific page from the built site.

    BUGFIX (2026-08-12, audit L4): previously glob-scanned every *.html
    under WWW_ROOT and read each one fully into memory looking for a
    substring match on every single request - O(site size) per preview
    click. The page's own record already has everything needed to
    compute its built path directly (same convention EXPCMS_Builder
    uses in _build_page: <www_root>/<category_slug>/<page_slug>/)."""
    page_data = cms.get_full_page_data(uuid)
    if page_data:
        cat_slug = page_data.get("category_fk") or "uncategorized"
        page_slug = page_data.get("slug")
        if page_slug:
            page_path = os.path.join(WWW_ROOT, cat_slug, page_slug, "index.html")
            if os.path.exists(page_path):
                return open(page_path, encoding='utf-8', errors='replace').read(), 200, {'Content-Type': 'text/html'}
    # fallback: serve the homepage with a notice
    flash(f"Page {uuid} not yet built — run Build Site first.")
    return redirect(url_for('build_site'))

@app.route('/build')
def build_site():
    try:
        from EXPCMS_Builder import EXPCMS_Builder
        builder = EXPCMS_Builder(
            data_root=os.path.join(BASE_DIR, "Data"),
            skel_dir=os.path.join(BASE_DIR, "HTML_Skeletons"),
            output_dir=WWW_ROOT
        )
        builder.build_site()
        flash("Site built successfully! Reloading Preview Server...")
        if _preview_srv["running"]:
            srv_stop()
            srv_start()
    except Exception:
        app.logger.exception("Site build failed")
        flash("Build failed — see server log for the full traceback.")
    return redirect(url_for('dashboard'))

@app.route('/preview_srv')
def preview_manager():
    status = _preview_srv["running"]
    url = f"http://{request.host.split(':')[0]}:{_preview_srv['port']}"
    return render_template("preview_manager.html", running=status, url=url)

@app.route('/srv/start')
def srv_start():
    if not _preview_srv["running"]:
        def run_srv():
            import functools
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=WWW_ROOT)
            socketserver.TCPServer.allow_reuse_address = True
            # BUGFIX (2026-08-18, audit NEW-H2): this was hardcoded to bind
            # "" (0.0.0.0). H1 (pkg25) locked the *admin* app to loopback by
            # default, but this preview server - which serves the built
            # site, including hosted standalone apps (see NEW-H3) - was
            # missed and stayed on all interfaces with no auth. Mirrors the
            # H1 pattern: env-driven, loopback default, loud warning if
            # overridden.
            preview_host = os.environ.get("EXPCMS_PREVIEW_HOST", "127.0.0.1")
            if preview_host not in ("127.0.0.1", "localhost"):
                print(f"WARNING: EXPCMS_PREVIEW_HOST={preview_host} exposes the "
                      f"preview server (unauthenticated, serves built site + "
                      f"hosted apps) beyond loopback.")
            _preview_srv["httpd"] = socketserver.TCPServer((preview_host, _preview_srv["port"]), handler)
            _preview_srv["httpd"].serve_forever()
        
        _preview_srv["thread"] = threading.Thread(target=run_srv, daemon=True)
        _preview_srv["running"] = True  # Set before thread starts to prevent double-start race
        _preview_srv["thread"].start()
        flash("Preview server started")
    return redirect(url_for('preview_manager'))

@app.route('/srv/stop')
def srv_stop():
    if _preview_srv["running"] and _preview_srv["httpd"]:
        _preview_srv["httpd"].shutdown()
        _preview_srv["httpd"].server_close()
        _preview_srv["running"] = False
        flash("Preview server stopped")
    return redirect(url_for('preview_manager'))


# =============================================================================
# BACKUP & CHUNKING
# =============================================================================

@app.route('/backups')
def backups():
    all_backups = chunker.list_backups()
    return render_template("backups.html", backups=all_backups)

@app.route('/backup/create', methods=['POST'])
def backup_create():
    changelog = request.form.get("changelog", "Manual Backup")
    result = chunker.backup_site(changelog=changelog)
    if result["success"]:
        flash(f"Backup created: {result['zip_path']}")
    else:
        flash(f"Backup failed: {result['error']}")
    return redirect(url_for('backups'))

@app.route('/backup/restore', methods=['POST'])
def backup_restore():
    filename = request.form.get("filename")
    result = chunker.restore_site(filename)
    if result["success"]:
        # BUGFIX (2026-08-11, audit M2 follow-up): restore_site() now
        # swaps in a whole new db_global/db_content workspace. Re-mount
        # so locks/in-memory manifests are current, then rebuild the
        # static site so it isn't left showing the pre-restore content.
        try:
            cms.mount_system(force=True)
            from EXPCMS_Builder import EXPCMS_Builder
            builder = EXPCMS_Builder(
                data_root=os.path.join(BASE_DIR, "Data"),
                skel_dir=os.path.join(BASE_DIR, "HTML_Skeletons"),
                output_dir=WWW_ROOT
            )
            builder.build_site()
            flash(result["message"] + " Site rebuilt.")
        except Exception as exc:
            flash(result["message"] + f" (rebuild after restore failed: {exc} - run Build Site manually)")
    else:
        flash(f"Restore failed: {result['error']}")
    return redirect(url_for('backups'))

@app.route('/backup/download/<filename>')
def backup_download(filename):
    return send_from_directory(chunker.backup_dir, filename, as_attachment=True)

# --- HTML3 Integration ---
_SIDEBAR_ICONS = {
    "layout-dashboard": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "list":             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
    "plus-circle":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    "folder":           '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "layout":           '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    "image":            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
    "cpu":              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "globe":            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "link":             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "users":            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "radio":            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>',
    "settings":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "sliders":          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "archive":          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/></svg>',
    "monitor":          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    "terminal":         '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    "info":             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "file-text":        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "chevron-right":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
}

def _sidebar_icon(name, size=13):
    """Return an inline SVG for the given icon name, sized to `size`px."""
    svg = _SIDEBAR_ICONS.get(name, _SIDEBAR_ICONS["info"])
    return f'<span style="display:inline-flex;align-items:center;width:{size}px;height:{size}px;flex-shrink:0;">{svg}</span>'

_sidebar_cache = None

def get_sidebar_html():
    global _sidebar_cache
    if _sidebar_cache is not None:
        return _sidebar_cache

    groups = [
        {
            "id": "grp-main",
            "label": "Main",
            "icon": "layout-dashboard",
            "links": [
                ("/",               "layout-dashboard", "Dashboard"),
                ("/pages",          "list",             "Pages"),
                ("/new",            "plus-circle",      "New Page"),
                ("/import",         "file-text",        "HTML Import"),
                ("/categories",     "folder",           "Categories"),
                ("/landing_editor", "layout",           "Landing Page"),
            ]
        },
        {
            "id": "grp-media",
            "label": "Media & Assets",
            "icon": "image",
            "links": [
                ("/media", "image", "Media Library"),
                ("/apps",  "cpu",   "Standalone Apps"),
            ]
        },
        {
            "id": "grp-site",
            "label": "Site Management",
            "icon": "globe",
            "links": [
                ("/navigation", "link",  "Navigation"),
                ("/authors",    "users", "Authors"),
                ("/ads",        "radio", "Ad Rotator"),
            ]
        },
        {
            "id": "grp-system",
            "label": "System",
            "icon": "settings",
            "links": [
                ("/config",      "sliders", "Global Config"),
                ("/backups",     "archive", "Backups"),
                ("/preview_srv", "monitor", "Preview Server"),
                ("/system",      "terminal","Build & Tools"),
                ("/about",       "info",    "About"),
            ]
        },
    ]

    html_parts = [
        '<style>',
        '.c-sidebar-group { margin-bottom: 4px; }',
        '.c-sidebar-group__btn {',
        '  width: 100%; background: none; border: none; padding: 8px 12px;',
        '  display: flex; align-items: center; gap: 8px; cursor: pointer;',
        '  color: var(--text-main); font-family: var(--font-mono);',
        '  font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.08em;',
        '  font-weight: 700; border-radius: 4px; transition: background 0.15s;',
        '  text-align: left;',
        '}',
        '.c-sidebar-group__btn:hover { background: var(--primary); color: #fff; }',
        '.c-sidebar-group__btn[aria-expanded="true"] { color: var(--text-main); }',
        '.c-sidebar-group__chevron { margin-left: auto; transition: transform 0.2s; display: inline-flex; align-items: center; width: 12px; height: 12px; flex-shrink: 0; transform: rotate(90deg); }',
        '.c-sidebar-group__btn[aria-expanded="false"] .c-sidebar-group__chevron { transform: rotate(0deg); }',
        '.c-sidebar-group__links { display: none; padding-left: 8px; }',
        '.c-sidebar-group__links--open { display: block; }',
        '.c-sidebar__link { display: flex; align-items: center; gap: 8px; padding: 7px 12px; font-size: 0.75rem; color: var(--text-main); text-decoration: none; border-radius: 4px; transition: background 0.15s, color 0.15s; border-left: 2px solid transparent; }',
        '.c-sidebar__link:hover { background: var(--primary); color: #fff; }',
        '.c-sidebar__link--active { background: var(--primary); color: #fff; font-weight: 600; border-left: 2px solid var(--primary); }',
        '.c-sidebar__link svg { width: 13px; height: 13px; flex-shrink: 0; }',
        '</style>',
        '<nav id="admin-sidebar-nav">',
    ]

    for group in groups:
        gid = group["id"]
        html_parts.append('<div class="c-sidebar-group">')
        html_parts.append(
            f'<button class="c-sidebar-group__btn" '
            f'aria-expanded="true" '
            f'onclick="toggleGroup(\'{gid}\')">'
            f'{_sidebar_icon(group["icon"], 12)}'
            f'{group["label"]}'
            f'<span class="c-sidebar-group__chevron">{_sidebar_icon("chevron-right", 12)}</span>'
            f'</button>'
        )
        html_parts.append(f'<div class="c-sidebar-group__links c-sidebar-group__links--open" id="{gid}">')
        for url, icon, label in group["links"]:
            html_parts.append(
                f'<a href="{url}" class="c-sidebar__link" data-path="{url}">'
                f'{_sidebar_icon(icon, 13)}{label}</a>'
            )
        html_parts.append('</div></div>')

    html_parts.append('</nav>')
    html_parts.append('''<script>
function toggleGroup(id) {
    const links = document.getElementById(id);
    const btn = links.previousElementSibling;
    const isOpen = links.classList.contains('c-sidebar-group__links--open');
    links.classList.toggle('c-sidebar-group__links--open', !isOpen);
    btn.setAttribute('aria-expanded', (!isOpen).toString());
}
// Auto-expand group containing current page and mark active link
(function(){
    const current = window.location.pathname;
    document.querySelectorAll('.c-sidebar__link').forEach(function(a) {
        const match = current === '/'
            ? a.dataset.path === '/'
            : current.startsWith(a.dataset.path) && a.dataset.path !== '/';
        if (match) {
            a.classList.add('c-sidebar__link--active');
            const group = a.closest('.c-sidebar-group__links');
            if (group) {
                group.classList.add('c-sidebar-group__links--open');
                group.previousElementSibling.setAttribute('aria-expanded','true');
            }
        }
    });
})();
</script>''')

    _sidebar_cache = '\n'.join(html_parts)
    return _sidebar_cache

if __name__ == '__main__':
    # SECURITY (2026-08-11, audit finding H1): this app has no
    # authentication anywhere. Previously bound 0.0.0.0 with debug=True,
    # exposing the Werkzeug interactive debugger (arbitrary code
    # execution) to the whole LAN. Now config-driven, defaulting to
    # loopback-only with the debugger off; debug is only ever enabled
    # automatically when the host is loopback.
    _run_host = os.environ.get("EXPCMS_HOST", "127.0.0.1")
    _run_port = int(os.environ.get("EXPCMS_PORT", "5005"))
    _run_debug_env = os.environ.get("EXPCMS_DEBUG")
    if _run_debug_env is not None:
        _run_debug = _run_debug_env.strip().lower() in ("1", "true", "yes")
    else:
        _run_debug = _run_host in ("127.0.0.1", "localhost", "::1")
    if _run_host not in ("127.0.0.1", "localhost", "::1") and _run_debug:
        raise RuntimeError(
            "EXPCMS_DEBUG=1 with non-loopback EXPCMS_HOST is BLOCKED. "
            "The Werkzeug debugger exposes arbitrary code execution to the network. "
            "Set EXPCMS_HOST to 127.0.0.1 or unset EXPCMS_DEBUG."
        )
    app.run(host=_run_host, port=_run_port, debug=_run_debug)
