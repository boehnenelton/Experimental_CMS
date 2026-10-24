"""
Library:        lib_bejson_ExpCMS_author_writer.py
Family:         ExpCMS
Description:    Owning Writer module for AuthorProfile entity adhering to Policy §10.1, §10.3, §10.4, and §6.2.
Version:        2.0.0
Author:         Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Date:           2026-10-24
RELATIONAL_ID:  7a3d9021-1b22-4e33-8a12-9c5d8e2a6b01
"""
import os
import sys
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import lib_bejson_Core_bejson_core as BEJSONCore
import lib_bejson_Core_mfdb_core as MFDBCore

logger = logging.getLogger("AuthorWriter")


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_cell(val: Any) -> Any:
    return val.strip() if isinstance(val, str) else val


class AuthorOwningWriter:
    """Designated Single Write-Owner for AuthorProfile entity records."""

    def __init__(self, global_manifest_path: str):
        self.manifest_path = global_manifest_path
        self._cached_author_file: Optional[str] = None
        self._cached_fmap: Optional[Dict[str, int]] = None

    def _resolve_author_file(self) -> str:
        if self._cached_author_file and os.path.exists(self._cached_author_file):
            return self._cached_author_file
        entry = MFDBCore._get_manifest_entry(self.manifest_path, "AuthorProfile")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        self._cached_author_file = os.path.normpath(os.path.join(manifest_dir, entry["file_path"]))
        return self._cached_author_file

    def _get_field_map(self, doc: Dict[str, Any]) -> Dict[str, int]:
        if self._cached_fmap is not None:
            return self._cached_fmap
        self._cached_fmap = {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}
        return self._cached_fmap

    def get_all_authors(self) -> List[Dict[str, Any]]:
        author_file = self._resolve_author_file()
        doc = MFDBCore.bejson_core_load_file(author_file)
        f_map = self._get_field_map(doc)
        results = []
        for row in doc.get("Values", []):
            rec = {col: _sanitize_cell(row[idx]) for col, idx in f_map.items()}
            # Backwards compatibility aliases
            rec["name"] = rec.get("author_name") or rec.get("name")
            rec["bio"] = rec.get("author_bio") or rec.get("bio")
            rec["image_url"] = rec.get("author_avatar_asset_fk") or rec.get("image_url") or ""
            results.append(rec)
        return results

    def get_author_by_uuid(self, author_uuid: str) -> Optional[Dict[str, Any]]:
        clean_uuid = author_uuid.strip()
        for a in self.get_all_authors():
            if a.get("author_uuid") == clean_uuid:
                return a
        return None

    def create_author(self, name: str, bio: str = "", avatar_asset_fk: str = "") -> Dict[str, Any]:
        clean_name = name.strip()
        clean_bio = bio.strip()
        clean_avatar = avatar_asset_fk.strip()
        author_uuid = str(uuid.uuid4())
        now_iso = get_utc_now()

        author_file = self._resolve_author_file()
        doc = MFDBCore.bejson_core_load_file(author_file)
        f_map = self._get_field_map(doc)

        new_row = [None] * len(f_map)
        new_row[f_map["author_uuid"]] = author_uuid
        
        name_idx = f_map.get("author_name", f_map.get("name", 1))
        new_row[name_idx] = clean_name
        
        bio_idx = f_map.get("author_bio", f_map.get("bio", 2))
        new_row[bio_idx] = clean_bio
        
        img_idx = f_map.get("author_avatar_asset_fk", f_map.get("image_url", 3))
        new_row[img_idx] = clean_avatar

        if "author_created_at" in f_map:
            new_row[f_map["author_created_at"]] = now_iso

        doc.setdefault("Values", []).append(new_row)
        BEJSONCore.bejson_core_atomic_write(author_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "AuthorProfile", len(doc["Values"]))

        logger.info("Created Author: %s (UUID: %s)", clean_name, author_uuid)
        return {
            "author_uuid": author_uuid,
            "author_name": clean_name,
            "author_bio": clean_bio,
            "author_avatar_asset_fk": clean_avatar,
            "author_created_at": now_iso
        }

    def update_author(self, author_uuid: str, name: str, bio: str = None, avatar_asset_fk: str = None) -> bool:
        clean_uuid = author_uuid.strip()
        author_file = self._resolve_author_file()
        doc = MFDBCore.bejson_core_load_file(author_file)
        f_map = self._get_field_map(doc)

        target_idx = None
        for i, row in enumerate(doc.get("Values", [])):
            if str(row[f_map["author_uuid"]]).strip() == clean_uuid:
                target_idx = i
                break

        if target_idx is None:
            return False

        name_idx = f_map.get("author_name", f_map.get("name", 1))
        doc["Values"][target_idx][name_idx] = name.strip()

        if bio is not None:
            bio_idx = f_map.get("author_bio", f_map.get("bio", 2))
            doc["Values"][target_idx][bio_idx] = bio.strip()

        if avatar_asset_fk is not None:
            img_idx = f_map.get("author_avatar_asset_fk", f_map.get("image_url", 3))
            doc["Values"][target_idx][img_idx] = avatar_asset_fk.strip()

        BEJSONCore.bejson_core_atomic_write(author_file, doc)
        logger.info("Updated Author: %s", clean_uuid)
        return True

    def delete_author(self, author_uuid: str) -> bool:
        clean_uuid = author_uuid.strip()
        author_file = self._resolve_author_file()
        doc = MFDBCore.bejson_core_load_file(author_file)
        f_map = self._get_field_map(doc)

        target_idx = None
        for i, row in enumerate(doc.get("Values", [])):
            if str(row[f_map["author_uuid"]]).strip() == clean_uuid:
                target_idx = i
                break

        if target_idx is None:
            return False

        doc["Values"].pop(target_idx)
        BEJSONCore.bejson_core_atomic_write(author_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "AuthorProfile", len(doc["Values"]))
        logger.info("Deleted Author: %s", clean_uuid)
        return True
