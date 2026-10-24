#!/usr/bin/env python3
"""
Name: migrate_taxonomy_v2.py
Description: Data Migration Script upgrading Experimental CMS MFDB storage layer to Taxonomy v2.0 (Policy §10.1, §10.2, §10.3).
Version: 2.0.0
Author Credit: Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
RELATIONAL_ID: 8d1c7e94-3a55-4e78-9b1d-2f08a47cd3ef
"""
import os
import sys
import json
import uuid
import shutil
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

def get_script_path() -> Path:
    return Path(__file__).resolve().parent

SCRIPT_PATH = get_script_path()
REPO_ROOT = SCRIPT_PATH.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TaxonomyMigratorV2")

DATA_DIR = REPO_ROOT / "Data" / "workspace"
DB_CONTENT_DIR = DATA_DIR / "db_content"
DB_GLOBAL_DIR = DATA_DIR / "db_global"

UNCATEGORIZED_STATIC_UUID = "00000000-0000-0000-0000-000000000001"


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def backup_file(file_path: Path):
    bak_path = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copyfile(file_path, bak_path)
    logger.info("Backup created: %s -> %s", file_path.name, bak_path.name)


def load_bejson(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_bejson(file_path: Path, doc: Dict[str, Any]):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    logger.info("Saved updated BEJSON: %s", file_path)


def compile_field_map(doc: Dict[str, Any]) -> Dict[str, int]:
    return {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}


def migrate_category_entity(dry_run: bool = False) -> Dict[str, str]:
    """Migrates Category table, injecting category_uuid. Returns slug->uuid mapping."""
    cat_file = DB_CONTENT_DIR / "data" / "category.bejson"
    doc = load_bejson(cat_file)
    f_map = compile_field_map(doc)
    
    slug_to_uuid: Dict[str, str] = {}
    new_values = []
    now_iso = get_utc_now()

    for row in doc.get("Values", []):
        cat_name = row[f_map["category_name"]]
        cat_slug = str(row[f_map["category_slug"]]).strip()
        cat_desc = row[f_map["description"]] if "description" in f_map else ""
        feed_type = row[f_map["feed_type"]] if "feed_type" in f_map else "article"

        if cat_slug.lower() == "uncategorized":
            cat_uuid = UNCATEGORIZED_STATIC_UUID
        else:
            cat_uuid = str(uuid.uuid4())
        
        slug_to_uuid[cat_slug] = cat_uuid
        slug_to_uuid[cat_slug.lower()] = cat_uuid

        new_values.append([
            cat_uuid,
            cat_name,
            cat_slug,
            cat_desc,
            feed_type,
            now_iso,
            now_iso
        ])

    doc["Fields"] = [
        {"name": "category_uuid", "type": "string"},
        {"name": "category_name", "type": "string"},
        {"name": "category_slug", "type": "string"},
        {"name": "category_description", "type": "string"},
        {"name": "category_feed_type", "type": "string"},
        {"name": "category_created_at", "type": "string"},
        {"name": "category_updated_at", "type": "string"}
    ]
    doc["Values"] = new_values

    logger.info("Category table migrated: %d categories mapped.", len(new_values))
    if not dry_run:
        backup_file(cat_file)
        save_bejson(cat_file, doc)

    return slug_to_uuid


def migrate_page_entity(slug_to_uuid: Dict[str, str], dry_run: bool = False):
    """Migrates Page table, translating category_fk to UUID and normalizing prefixes."""
    page_file = DB_CONTENT_DIR / "data" / "page.bejson"
    doc = load_bejson(page_file)
    f_map = compile_field_map(doc)

    new_values = []
    now_iso = get_utc_now()

    for row in doc.get("Values", []):
        p_uuid = row[f_map["page_uuid"]]
        p_title = row[f_map["title"]]
        p_slug = row[f_map["slug"]]
        raw_cat = str(row[f_map["category_fk"]] or "").strip()
        cat_fk = slug_to_uuid.get(raw_cat, slug_to_uuid.get(raw_cat.lower(), UNCATEGORIZED_STATIC_UUID))
        author_fk = row[f_map["author_fk"]] or ""
        p_type = row[f_map["page_type"]]
        feat_img = row[f_map["featured_img"]] if "featured_img" in f_map else ""
        p_created = row[f_map["created_at"]] if "created_at" in f_map else now_iso

        new_values.append([
            p_uuid,
            cat_fk,
            author_fk,
            feat_img,
            p_title,
            p_slug,
            p_type,
            p_created,
            now_iso
        ])

    doc["Fields"] = [
        {"name": "page_uuid", "type": "string"},
        {"name": "category_fk", "type": "string"},
        {"name": "author_fk", "type": "string"},
        {"name": "page_featured_asset_fk", "type": "string"},
        {"name": "page_title", "type": "string"},
        {"name": "page_slug", "type": "string"},
        {"name": "page_type", "type": "string"},
        {"name": "page_created_at", "type": "string"},
        {"name": "page_updated_at", "type": "string"}
    ]
    doc["Values"] = new_values

    logger.info("Page table migrated: %d pages remapped to category UUIDs.", len(new_values))
    if not dry_run:
        backup_file(page_file)
        save_bejson(page_file, doc)


def migrate_pagecontent_entity(dry_run: bool = False):
    """Migrates PageContent table, adding content_uuid and page_fk."""
    content_file = DB_CONTENT_DIR / "data" / "pagecontent.bejson"
    doc = load_bejson(content_file)
    f_map = compile_field_map(doc)

    new_values = []
    now_iso = get_utc_now()

    for row in doc.get("Values", []):
        page_fk = row[f_map.get("page_uuid_fk", f_map.get("page_fk", 0))]
        html_body = row[f_map.get("html_body", 1)]
        markdown_body = row[f_map.get("markdown_body", 2)] if "markdown_body" in f_map else ""
        source_files = row[f_map.get("source_files", 3)] if "source_files" in f_map else []
        video_url = row[f_map.get("video_url", 4)] if "video_url" in f_map else ""
        pdf_url = row[f_map.get("pdf_url", 5)] if "pdf_url" in f_map else ""
        content_uuid = str(uuid.uuid4())

        new_values.append([
            content_uuid,
            page_fk,
            html_body,
            markdown_body,
            source_files,
            video_url,
            pdf_url,
            now_iso
        ])

    doc["Fields"] = [
        {"name": "content_uuid", "type": "string"},
        {"name": "page_fk", "type": "string"},
        {"name": "content_html_body", "type": "string"},
        {"name": "content_markdown_body", "type": "string"},
        {"name": "content_source_files", "type": "array"},
        {"name": "content_video_url", "type": "string"},
        {"name": "content_pdf_url", "type": "string"},
        {"name": "content_updated_at", "type": "string"}
    ]
    doc["Values"] = new_values

    logger.info("PageContent table migrated: %d content records assigned content_uuid.", len(new_values))
    if not dry_run:
        backup_file(content_file)
        save_bejson(content_file, doc)


def migrate_standaloneapp_entity(slug_to_uuid: Dict[str, str], dry_run: bool = False):
    """Migrates StandaloneApp table, updating category_fk and column prefixes."""
    app_file = DB_CONTENT_DIR / "data" / "standaloneapp.bejson"
    if not app_file.exists():
        return
    doc = load_bejson(app_file)
    f_map = compile_field_map(doc)

    new_values = []
    now_iso = get_utc_now()

    for row in doc.get("Values", []):
        a_uuid = row[f_map["app_uuid"]]
        a_name = row[f_map.get("name", f_map.get("app_name", 1))]
        a_slug = row[f_map.get("slug", f_map.get("app_slug", 2))]
        raw_cat = str(row[f_map.get("category", f_map.get("app_category_fk", 3))] or "").strip()
        cat_fk = slug_to_uuid.get(raw_cat, slug_to_uuid.get(raw_cat.lower(), UNCATEGORIZED_STATIC_UUID))
        entry_file = row[f_map.get("entry_file", f_map.get("app_entry_file", 4))]
        desc = row[f_map.get("description", f_map.get("app_description", 5))]
        created_at = row[f_map.get("created_at", f_map.get("app_created_at", 6))] if "created_at" in f_map else now_iso

        new_values.append([
            a_uuid,
            cat_fk,
            "",
            a_name,
            a_slug,
            entry_file,
            desc,
            created_at
        ])

    doc["Fields"] = [
        {"name": "app_uuid", "type": "string"},
        {"name": "app_category_fk", "type": "string"},
        {"name": "app_icon_asset_fk", "type": "string"},
        {"name": "app_name", "type": "string"},
        {"name": "app_slug", "type": "string"},
        {"name": "app_entry_file", "type": "string"},
        {"name": "app_description", "type": "string"},
        {"name": "app_created_at", "type": "string"}
    ]
    doc["Values"] = new_values

    logger.info("StandaloneApp table migrated: %d app records normalized.", len(new_values))
    if not dry_run:
        backup_file(app_file)
        save_bejson(app_file, doc)


def migrate_navlink_entity(dry_run: bool = False):
    """Migrates NavLink table, adding nav_uuid."""
    nav_file = DB_GLOBAL_DIR / "data" / "navlink.bejson"
    doc = load_bejson(nav_file)
    f_map = compile_field_map(doc)

    new_values = []
    now_iso = get_utc_now()

    for row in doc.get("Values", []):
        label = row[f_map.get("label", f_map.get("nav_label", 0))]
        url = row[f_map.get("url", f_map.get("nav_url", 1))]
        order = row[f_map.get("order", f_map.get("nav_sort_order", 2))]
        nav_uuid = str(uuid.uuid4())

        new_values.append([
            nav_uuid,
            label,
            url,
            order,
            now_iso
        ])

    doc["Fields"] = [
        {"name": "nav_uuid", "type": "string"},
        {"name": "nav_label", "type": "string"},
        {"name": "nav_url", "type": "string"},
        {"name": "nav_sort_order", "type": "integer"},
        {"name": "nav_created_at", "type": "string"}
    ]
    doc["Values"] = new_values

    logger.info("NavLink table migrated: %d nav records assigned nav_uuid.", len(new_values))
    if not dry_run:
        backup_file(nav_file)
        save_bejson(nav_file, doc)


def migrate_sociallink_entity(dry_run: bool = False):
    """Migrates SocialLink table, adding social_uuid."""
    soc_file = DB_GLOBAL_DIR / "data" / "sociallink.bejson"
    doc = load_bejson(soc_file)
    f_map = compile_field_map(doc)

    new_values = []
    idx = 0

    for row in doc.get("Values", []):
        platform = row[f_map.get("platform", f_map.get("social_platform", 0))]
        url = row[f_map.get("url", f_map.get("social_url", 1))]
        icon = row[f_map.get("icon", f_map.get("social_icon_key", 2))]
        social_uuid = str(uuid.uuid4())
        idx += 1

        new_values.append([
            social_uuid,
            platform,
            url,
            icon,
            idx
        ])

    doc["Fields"] = [
        {"name": "social_uuid", "type": "string"},
        {"name": "social_platform", "type": "string"},
        {"name": "social_url", "type": "string"},
        {"name": "social_icon_key", "type": "string"},
        {"name": "social_sort_order", "type": "integer"}
    ]
    doc["Values"] = new_values

    logger.info("SocialLink table migrated: %d social records assigned social_uuid.", len(new_values))
    if not dry_run:
        backup_file(soc_file)
        save_bejson(soc_file, doc)


def update_manifest_primary_keys(dry_run: bool = False):
    """Updates 104a.mfdb.bejson manifests to reflect new primary keys."""
    # Content manifest
    content_manifest_file = DB_CONTENT_DIR / "104a.mfdb.bejson"
    c_doc = load_bejson(content_manifest_file)
    c_fmap = compile_field_map(c_doc)
    c_pk_idx = c_fmap["primary_key"]
    c_name_idx = c_fmap["entity_name"]

    for row in c_doc.get("Values", []):
        entity = row[c_name_idx]
        if entity == "Category":
            row[c_pk_idx] = "category_uuid"
        elif entity == "PageContent":
            row[c_pk_idx] = "content_uuid"

    if not dry_run:
        backup_file(content_manifest_file)
        save_bejson(content_manifest_file, c_doc)

    # Global manifest
    global_manifest_file = DB_GLOBAL_DIR / "104a.mfdb.bejson"
    g_doc = load_bejson(global_manifest_file)
    g_fmap = compile_field_map(g_doc)
    g_pk_idx = g_fmap["primary_key"]
    g_name_idx = g_fmap["entity_name"]

    for row in g_doc.get("Values", []):
        entity = row[g_name_idx]
        if entity == "NavLink":
            row[g_pk_idx] = "nav_uuid"
        elif entity == "SocialLink":
            row[g_pk_idx] = "social_uuid"

    if not dry_run:
        backup_file(global_manifest_file)
        save_bejson(global_manifest_file, g_doc)

    logger.info("MFDB manifests updated with new primary keys.")


def run_migration(dry_run: bool = False):
    logger.info("Starting Taxonomy v2.0 Data Migration (Dry Run: %s)...", dry_run)
    slug_map = migrate_category_entity(dry_run=dry_run)
    migrate_page_entity(slug_map, dry_run=dry_run)
    migrate_pagecontent_entity(dry_run=dry_run)
    migrate_standaloneapp_entity(slug_map, dry_run=dry_run)
    migrate_navlink_entity(dry_run=dry_run)
    migrate_sociallink_entity(dry_run=dry_run)
    update_manifest_primary_keys(dry_run=dry_run)
    logger.info("Taxonomy v2.0 Data Migration Completed Successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experimental CMS Taxonomy v2.0 Migration Script")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifying files on disk")
    args = parser.parse_args()

    run_migration(dry_run=args.dry_run)
