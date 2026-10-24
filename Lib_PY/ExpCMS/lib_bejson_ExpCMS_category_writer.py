"""
Library:        lib_bejson_ExpCMS_category_writer.py
Family:         ExpCMS
Description:    Owning Writer module for Category entity adhering to Policy §10.1, §10.3, §10.4, and §6.2.
Version:        2.0.0
Author:         Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Date:           2026-10-24
RELATIONAL_ID:  5b2e91a0-4c38-4e12-8f92-1a0c4e7b3d11
"""
import os
import sys
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import lib_bejson_Core_bejson_core as BEJSONCore
import lib_bejson_Core_mfdb_core as MFDBCore

logger = logging.getLogger("CategoryWriter")

UNCATEGORIZED_STATIC_UUID = "00000000-0000-0000-0000-000000000001"


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_cell(val: Any) -> Any:
    return val.strip() if isinstance(val, str) else val


class CategoryOwningWriter:
    """Designated Single Write-Owner for Category entity records."""

    def __init__(self, content_manifest_path: str):
        self.manifest_path = content_manifest_path
        self._cached_entity_path: Optional[str] = None
        self._cached_field_map: Optional[Dict[str, int]] = None

    def _resolve_category_file(self) -> str:
        if self._cached_entity_path and os.path.exists(self._cached_entity_path):
            return self._cached_entity_path
        entry = MFDBCore._get_manifest_entry(self.manifest_path, "Category")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        self._cached_entity_path = os.path.normpath(os.path.join(manifest_dir, entry["file_path"]))
        return self._cached_entity_path

    def _get_field_map(self, doc: Dict[str, Any]) -> Dict[str, int]:
        if self._cached_field_map is not None:
            return self._cached_field_map
        self._cached_field_map = {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}
        return self._cached_field_map

    def get_all_categories(self) -> List[Dict[str, Any]]:
        entity_file = self._resolve_category_file()
        doc = MFDBCore.bejson_core_load_file(entity_file)
        f_map = self._get_field_map(doc)
        results = []
        for row in doc.get("Values", []):
            rec = {col: _sanitize_cell(row[idx]) for col, idx in f_map.items()}
            # Backwards compatibility aliases
            rec["slug"] = rec.get("category_slug")
            rec["name"] = rec.get("category_name")
            rec["description"] = rec.get("category_description")
            rec["feed_type"] = rec.get("category_feed_type")
            results.append(rec)
        return results

    def get_category_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        clean_slug = slug.strip().lower()
        for cat in self.get_all_categories():
            if str(cat.get("category_slug", "")).strip().lower() == clean_slug:
                return cat
        return None

    def get_category_by_uuid(self, category_uuid: str) -> Optional[Dict[str, Any]]:
        clean_uuid = category_uuid.strip()
        for cat in self.get_all_categories():
            if str(cat.get("category_uuid", "")).strip() == clean_uuid:
                return cat
        return None

    def create_category(self, name: str, slug: str, description: str = "", feed_type: str = "article") -> Dict[str, Any]:
        clean_name = name.strip()
        clean_slug = slug.strip()
        clean_desc = description.strip()
        clean_feed = feed_type.strip() or "article"

        existing = self.get_category_by_slug(clean_slug)
        if existing:
            raise ValueError(f"Category with slug '{clean_slug}' already exists (UUID: {existing['category_uuid']}).")

        category_uuid = UNCATEGORIZED_STATIC_UUID if clean_slug.lower() == "uncategorized" else str(uuid.uuid4())
        now_iso = get_utc_now()

        entity_file = self._resolve_category_file()
        doc = MFDBCore.bejson_core_load_file(entity_file)
        f_map = self._get_field_map(doc)

        new_row = [None] * len(f_map)
        new_row[f_map["category_uuid"]] = category_uuid
        new_row[f_map["category_name"]] = clean_name
        new_row[f_map["category_slug"]] = clean_slug
        new_row[f_map["category_description"]] = clean_desc
        new_row[f_map["category_feed_type"]] = clean_feed
        new_row[f_map["category_created_at"]] = now_iso
        new_row[f_map["category_updated_at"]] = now_iso

        doc.setdefault("Values", []).append(new_row)
        BEJSONCore.bejson_core_atomic_write(entity_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "Category", len(doc["Values"]))

        logger.info("Created Category: %s (%s, UUID: %s)", clean_name, clean_slug, category_uuid)
        return {
            "category_uuid": category_uuid,
            "category_name": clean_name,
            "category_slug": clean_slug,
            "category_description": clean_desc,
            "category_feed_type": clean_feed,
            "category_created_at": now_iso,
            "category_updated_at": now_iso
        }

    def update_category(self, identifier: str, name: str, description: str = None, feed_type: str = None) -> bool:
        entity_file = self._resolve_category_file()
        doc = MFDBCore.bejson_core_load_file(entity_file)
        f_map = self._get_field_map(doc)

        clean_id = identifier.strip().lower()
        target_idx = None
        for i, row in enumerate(doc.get("Values", [])):
            row_uuid = str(row[f_map["category_uuid"]]).strip().lower()
            row_slug = str(row[f_map["category_slug"]]).strip().lower()
            if row_uuid == clean_id or row_slug == clean_id:
                target_idx = i
                break

        if target_idx is None:
            return False

        now_iso = get_utc_now()
        doc["Values"][target_idx][f_map["category_name"]] = name.strip()
        if description is not None:
            doc["Values"][target_idx][f_map["category_description"]] = description.strip()
        if feed_type is not None:
            doc["Values"][target_idx][f_map["category_feed_type"]] = feed_type.strip()
        doc["Values"][target_idx][f_map["category_updated_at"]] = now_iso

        BEJSONCore.bejson_core_atomic_write(entity_file, doc)
        logger.info("Updated Category at index %d: %s", target_idx, identifier)
        return True

    def delete_category(self, identifier: str) -> bool:
        clean_id = identifier.strip().lower()
        if clean_id == "uncategorized" or clean_id == UNCATEGORIZED_STATIC_UUID:
            raise ValueError("The default category 'uncategorized' cannot be deleted.")

        entity_file = self._resolve_category_file()
        doc = MFDBCore.bejson_core_load_file(entity_file)
        f_map = self._get_field_map(doc)

        target_idx = None
        target_uuid = None
        for i, row in enumerate(doc.get("Values", [])):
            row_uuid = str(row[f_map["category_uuid"]]).strip().lower()
            row_slug = str(row[f_map["category_slug"]]).strip().lower()
            if row_uuid == clean_id or row_slug == clean_id:
                target_idx = i
                target_uuid = row[f_map["category_uuid"]]
                break

        if target_idx is None:
            return False

        # Cascade SET DEFAULT: reassign any orphaned pages to uncategorized static UUID
        page_entry = MFDBCore._get_manifest_entry(self.manifest_path, "Page")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        page_file = os.path.normpath(os.path.join(manifest_dir, page_entry["file_path"]))
        page_doc = MFDBCore.bejson_core_load_file(page_file)
        page_fmap = {f["name"].strip(): idx for idx, f in enumerate(page_doc.get("Fields", []))}

        cat_col_idx = page_fmap["category_fk"]
        pages_reassigned = 0
        for p_row in page_doc.get("Values", []):
            curr_fk = str(p_row[cat_col_idx]).strip()
            if curr_fk == target_uuid or curr_fk == clean_id:
                p_row[cat_col_idx] = UNCATEGORIZED_STATIC_UUID
                pages_reassigned += 1

        if pages_reassigned > 0:
            BEJSONCore.bejson_core_atomic_write(page_file, page_doc)
            logger.info("Cascade SET DEFAULT: Reassigned %d orphaned page(s) to uncategorized.", pages_reassigned)

        # Remove category record
        doc["Values"].pop(target_idx)
        BEJSONCore.bejson_core_atomic_write(entity_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "Category", len(doc["Values"]))
        logger.info("Deleted Category: %s", identifier)
        return True
