"""
Library:        lib_bejson_ExpCMS_cms_mfdb.py
Family:         ExpCMS
Description:    Relational database layer for Experimental CMS content, pages, and taxonomies.
Version:        2.5.1
Date:           2026-08-18
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  2751e1b1-78c3-4574-b7f6-14c67e8ba085
CHANGE (2026-08-18): pkg28 audit-fix pass, Phase 0 (NEW-C1, regression
from pkg26's M6 fix). The Page entity's field is "slug" (see
Data/workspace/db_content/data/page.bejson and initialize_system()),
but M6's _unique_page_slug()/update_page() read/wrote "page_slug" -
a name that does not exist in the schema. Effect: create_page() raised
KeyError on any category that already held a page (i.e. every category
in the shipped DB), and update_page() raised BEJSONCoreError AFTER the
title had already been written, leaving a partial/inconsistent record.
Both call sites corrected to use "slug".
CHANGE (2026-08-12): pkg26 audit-fix pass, part 2.
H2 follow-up: fixed original_filename -> original_name field-name mismatch
in editor_main.html's featured-image dropdown (same class of bug as the
audit's H4, just not the specific instance H4 named).
M6: create_page()/update_page() now call the new _unique_page_slug() -
two pages with the same title in the same category previously got the
same slug, and the builder silently overwrote the first page's built
output with the second's while both remained in the DB. update_page()
also now regenerates the slug when the title changes (it never did
before, so a renamed page kept building at its stale old URL).
M7: delete_category() now reassigns any member pages to "uncategorized"
before removing the category - previously they were left with a
dangling category_fk and silently vanished from every feed (same trap
pkg19 already fixed for blank categories).
CHANGE (2026-08-11): pkg25 audit-fix pass.
C2: import_html_as_page() had no sanitization at all despite README/
usage-guide claiming it strips scripts and AI-watermark footers via
BeautifulSoup - html_body is rendered with `| safe` on every built page,
so an imported file's <script>/event-handler content survived straight
into the live site. Added _sanitize_imported_html() (BeautifulSoup,
already a declared but unused dependency) and wired it in before the
title-detect pass.
H2: added _reconcile_global_schema(), called from mount_system() on every
startup. Installs whose global manifest predates a field being added to
this class's schema (e.g. MediaAsset.folder) or predates a whole entity
being added (VideoAsset) never got it, so add_asset()/add_video() failed
mfdb_core_add_entity_record()'s length check and landed in the caller's
except - uploads silently did nothing on those installs. Also fixed the
webp-conversion add_entity_record() call in optimize_assets() that was
passing 6 values against the 7-field MediaAsset schema.
CHANGE (2026-08-08): pkg24 library reconciliation. Relocated from
Lib_PY/CMS/lib_bejson_CMS_cms_mfdb.py to Lib_PY/ExpCMS/lib_bejson_ExpCMS_cms_mfdb.py.
This file is Experimental CMS's own content/page/taxonomy database layer -
it was mis-filed under the CMS family, which belongs to a separate CMS
product. Renamed Library/Family header to ExpCMS to match. No logic
changed in this pass; EXPCMS.py and EXPCMS_Builder.py's imports and
sys.path family lists updated accordingly, and the now-empty/foreign
Lib_PY/CMS folder (this file plus two confirmed-unused files,
lib_bejson_CMS_cms_config.py and lib_bejson_CMS_cms_core.py, neither
imported anywhere in this project) removed from the package.
CHANGE (2026-08-05): pkg23 database audit - critical regression fix.
mount_system() was falling straight through to MFDBCore.MFDBArchive.mount()
whenever the .zip archives existed, with no check for whether live
workspace data already existed. That wipes the workspace and re-extracts
from the archive whenever no .mfdb_lock is present - which happens on
every fresh boot, since this app's own CRUD never writes to the archive
except via manual /repack. Reproduced against a copy of the real shipped
Data/ dir: SiteConfig 6 rows -> 3, VideoAsset table dropped entirely, in
one mount_system() call. Rewrote to only cold-mount from the archive when
no live manifest exists yet for that root; otherwise just ensures a lock
session. Verified fresh-install, live-data-preserved, and repeated-restart
scenarios all pass; repack still works afterward in all three.
CHANGE (2026-08-05): pkg21 bugfix pass.
1) Added add_video_asset()/delete_video_asset()/get_video_assets() and
   registered VideoAsset in initialize_system()'s global_entities. The
   VideoAsset entity was already present in the manifest/data on disk
   (data/videoasset.bejson, primary_key video_uuid) but the manager
   methods that read/write it had been lost - a ghost update. EXPCMS.py's
   media_library route calling cms.get_video_assets() was raising
   AttributeError. Verified via standalone add/get/delete round-trip.
2) Fixed import_html_as_page(): previously required a positional `title`
   arg that EXPCMS.py's /import route never supplied (TypeError on every
   HTML import). Rewrote to auto-detect title from <title>, then <h1>,
   then an optional fallback_title - matching what templates/import_html.html
   already told users would happen. Verified with both a titled and an
   untitled fixture file.
CHANGE (2026-07-07): Fixed a verified bug - imported bejson_utility_slugify
from lib_bejson_Utility_bejson_utility, a module that doesn't exist
anywhere in the project (confirmed pre-existing, predates this session -
this file could never actually run). Implemented locally instead,
matching the identical pattern already used in Flask_Page_Editor.py's
_slug(). Verified via cms-manage.py actually running end-to-end
afterward, not just a syntax check.
"""

