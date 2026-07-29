# RELATIONAL_GUID: 2e3e1761-df04-42a1-b64f-27b708eca287
# VERSION: v3.5.0
# CREDITS: Elton Boehnen (github.com/boehnenelton)
# FILE: EXPCMS.py
# DATE: 2026-07-10

"""
Experimental CMS v3.1 — Unified Administrative Dashboard
Description: Flask-based admin dashboard and MFDB content manager for the ExpCMS static site engine.
             Isolated from production BEJSON CMS via the Lib_EXPCMS library boundary.
"""
import os
import sys
import uuid
import collections
import threading
import http.server
import socketserver
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# Add Lib to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "Lib_EXPCMS")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_expcms_mfdb import MFDB_CMS_Manager
from lib_expcms_widgets import WIDGETS, render_widget
from lib_bejson_html3_skeletons import COLOR, CSS_CORE
from lib_html3_body import html_card, html_stats_bar, html_code_box, html_brutal_table
from lib_html3_tables import html_table
from lib_html3_widgets import html_widget, html_info_box
from lib_expcms_chunker_wrapper import CMS_Chunker_Wrapper
import lib_bejson_Core_mfdb_core as MFDBCore

# --- Flask App Initialization ---
import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, "templates"),
            static_url_path='/static')
app.secret_key = 'expcss-unified-v2-secret'
app.jinja_env.add_extension('jinja2.ext.do')

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
        html_info_box=html_info_box
    )

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "Assets"), filename)

DATA_ROOT = os.path.join(BASE_DIR, "Data")
WWW_ROOT = os.path.join(BASE_DIR, "Processing", "www")
cms = MFDB_CMS_Manager(DATA_ROOT)
chunker = CMS_Chunker_Wrapper(cms)

# Initialize databases on start
with app.app_context():
    cms.initialize_system()

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

@app.route('/factory_reset')
def reset_system():
    cms.factory_reset()
    cms.initialize_system()
    flash("System has been factory reset.")
    return redirect(url_for('dashboard'))

@app.route('/repack')
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

@app.route('/media/video/delete/<video_uuid>')
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
                        folder = os.path.dirname(name)
                        data = z.read(name)
                        ct = mimetypes.guess_type(name)[0] or 'application/octet-stream'
                        process_file(data, os.path.basename(name), ct, folder)
            else:
                # Single file or webkitdirectory bulk upload
                # Browser sends full relative path in f.filename for dir uploads
                folder = os.path.dirname(f.filename)
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

@app.route('/media/delete/<filename>')
def media_delete(filename):
    if cms.delete_asset(filename):
        flash("Asset deleted")
    return redirect(url_for('media_library'))

# =============================================================================
# CONTENT & CATEGORIES
# =============================================================================

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

    cats_doc = MFDBCore.bejson_core_load_file(os.path.join(cms.content_db_root, 'data', 'category.bejson'))
    return render_template("categories.html", cats_doc=cats_doc)

@app.route('/categories/delete/<slug>')
def category_delete(slug):
    if slug == "uncategorized":
        flash('Cannot delete the default category.')
    else:
        cms.delete_category(slug)
        flash('Category deleted')
    return redirect(url_for('categories'))

@app.route('/pages')
def pages():
    pages_doc = MFDBCore.bejson_core_load_file(os.path.join(cms.content_db_root, "data", "page.bejson"))
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
            result = cms.import_html_as_page(tmp_path, category=category, author_uuid=author_uuid)
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
    cat = request.form.get('category_fk')
    ptype = request.form.get('page_type')
    html_body = request.form.get('html_body')
    
    content_data = {"html_body": html_body}
    if ptype == 'video':
        content_data["video_url"] = request.form.get('video_url')
    elif ptype == 'pdf-viewer':
        content_data["pdf_url"] = request.form.get('pdf_url')
    elif ptype == 'source-code':
        source_files_json = request.form.get('source_files_json')
        if source_files_json:
            content_data["source_files"] = json.loads(source_files_json)
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

@app.route('/pages/delete/<uuid>')
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
        cat = request.form.get('category_fk')
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
                with zipfile.ZipFile(fpath, 'r') as z:
                    z.extractall(app_dir)
                os.remove(fpath)
            else:
                entry = fname
                
        cms.create_app(name, desc, cat, feat_img, entry)
        flash("App imported successfully")
        return redirect(url_for('apps'))

    apps_list = cms.get_apps()
    cats = MFDBCore.mfdb_core_load_entity(cms.content_manifest, "Category")
    assets = cms.get_assets()
    return render_template("apps.html", apps=apps_list, cats=cats, assets=assets)

@app.route('/apps/delete/<uuid>')
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

@app.route('/navigation/delete/<label>')
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

@app.route('/authors/delete/<uuid>')
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

@app.route('/ads/delete/<uuid>')
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
    """Serve a preview of a specific page from the built site."""
    page_dir = os.path.join(WWW_ROOT, "**", "*.html")
    import glob as _glob
    built_pages = _glob.glob(page_dir, recursive=True)
    # find the page by scanning built HTML for the uuid
    for page_path in built_pages:
        try:
            content = open(page_path, encoding='utf-8', errors='replace').read()
            if uuid in content:
                return content, 200, {'Content-Type': 'text/html'}
        except Exception:
            continue
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
            _preview_srv["httpd"] = socketserver.TCPServer(("", _preview_srv["port"]), handler)
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
        flash(result["message"])
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
        '  color: #aaa; font-family: var(--font-mono);',
        '  font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.08em;',
        '  font-weight: 700; border-radius: 4px; transition: background 0.15s;',
        '  text-align: left;',
        '}',
        '.c-sidebar-group__btn:hover { background: rgba(255,255,255,0.05); color: #fff; }',
        '.c-sidebar-group__btn[aria-expanded="true"] { color: #e0e0e0; }',
        '.c-sidebar-group__chevron { margin-left: auto; transition: transform 0.2s; display: inline-flex; align-items: center; width: 12px; height: 12px; flex-shrink: 0; transform: rotate(90deg); }',
        '.c-sidebar-group__btn[aria-expanded="false"] .c-sidebar-group__chevron { transform: rotate(0deg); }',
        '.c-sidebar-group__links { display: none; padding-left: 8px; }',
        '.c-sidebar-group__links--open { display: block; }',
        '.c-sidebar__link { display: flex; align-items: center; gap: 8px; padding: 7px 12px; font-size: 0.75rem; color: #b0b0b0; text-decoration: none; border-radius: 4px; transition: background 0.15s, color 0.15s; border-left: 2px solid transparent; }',
        '.c-sidebar__link:hover { background: rgba(255,255,255,0.06); color: #fff; }',
        '.c-sidebar__link--active { background: rgba(222,38,38,0.18); color: #fff; font-weight: 600; border-left: 2px solid var(--primary); }',
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
    app.run(host='0.0.0.0', port=5005, debug=True)
