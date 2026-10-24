"""
Library:        lib_bejson_ExpCMS_media_writer.py
Family:         ExpCMS
Description:    Owning Writer module for MediaAsset entity adhering to Policy §10.1, §10.3, §10.4, and §6.2.
Version:        2.0.0
Author:         Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Date:           2026-10-24
RELATIONAL_ID:  9c4e1203-3f34-4a45-9b23-1d6e9f3b7c12
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

logger = logging.getLogger("MediaWriter")


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_cell(val: Any) -> Any:
    return val.strip() if isinstance(val, str) else val


class MediaOwningWriter:
    """Designated Single Write-Owner for MediaAsset entity records."""

    def __init__(self, global_manifest_path: str, assets_dir: str):
        self.manifest_path = global_manifest_path
        self.assets_dir = assets_dir
        self._cached_asset_file: Optional[str] = None
        self._cached_fmap: Optional[Dict[str, int]] = None

    def _resolve_asset_file(self) -> str:
        if self._cached_asset_file and os.path.exists(self._cached_asset_file):
            return self._cached_asset_file
        entry = MFDBCore._get_manifest_entry(self.manifest_path, "MediaAsset")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        self._cached_asset_file = os.path.normpath(os.path.join(manifest_dir, entry["file_path"]))
        return self._cached_asset_file

    def _get_field_map(self, doc: Dict[str, Any]) -> Dict[str, int]:
        if self._cached_fmap is not None:
            return self._cached_fmap
        self._cached_fmap = {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}
        return self._cached_fmap

    def get_all_assets(self) -> List[Dict[str, Any]]:
        asset_file = self._resolve_asset_file()
        doc = MFDBCore.bejson_core_load_file(asset_file)
        f_map = self._get_field_map(doc)
        results = []
        for row in doc.get("Values", []):
            rec = {col: _sanitize_cell(row[idx]) for col, idx in f_map.items()}
            # Backwards compatibility aliases
            rec["filename"] = rec.get("asset_filename") or rec.get("filename")
            rec["original_name"] = rec.get("asset_original_name") or rec.get("original_name")
            rec["mime_type"] = rec.get("asset_mime_type") or rec.get("mime_type")
            rec["size_bytes"] = rec.get("asset_size_bytes") or rec.get("size_bytes")
            rec["uploaded_at"] = rec.get("asset_uploaded_at") or rec.get("uploaded_at")
            rec["folder"] = rec.get("asset_folder") or rec.get("folder") or ""
            results.append(rec)
        return results

    def add_media_asset(self, filename: str, original_name: str, mime_type: str, size: int, folder: str = "") -> str:
        asset_uuid = str(uuid.uuid4())
        now_iso = get_utc_now()
        clean_file = filename.strip()
        clean_orig = original_name.strip()
        clean_mime = mime_type.strip()
        clean_folder = folder.strip()

        asset_file = self._resolve_asset_file()
        doc = MFDBCore.bejson_core_load_file(asset_file)
        f_map = self._get_field_map(doc)

        new_row = [None] * len(f_map)
        new_row[f_map["asset_uuid"]] = asset_uuid
        
        fn_idx = f_map.get("asset_filename", f_map.get("filename", 1))
        new_row[fn_idx] = clean_file
        
        orig_idx = f_map.get("asset_original_name", f_map.get("original_name", 2))
        new_row[orig_idx] = clean_orig
        
        mime_idx = f_map.get("asset_mime_type", f_map.get("mime_type", 3))
        new_row[mime_idx] = clean_mime
        
        size_idx = f_map.get("asset_size_bytes", f_map.get("size_bytes", 4))
        new_row[size_idx] = int(size)

        up_idx = f_map.get("asset_uploaded_at", f_map.get("uploaded_at", 5))
        new_row[up_idx] = now_iso

        fold_idx = f_map.get("asset_folder", f_map.get("folder", 6))
        new_row[fold_idx] = clean_folder

        doc.setdefault("Values", []).append(new_row)
        BEJSONCore.bejson_core_atomic_write(asset_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "MediaAsset", len(doc["Values"]))

        logger.info("Created MediaAsset: %s (UUID: %s)", clean_file, asset_uuid)
        return asset_uuid

    def delete_media_asset(self, identifier: str) -> bool:
        clean_id = identifier.strip()
        asset_file = self._resolve_asset_file()
        doc = MFDBCore.bejson_core_load_file(asset_file)
        f_map = self._get_field_map(doc)

        target_idx = None
        target_filename = None
        for i, row in enumerate(doc.get("Values", [])):
            row_uuid = str(row[f_map["asset_uuid"]]).strip()
            fn_idx = f_map.get("asset_filename", f_map.get("filename", 1))
            row_filename = str(row[fn_idx]).strip()
            if row_uuid == clean_id or row_filename == clean_id:
                target_idx = i
                target_filename = row_filename
                break

        if target_idx is None:
            return False

        # Remove physical file if on disk
        if target_filename:
            phys_path = os.path.join(self.assets_dir, target_filename)
            if os.path.exists(phys_path):
                try:
                    os.remove(phys_path)
                    logger.info("Removed physical asset file: %s", phys_path)
                except Exception as exc:
                    logger.warning("Could not remove physical file %s: %s", phys_path, exc)

        doc["Values"].pop(target_idx)
        BEJSONCore.bejson_core_atomic_write(asset_file, doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "MediaAsset", len(doc["Values"]))
        logger.info("Deleted MediaAsset: %s", clean_id)
        return True