import os
import sys
import uuid
import hashlib
import shutil
import zipfile
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, Comment

# Add Lib to path
LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

import lib_bejson_Core_bejson_core as BEJSONCore
import lib_bejson_Core_mfdb_core as MFDBCore
from lib_bejson_Core_bejson_path_guard import bejson_safe_join

def bejson_utility_slugify(text):
    """Was imported from lib_bejson_Utility_bejson_utility, which doesn't
    exist anywhere in this project (confirmed broken since before this
    session - this file could never actually run). Implemented locally,
    matching the identical pattern already used in Flask_Page_Editor.py's
    _slug()."""
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')

_YOUTUBE_ID_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?v=)([\w-]{11})"),
    re.compile(r"(?:youtu\.be/)([\w-]{11})"),
    re.compile(r"(?:youtube\.com/embed/)([\w-]{11})"),
    re.compile(r"(?:youtube\.com/shorts/)([\w-]{11})"),
]

def bejson_cms_extract_youtube_id(raw: str) -> str:
    """Extracts an 11-char YouTube video ID from a URL, or returns the input
    unchanged if it already looks like a bare video ID. Local copy of the
    identical pattern in lib_bejson_ExpCMS_widgets.py — kept as a local copy
    rather than cross-importing between this DB-layer file and the
    presentation-layer widgets file within the ExpCMS family."""
    raw = (raw or "").strip()
    for pattern in _YOUTUBE_ID_PATTERNS:
        m = pattern.search(raw)
        if m:
            return m.group(1)
    if re.fullmatch(r"[\w-]{11}", raw):
        return raw
    return ""

# Standard Entity Schemas (Policy Standard)
SCHEMA_SITECONFIG = [
    {"name": "config_key", "type": "string"},
    {"name": "config_value", "type": "string"},
    {"name": "description", "type": "string"}
]

class MFDB_CMS_Manager:
    def __init__(self, data_root: str):
        self.data_root = data_root
        self.workspace_root = os.path.join(data_root, "workspace")
        self.global_db_root = os.path.join(self.workspace_root, "db_global")
        self.content_db_root = os.path.join(self.workspace_root, "db_content")
        self.assets_dir = os.path.join(data_root, "assets")
        self.apps_dir = os.path.join(data_root, "standalone_apps")
        self.www_root = os.path.join(os.path.dirname(data_root), "Processing", "www")
        
        # Manifests inside the workspace
        self.global_manifest = os.path.join(self.global_db_root, "104a.mfdb.bejson")
        self.content_manifest = os.path.join(self.content_db_root, "104a.mfdb.bejson")
        
        # Transport Archives
        self.global_archive = os.path.join(data_root, "global_master.mfdb.zip")
        self.content_archive = os.path.join(data_root, "content_master.mfdb.zip")

        # Granular Change Tracking
        self.change_log = []
        
        if not os.path.exists(self.assets_dir): os.makedirs(self.assets_dir)
        if not os.path.exists(self.apps_dir): os.makedirs(self.apps_dir)

    def log_change(self, entity: str, action: str, identifier: Any, metadata: dict = None):
        """Records a specific modification for granular state tracking."""
        self.change_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity": entity,
            "action": action,
            "id": identifier,
            "metadata": metadata or {}
        })

    def is_dirty(self) -> bool:
        return len(self.change_log) > 0

    def clear_changes(self):
        self.change_log = []

    def mount_system(self, force: bool = False):
        """Ensures both workspace roots have an active .mfdb_lock so
        repack_system() can commit. Live workspace files under db_root are
        this app's actual source of truth - every CRUD method (add_author,
        create_page, etc.) reads/writes <db_root>/104a.mfdb.bejson directly,
        and the .zip archives are only written when repack_system() runs.

        VERIFIED BUG (2026-08-05): this used to fall straight through to
        MFDBCore.MFDBArchive.mount() whenever the archives existed, with no
        check for whether live workspace data already existed. mount()'s
        cold-mount path wipes target_dir and re-extracts from the .zip
        whenever no .mfdb_lock is present - which silently reverted live
        data back to a stale archived snapshot and dropped an entire entity
        table (VideoAsset) that had been added since the last repack.
        Reproduced against a copy of the actual shipped Data/ directory:
        SiteConfig 6 rows -> 3, VideoAsset table gone entirely. Root cause
        was compounded by the earlier fix that made EXPCMS.py call
        mount_system() on every startup - previously mount_system() was
        never called at all, so this path was dormant.

        Fix: only ever call MFDBArchive.mount() (extract-from-archive) when
        no live manifest exists yet for that root. If live data is already
        on disk, just ensure the lock session exists - never wipe it.
        """
        needs_bootstrap_repack = []
        for db_root, manifest_path, archive in [
            (self.global_db_root, self.global_manifest, self.global_archive),
            (self.content_db_root, self.content_manifest, self.content_archive),
        ]:
            os.makedirs(db_root, exist_ok=True)
            lock_file = os.path.join(db_root, ".mfdb_lock")

            if os.path.exists(manifest_path):
                # Live data already present on disk - the source of truth.
                # Only ensure a lock session exists; never wipe/re-extract.
                if force or not os.path.exists(lock_file):
                    with open(lock_file, "w") as f:
                        json.dump({"pid": os.getpid(), "mounted_at": datetime.now(timezone.utc).isoformat()}, f)
            elif os.path.exists(archive):
                # No live workspace yet, but a transport archive exists -
                # the one case MFDBArchive.mount()'s extract behavior is
                # actually the correct operation for.
                MFDBCore.MFDBArchive.mount(archive, db_root, force=force)
            else:
                # True fresh install: no schema anywhere yet for this root.
                needs_bootstrap_repack.append(db_root)

        self.initialize_system()  # no-op for any root whose manifest already exists
        self._reconcile_global_schema()

        for db_root in needs_bootstrap_repack:
            lock_file = os.path.join(db_root, ".mfdb_lock")
            if not os.path.exists(lock_file):
                with open(lock_file, "w") as f:
                    json.dump({"pid": os.getpid(), "mounted_at": datetime.now(timezone.utc).isoformat()}, f)

        if needs_bootstrap_repack:
            self.repack_system()

        self.clear_changes()

    _GLOBAL_CANONICAL_SCHEMA = {
        "MediaAsset": {
            "primary_key": "filename",
            "fields": [
                {"name": "filename", "type": "string"},
                {"name": "original_name", "type": "string"},
                {"name": "file_hash", "type": "string"},
                {"name": "file_size", "type": "integer"},
                {"name": "mime_type", "type": "string"},
                {"name": "uploaded_at", "type": "string"},
                {"name": "folder", "type": "string"},
            ],
        },
        "VideoAsset": {
            "primary_key": "video_uuid",
            "fields": [
                {"name": "video_uuid", "type": "string"},
                {"name": "url", "type": "string"},
                {"name": "video_id", "type": "string"},
                {"name": "provider", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "thumbnail_url", "type": "string"},
                {"name": "added_at", "type": "string"},
            ],
        },
    }

    def _reconcile_global_schema(self):
        """SCHEMA RECONCILE (2026-08-11, audit finding H2): initialize_system()
        only builds entities the first time global_manifest is created. An
        install whose manifest predates a field being added to this class
        (e.g. MediaAsset.folder) - or predates a whole entity being added
        (e.g. VideoAsset) - never gets it, and add_asset()/add_video() then
        fail the row-length check inside mfdb_core_add_entity_record() and
        land in the caller's bare except, so uploads silently do nothing.
        This appends any missing canonical field to the END of that
        entity's Fields[] (BEJSON positional integrity - never inserted
        mid-array) and pads every existing row with None for it, and
        registers any missing canonical entity outright via the normal
        Core API. Idempotent; safe to call on every mount_system()."""
        if not os.path.exists(self.global_manifest):
            return  # brand-new install - initialize_system() just built it fresh

        manifest_rows = MFDBCore.mfdb_core_load_manifest(self.global_manifest)
        registered = {r["entity_name"]: r for r in manifest_rows}

        for entity_name, spec in self._GLOBAL_CANONICAL_SCHEMA.items():
            if entity_name not in registered:
                MFDBCore.mfdb_core_create_entity_file(
                    self.global_manifest, entity_name, spec["fields"],
                    description=f"{entity_name} (schema-reconciled {datetime.now(timezone.utc).date().isoformat()})",
                    primary_key=spec["primary_key"],
                )
                self.log_change(entity_name, "SCHEMA_RECONCILE_CREATE", entity_name)
                continue

            doc = MFDBCore.mfdb_core_get_entity_doc(self.global_manifest, entity_name)
            live_names = {f["name"] for f in doc.get("Fields", [])}
            missing = [f for f in spec["fields"] if f["name"] not in live_names]
            if not missing:
                continue

            doc["Fields"].extend(missing)
            for row in doc.get("Values", []):
                row.extend([None] * len(missing))

            entity_path = os.path.normpath(os.path.join(
                os.path.dirname(self.global_manifest), registered[entity_name]["file_path"]
            ))
            BEJSONCore.bejson_core_atomic_write(entity_path, doc)
            self.log_change(entity_name, "SCHEMA_RECONCILE_ADD_FIELDS", [f["name"] for f in missing])

    def repack_system(self):
        MFDBCore.MFDBArchive.commit(self.global_db_root, self.global_archive)
        MFDBCore.MFDBArchive.commit(self.content_db_root, self.content_archive)
        self.clear_changes()

    def _create_record(self, entity_schema: List[Dict], rtp: str, values_map: Dict) -> List:
        """Helper to create a positional record from a named values map."""
        fm = {f["name"]: i for i, f in enumerate(entity_schema)}
        row = [None] * len(entity_schema)
        # 104db discriminator handling
        if "Record_Type_Parent" in fm:
            row[fm["Record_Type_Parent"]] = rtp
        for k, v in values_map.items():
            if k in fm: row[fm[k]] = v
        return row

    def factory_reset(self):
        dirs_to_wipe = [self.workspace_root, self.assets_dir, self.apps_dir, self.www_root]
        for d in dirs_to_wipe:
            if os.path.exists(d): shutil.rmtree(d)
            os.makedirs(d)
        for arc in [self.global_archive, self.content_archive]:
            if os.path.exists(arc): os.remove(arc)
        self.clear_changes()
        print("Factory reset complete. System wiped.")

    def initialize_system(self):
        # 1. GLOBAL DATABASE
        if not os.path.exists(self.global_manifest):
            global_entities = [
                {"name": "SiteConfig", "primary_key": "config_key", "fields": [{"name": "config_key", "type": "string"}, {"name": "config_value", "type": "string"}, {"name": "description", "type": "string"}]},
                {"name": "NavLink", "fields": [{"name": "label", "type": "string"}, {"name": "url", "type": "string"}, {"name": "order", "type": "integer"}]},
                {"name": "SocialLink", "fields": [{"name": "platform", "type": "string"}, {"name": "url", "type": "string"}, {"name": "icon", "type": "string"}]},
                {"name": "AuthorProfile", "primary_key": "author_uuid", "fields": [{"name": "author_uuid", "type": "string"}, {"name": "name", "type": "string"}, {"name": "bio", "type": "string"}, {"name": "image_url", "type": "string"}]},
                {"name": "AdUnit", "primary_key": "ad_uuid", "fields": [{"name": "ad_uuid", "type": "string"}, {"name": "name", "type": "string"}, {"name": "image_url", "type": "string"}, {"name": "link_url", "type": "string"}, {"name": "zone", "type": "string"}, {"name": "active", "type": "boolean"}]},
                {"name": "MediaAsset", "primary_key": "filename", "fields": [{"name": "filename", "type": "string"}, {"name": "original_name", "type": "string"}, {"name": "file_hash", "type": "string"}, {"name": "file_size", "type": "integer"}, {"name": "mime_type", "type": "string"}, {"name": "uploaded_at", "type": "string"}, {"name": "folder", "type": "string"}]},
                {"name": "VideoAsset", "primary_key": "video_uuid", "fields": [{"name": "video_uuid", "type": "string"}, {"name": "url", "type": "string"}, {"name": "video_id", "type": "string"}, {"name": "provider", "type": "string"}, {"name": "title", "type": "string"}, {"name": "thumbnail_url", "type": "string"}, {"name": "added_at", "type": "string"}]}
            ]
            MFDBCore.mfdb_core_create_database(root_dir=self.global_db_root, db_name="BEJSON CMS Global", entities=global_entities)
            self.add_global_config("site_title", "boehnenelton2024")
            self.add_global_config("site_tagline", "Premium Dark Theme Templates")
            self.add_global_config("base_url", "https://boehnenelton2024.pages.dev")
            
            # Dynamic Creation
            soc_schema = next(e["fields"] for e in global_entities if e["name"] == "SocialLink")
            MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "SocialLink", 
                self._create_record(soc_schema, "SocialLink", {"platform": "GitHub", "url": "https://github.com/boehnenelton", "icon": "github"}))

        # 2. CONTENT DATABASE
        if not os.path.exists(self.content_manifest):
            content_entities = [
                {"name": "Category", "primary_key": "category_slug", "fields": [
                    {"name": "category_name", "type": "string"},
                    {"name": "category_slug", "type": "string"},
                    {"name": "description", "type": "string"},
                    {"name": "feed_type", "type": "string"}
                ]},
                {"name": "Page", "primary_key": "page_uuid", "fields": [{"name": "page_uuid", "type": "string"}, {"name": "title", "type": "string"}, {"name": "slug", "type": "string"}, {"name": "category_fk", "type": "string"}, {"name": "author_fk", "type": "string"}, {"name": "page_type", "type": "string"}, {"name": "featured_img", "type": "string"}, {"name": "created_at", "type": "string"}]},
                {"name": "PageContent", "fields": [{"name": "page_uuid_fk", "type": "string"}, {"name": "html_body", "type": "string"}, {"name": "markdown_body", "type": "string"}, {"name": "source_files", "type": "array"}, {"name": "video_url", "type": "string"}, {"name": "pdf_url", "type": "string"}, {"name": "pros", "type": "array"}, {"name": "cons", "type": "array"}, {"name": "verdict_score", "type": "number"}]},
                {"name": "StandaloneApp", "primary_key": "app_uuid", "fields": [{"name": "app_uuid", "type": "string"}, {"name": "name", "type": "string"}, {"name": "slug", "type": "string"}, {"name": "description", "type": "string"}, {"name": "category_fk", "type": "string"}, {"name": "featured_img", "type": "string"}, {"name": "entry_file", "type": "string"}, {"name": "created_at", "type": "string"}]}
            ]
            MFDBCore.mfdb_core_create_database(root_dir=self.content_db_root, db_name="BEJSON CMS Content", entities=content_entities)
            self.add_category("Uncategorized", "uncategorized", "General posts", "blog")

    def add_global_config(self, key: str, value: str, desc: str = ""):
        # Use module-level schema constant (REC-6)
        row = self._create_record(SCHEMA_SITECONFIG, "SiteConfig", {"config_key": key, "config_value": value, "description": desc})
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "SiteConfig", row)
        self.log_change("SiteConfig", "ADD", key)

    def get_global_configs(self) -> Dict[str, str]:
        recs = MFDBCore.mfdb_core_load_entity(self.global_manifest, "SiteConfig")
        return {r["config_key"]: r["config_value"] for r in recs}

    def add_nav_link(self, label: str, url: str, order: int = 0):
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "NavLink", [label, url, order])
        self.log_change("NavLink", "ADD", label)

    def delete_nav_link(self, label: str):
        recs = MFDBCore.mfdb_core_load_entity(self.global_manifest, "NavLink")
        for i, r in enumerate(recs):
            if r["label"] == label:
                MFDBCore.mfdb_core_remove_entity_record(self.global_manifest, "NavLink", i)
                self.log_change("NavLink", "DELETE", label)
                break

    def add_author(self, name: str, bio: str, image_url: str):
        auuid = str(uuid.uuid4())
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "AuthorProfile", [auuid, name, bio, image_url])
        self.log_change("AuthorProfile", "ADD", auuid)
        return auuid

    def update_author(self, author_uuid: str, name: str, bio: str, image_url: str):
        recs = self.get_authors()
        for i, r in enumerate(recs):
            if r["author_uuid"] == author_uuid:
                updates = {
                    "name": name,
                    "bio": bio,
                    "image_url": image_url
                }
                MFDBCore.mfdb_core_update_entity_record_bulk(self.global_manifest, "AuthorProfile", i, updates)
                self.log_change("AuthorProfile", "UPDATE", author_uuid)
                break

    def delete_author(self, author_uuid: str):
        recs = self.get_authors()
        for i, r in enumerate(recs):
            if r["author_uuid"] == author_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.global_manifest, "AuthorProfile", i)
                self.log_change("AuthorProfile", "DELETE", author_uuid)
                break

    def get_authors(self) -> List[Dict]: return MFDBCore.mfdb_core_load_entity(self.global_manifest, "AuthorProfile")

    def add_ad(self, name: str, img: str, link: str, zone: str, active: bool = True):
        auuid = str(uuid.uuid4())
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "AdUnit", [auuid, name, img, link, zone, active])
        self.log_change("AdUnit", "ADD", auuid)
        return auuid

    def add_asset(self, filename: str, original_name: str, file_hash: str, file_size: int, mime_type: str, folder: str = ""):
        """Registers an asset that has already been saved to the assets directory."""
        uploaded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "MediaAsset", [filename, original_name, file_hash, file_size, mime_type, uploaded_at, folder])
        self.log_change("MediaAsset", "ADD", filename)
        return filename

    def delete_asset(self, filename: str):
        recs = MFDBCore.mfdb_core_load_entity(self.global_manifest, "MediaAsset")
        for i, r in enumerate(recs):
            if r["filename"] == filename:
                MFDBCore.mfdb_core_remove_entity_record(self.global_manifest, "MediaAsset", i)
                fpath = os.path.join(self.assets_dir, filename)
                if os.path.exists(fpath): os.remove(fpath)
                self.log_change("MediaAsset", "DELETE", filename)
                return True
        return False

    def add_category(self, name: str, slug: str, description: str = "", feed_type: str = "blog"):
        MFDBCore.mfdb_core_add_entity_record(self.content_manifest, "Category", [name, slug, description, feed_type])
        self.log_change("Category", "ADD", slug)

    def update_category(self, slug: str, name: str, description: str = None, feed_type: str = None):
        recs = self.get_categories()
        for i, r in enumerate(recs):
            if r["category_slug"] == slug:
                updates = {"category_name": name}
                if description is not None: updates["description"] = description
                if feed_type is not None: updates["feed_type"] = feed_type
                MFDBCore.mfdb_core_update_entity_record_bulk(self.content_manifest, "Category", i, updates)
                self.log_change("Category", "UPDATE", slug)
                break

    def _unique_page_slug(self, base_slug: str, category_slug: str, exclude_uuid: str = None) -> str:
        """BUGFIX (2026-08-11, audit M6): two pages with the same title in
        the same category previously got the same slug, and _build_page
        silently overwrote the first page's built index.html with the
        second's (os.makedirs(..., exist_ok=True)) while both remained in
        the DB. Appends -2, -3, ... until the slug is unique within the
        target category. exclude_uuid lets update_page re-check a page's
        own existing slug without colliding with itself."""
        existing = {
            r["slug"] for r in MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
            if r.get("category_fk") == category_slug and r.get("page_uuid") != exclude_uuid
        }
        if base_slug not in existing:
            return base_slug
        n = 2
        while f"{base_slug}-{n}" in existing:
            n += 1
        return f"{base_slug}-{n}"

    def create_page(self, title: str, category_slug: str, page_type: str, content_data: Dict[str, Any]) -> str:
        page_uuid = str(uuid.uuid4())
        page_slug = self._unique_page_slug(bejson_utility_slugify(title), category_slug)
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MFDBCore.mfdb_core_add_entity_record(self.content_manifest, "Page", [page_uuid, title, page_slug, category_slug, content_data.get("author_fk", ""), page_type, content_data.get("featured_img"), created_at])
        content_values = [page_uuid, content_data.get("html_body", ""), content_data.get("markdown_body", ""), content_data.get("source_files", []), content_data.get("video_url", ""), content_data.get("pdf_url", ""), content_data.get("pros", []), content_data.get("cons", []), content_data.get("verdict_score", 0.0)]
        MFDBCore.mfdb_core_add_entity_record(self.content_manifest, "PageContent", content_values)
        self.log_change("Page", "ADD", page_uuid)
        return page_uuid

    def update_page(self, page_uuid: str, title: str, category_slug: str, page_type: str, content_data: Dict[str, Any]):
        recs = MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
        for i, r in enumerate(recs):
            if r["page_uuid"] == page_uuid:
                # BUGFIX (2026-08-11, audit M6): slug was never regenerated
                # when the title (or category) changed, so a renamed page
                # kept building at its old URL while a NEW page with the
                # renamed title's slug would silently collide with it.
                new_slug = self._unique_page_slug(bejson_utility_slugify(title), category_slug, exclude_uuid=page_uuid)
                MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "Page", i, "title", title)
                MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "Page", i, "slug", new_slug)
                MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "Page", i, "category_fk", category_slug)
                MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "Page", i, "page_type", page_type)
                self.log_change("Page", "UPDATE", page_uuid)
                break
        crecs = MFDBCore.mfdb_core_load_entity(self.content_manifest, "PageContent")
        for i, r in enumerate(crecs):
            if r["page_uuid_fk"] == page_uuid:
                for key in ["html_body", "markdown_body", "source_files", "video_url", "pdf_url", "pros", "cons", "verdict_score"]:
                    if key in content_data: MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "PageContent", i, key, content_data[key])
                break

    def delete_page(self, page_uuid: str):
        # 1. Remove from Page entity
        pages = MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
        for i, p in enumerate(pages):
            if p.get("page_uuid") == page_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.content_manifest, "Page", i)
                break
        
        # 2. Remove from PageContent entity
        contents = MFDBCore.mfdb_core_load_entity(self.content_manifest, "PageContent")
        for i, c in enumerate(contents):
            if c.get("page_uuid_fk") == page_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.content_manifest, "PageContent", i)
                break
        self.log_change("Page", "DELETE", page_uuid)

    def delete_category(self, slug: str):
        # BUGFIX (2026-08-11, audit M7): deleting a category used to leave
        # its pages with a dangling category_fk, silently dropping them
        # from every feed - the same trap pkg19 already fixed for blank
        # categories, just not on this path. Reassign members to
        # "uncategorized" first (skip if the category being deleted IS
        # uncategorized itself - that one should never be removable via
        # this path in the first place, but guard against it regardless).
        if slug != "uncategorized":
            pages = MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
            for i, p in enumerate(pages):
                if p.get("category_fk") == slug:
                    MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "Page", i, "category_fk", "uncategorized")
            self.log_change("Page", "REASSIGN_ORPHANS", slug + " -> uncategorized")

        recs = MFDBCore.mfdb_core_load_entity(self.content_manifest, "Category")
        for i, r in enumerate(recs):
            if r.get("category_slug") == slug:
                MFDBCore.mfdb_core_remove_entity_record(self.content_manifest, "Category", i)
                break
        self.log_change("Category", "DELETE", slug)

    def delete_ad(self, ad_uuid: str):
        recs = self.get_ads()
        for i, r in enumerate(recs):
            if r.get("ad_uuid") == ad_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.global_manifest, "AdUnit", i)
                self.log_change("AdUnit", "DELETE", ad_uuid)
                break

    def update_ad(self, ad_uuid: str, name: str, img: str, link: str, zone: str, active: bool = True):
        recs = self.get_ads()
        for i, r in enumerate(recs):
            if r["ad_uuid"] == ad_uuid:
                updates = {
                    "name": name,
                    "image_url": img,
                    "link_url": link,
                    "zone": zone,
                    "active": active
                }
                MFDBCore.mfdb_core_update_entity_record_bulk(self.global_manifest, "AdUnit", i, updates)
                self.log_change("AdUnit", "UPDATE", ad_uuid)
                break

    def delete_app(self, app_uuid: str):
        recs = MFDBCore.mfdb_core_load_entity(self.content_manifest, "StandaloneApp")
        for i, r in enumerate(recs):
            if r["app_uuid"] == app_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.content_manifest, "StandaloneApp", i)
                self.log_change("StandaloneApp", "DELETE", app_uuid)
                break

    # -----------------------------------------------------------------------
    # Read helpers — not yet in upstream lib; required by Flask routes
    # -----------------------------------------------------------------------

    def get_ads(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.global_manifest, "AdUnit")

    def get_nav_links(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.global_manifest, "NavLink")

    def add_video_asset(self, url: str, title: str = "") -> Optional[str]:
        """Registers a YouTube video by URL. Returns the new video_uuid, or
        None if the URL couldn't be parsed for a video ID."""
        video_id = bejson_cms_extract_youtube_id(url)
        if not video_id:
            return None
        video_uuid = str(uuid.uuid4())
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        added_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "VideoAsset",
            [video_uuid, url, video_id, "youtube", title, thumbnail_url, added_at])
        self.log_change("VideoAsset", "ADD", video_uuid)
        return video_uuid

    def delete_video_asset(self, video_uuid: str) -> bool:
        recs = MFDBCore.mfdb_core_load_entity(self.global_manifest, "VideoAsset")
        for i, r in enumerate(recs):
            if r["video_uuid"] == video_uuid:
                MFDBCore.mfdb_core_remove_entity_record(self.global_manifest, "VideoAsset", i)
                self.log_change("VideoAsset", "DELETE", video_uuid)
                return True
        return False

    def get_video_assets(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.global_manifest, "VideoAsset")

    def get_assets(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.global_manifest, "MediaAsset")

    def get_asset_by_hash(self, file_hash: str) -> Optional[Dict]:
        return next((a for a in self.get_assets() if a["file_hash"] == file_hash), None)

    def get_file_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_apps(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.content_manifest, "StandaloneApp")

    def get_pages(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")

    def get_categories(self) -> List[Dict]:
        return MFDBCore.mfdb_core_load_entity(self.content_manifest, "Category")

    def get_pages_in_category(self, category_slug: str) -> List[Dict]:
        return [p for p in MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
                if p.get("category_fk") == category_slug]

    def get_apps_in_category(self, category_slug: str) -> List[Dict]:
        return [a for a in self.get_apps() if a.get("category_fk") == category_slug]

    def get_full_page_data(self, page_uuid: str) -> Optional[Dict]:
        pages = MFDBCore.mfdb_core_load_entity(self.content_manifest, "Page")
        page = next((p for p in pages if p.get("page_uuid") == page_uuid), None)
        if not page:
            return None
        contents = MFDBCore.mfdb_core_load_entity(self.content_manifest, "PageContent")
        content = next((c for c in contents if c.get("page_uuid_fk") == page_uuid), {})
        return {**page, **content}

    def create_app(self, name: str, description: str, category: str,
                   featured_img: str, entry_file: str):
        app_uuid   = str(uuid.uuid4())
        slug       = bejson_utility_slugify(name)
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MFDBCore.mfdb_core_add_entity_record(
            self.content_manifest, "StandaloneApp",
            [app_uuid, name, slug, description, category, featured_img, entry_file, created_at]
        )
        self.log_change("StandaloneApp", "ADD", app_uuid)
        return app_uuid

    def import_html_as_page(self, file_path: str, category: str, author_uuid: str = "", fallback_title: str = ""):
        """Imports an HTML file as a new CMS page. Title is auto-detected
        from <title>, then the first <h1>; fallback_title (e.g. derived from
        the original filename) is used only if neither is present.

        SECURITY (2026-08-11, audit finding C2): html_body is rendered on
        every built page via `{{ html_body | safe }}`, so it must never
        contain scripts or event handlers from an imported (untrusted)
        file. _sanitize_imported_html() strips scripts/styles/AI-watermark
        cruft before the title-detect pass runs, restoring the pipeline
        that documentation (README/usage-guide) already claimed existed."""
        path = Path(file_path)
        if not path.exists(): return None

        content = path.read_text(encoding="utf-8")
        content = self._sanitize_imported_html(content)
        body_match = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL | re.IGNORECASE)
        html_body = body_match.group(1) if body_match else content

        title = ""
        title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.DOTALL | re.IGNORECASE)
        if title_match:
            title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        if not title:
            h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_body, re.DOTALL | re.IGNORECASE)
            if h1_match:
                title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h1_match.group(1))).strip()
        if not title:
            title = fallback_title.strip() if fallback_title else "Untitled Page"

        return self.create_page(title, category, "blog", {"html_body": html_body, "author_fk": author_uuid})

    _AI_WATERMARK_PATTERNS = (
        re.compile(r"generated by\s+\w+", re.IGNORECASE),
        re.compile(r"created with\s+\w+\s+ai", re.IGNORECASE),
        re.compile(r"powered by\s+chatgpt|powered by\s+claude|powered by\s+gemini", re.IGNORECASE),
    )

    @staticmethod
    def _sanitize_imported_html(content: str) -> str:
        """Strips scripts, styles, event-handler attributes, javascript:/data:
        URLs, MS-Word cruft (Mso* classes, mso- inline styles, <o:p> tags,
        conditional comments), and short AI-tool watermark footers from an
        imported HTML document. Returns cleaned HTML source (still a full
        document; caller extracts <body> separately)."""
        soup = BeautifulSoup(content, "html.parser")

        # Scripts / styles / anything that can execute or load external code.
        for tag in soup(["script", "style", "noscript", "link", "meta", "iframe", "object", "embed"]):
            tag.decompose()

        # Event-handler attributes and javascript:/data: URLs on every tag.
        for tag in soup.find_all(True):
            for attr in list(tag.attrs):
                if attr.lower().startswith("on"):
                    del tag.attrs[attr]
            for url_attr in ("href", "src", "action", "formaction"):
                val = tag.attrs.get(url_attr)
                if isinstance(val, str) and val.strip().lower().startswith(("javascript:", "data:text/html")):
                    del tag.attrs[url_attr]
            # Word-specific cruft
            cls = tag.attrs.get("class")
            if cls and any(str(c).lower().startswith("mso") for c in (cls if isinstance(cls, list) else [cls])):
                del tag.attrs["class"]
            style = tag.attrs.get("style")
            if style and "mso-" in style.lower():
                tag.attrs["style"] = "; ".join(
                    p for p in style.split(";") if "mso-" not in p.lower()
                ).strip("; ")

        # <o:p> (Word paragraph markers) and MS conditional comments.
        for tag in soup.find_all(re.compile(r"^o:", re.IGNORECASE)):
            tag.unwrap()
        for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
            comment.extract()

        cleaned = str(soup)

        # Short AI-tool watermark footer lines (e.g. "Generated by X").
        lines = cleaned.splitlines()
        kept = []
        for line in lines:
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text and len(text) < 80 and any(p.search(text) for p in MFDB_CMS_Manager._AI_WATERMARK_PATTERNS):
                continue
            kept.append(line)
        return "\n".join(kept)

    def import_app_as_page(self, app_uuid: str, author_uuid: str = ""):
        """Wraps a StandaloneApp in a CMS page."""
        apps = self.get_apps()
        app = next((a for a in apps if a["app_uuid"] == app_uuid), None)
        if not app: return None
        
        content = {
            "html_body": f'<iframe src="{app["entry_file"]}" style="width:100%; height:80vh; border:none;"></iframe>',
            "author_fk": author_uuid
        }
        return self.create_page(f"App: {app['name']}", app["category_fk"], "app", content)

    def optimize_assets(self, convert_webp: bool = True):
        """Converts PNGs to WebP and updates all database references."""
        try:
            from PIL import Image
        except ImportError:
            print("Error: Pillow library required for image optimization.")
            return False
            
        recs = self.get_assets()
        updated_paths = {}
        
        for r in recs:
            filename = r["filename"]
            if convert_webp and filename.lower().endswith(".png"):
                old_path = os.path.join(self.assets_dir, filename)
                new_filename = filename.rsplit(".", 1)[0] + ".webp"
                new_path = os.path.join(self.assets_dir, new_filename)
                
                if os.path.exists(old_path):
                    try:
                        img = Image.open(old_path)
                        img.save(new_path, "webp")
                        
                        # Update registry
                        file_size = os.path.getsize(new_path)
                        with open(new_path, "rb") as f:
                            file_hash = self.get_file_hash(f.read())
                        
                        # Add new record directly (avoid redundant copy)
                        uploaded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                        # BUGFIX (2026-08-11, audit H2): this call was 6
                        # values against a 7-field MediaAsset schema
                        # (missing "folder"), so it silently failed the
                        # length check on any install with the folder
                        # field present. Preserve the source record's
                        # folder value instead of dropping it.
                        MFDBCore.mfdb_core_add_entity_record(self.global_manifest, "MediaAsset", [new_filename, r["original_name"], file_hash, file_size, "image/webp", uploaded_at, r.get("folder")])
                        
                        # Delete old
                        self.delete_asset(filename)
                        updated_paths[filename] = new_filename
                        print(f"Optimized: {filename} -> {new_filename}")
                    except Exception as e:
                        print(f"Failed to optimize {filename}: {e}")
        
        # Update PageContent references
        if updated_paths:
            page_contents = MFDBCore.mfdb_core_load_entity(self.content_manifest, "PageContent")
            for i, pc in enumerate(page_contents):
                body = pc.get("html_body", "")
                md_body = pc.get("markdown_body", "")
                changed = False
                for old, new in updated_paths.items():
                    if old in body:
                        body = body.replace(old, new)
                        changed = True
                    if md_body and old in md_body:
                        md_body = md_body.replace(old, new)
                        changed = True
                
                if changed:
                    MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "PageContent", i, "html_body", body)
                    if md_body:
                        MFDBCore.mfdb_core_update_entity_record(self.content_manifest, "PageContent", i, "markdown_body", md_body)
            print(f"Updated references for {len(updated_paths)} assets across pages.")
        return True

    def create_site_backup(self, backup_dir: str) -> Optional[str]:
        """Creates a full site backup zip containing DBs, assets, and apps."""
        if self.is_dirty():
            self.repack_system()
            
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"bejson_cms_backup_{ts}.zip"
        backup_path = os.path.join(backup_dir, backup_name)
        
        os.makedirs(backup_dir, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add DB Archives
            if os.path.exists(self.global_archive):
                zf.write(self.global_archive, "global_master.mfdb.zip")
            if os.path.exists(self.content_archive):
                zf.write(self.content_archive, "content_master.mfdb.zip")
            
            # Add Assets
            for root, _, files in os.walk(self.assets_dir):
                for file in files:
                    fpath = os.path.join(root, file)
                    zf.write(fpath, os.path.join("assets", os.path.relpath(fpath, self.assets_dir)))
            
            # Add Apps
            for root, _, files in os.walk(self.apps_dir):
                for file in files:
                    fpath = os.path.join(root, file)
                    zf.write(fpath, os.path.join("standalone_apps", os.path.relpath(fpath, self.apps_dir)))
                    
        return backup_path

    def restore_site_backup(self, backup_path: str) -> bool:
        """Restores a full site backup."""
        if not os.path.exists(backup_path):
            return False
            
        # 1. Clear Workspace
        if os.path.exists(self.workspace_root):
            shutil.rmtree(self.workspace_root)
        os.makedirs(self.workspace_root, exist_ok=True)
        
        # 2. Extract Archive
        with zipfile.ZipFile(backup_path, 'r') as zf:
            # Restore Databases
            for db_zip in ["global_master.mfdb.zip", "content_master.mfdb.zip"]:
                if db_zip in zf.namelist():
                    # R5-NEW-08: validate AND use the validated path for extraction
                    target = bejson_safe_join(self.data_root, db_zip)  # raises on traversal
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with zf.open(db_zip) as src, open(target, 'wb') as dst:
                        dst.write(src.read())
                
            # Restore Assets
            if os.path.exists(self.assets_dir): shutil.rmtree(self.assets_dir)
            for item in zf.namelist():
                if item.startswith("assets/"):
                    # R5-NEW-08: validated path is now actually used for extraction
                    target = bejson_safe_join(self.data_root, item)  # raises on traversal
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    if not item.endswith('/'):
                        with zf.open(item) as src, open(target, 'wb') as dst:
                            dst.write(src.read())
                    
            # Restore Apps
            if os.path.exists(self.apps_dir): shutil.rmtree(self.apps_dir)
            for item in zf.namelist():
                if item.startswith("standalone_apps/"):
                    # R5-NEW-08: validated path is now actually used for extraction
                    target = bejson_safe_join(self.data_root, item)  # raises on traversal
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    if not item.endswith('/'):
                        with zf.open(item) as src, open(target, 'wb') as dst:
                            dst.write(src.read())
                    
        # 3. Re-mount
        self.mount_system(force=True)
        return True
