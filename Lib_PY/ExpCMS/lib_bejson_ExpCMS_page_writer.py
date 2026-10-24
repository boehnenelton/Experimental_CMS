"""
Library:        lib_bejson_ExpCMS_page_writer.py
Family:         ExpCMS
Description:    Owning Writer module for Page and PageContent entities adhering to Policy §10.1, §10.3, §10.4, and §6.2.
Version:        2.0.0
Author:         Elton Boehnen · boehnenelton2024@gmail.com · boehnenelton2024.pages.dev · github.com/boehnenelton
Date:           2026-10-24
RELATIONAL_ID:  4f3b8901-2e11-4f32-9b21-8c4d7e1a5b99
"""
import os
import sys
import uuid
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import lib_bejson_Core_bejson_core as BEJSONCore
import lib_bejson_Core_mfdb_core as MFDBCore
from lib_bejson_ExpCMS_category_writer import CategoryOwningWriter, UNCATEGORIZED_STATIC_UUID

logger = logging.getLogger("PageWriter")


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_cell(val: Any) -> Any:
    return val.strip() if isinstance(val, str) else val


def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "page"


class PageOwningWriter:
    """Designated Single Write-Owner for Page and PageContent relational entities."""

    def __init__(self, content_manifest_path: str):
        self.manifest_path = content_manifest_path
        self.category_writer = CategoryOwningWriter(content_manifest_path)
        self._cached_page_file: Optional[str] = None
        self._cached_content_file: Optional[str] = None
        self._cached_page_fmap: Optional[Dict[str, int]] = None
        self._cached_content_fmap: Optional[Dict[str, int]] = None

    def _resolve_page_file(self) -> str:
        if self._cached_page_file and os.path.exists(self._cached_page_file):
            return self._cached_page_file
        entry = MFDBCore._get_manifest_entry(self.manifest_path, "Page")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        self._cached_page_file = os.path.normpath(os.path.join(manifest_dir, entry["file_path"]))
        return self._cached_page_file

    def _resolve_content_file(self) -> str:
        if self._cached_content_file and os.path.exists(self._cached_content_file):
            return self._cached_content_file
        entry = MFDBCore._get_manifest_entry(self.manifest_path, "PageContent")
        manifest_dir = os.path.dirname(os.path.abspath(self.manifest_path))
        self._cached_content_file = os.path.normpath(os.path.join(manifest_dir, entry["file_path"]))
        return self._cached_content_file

    def _get_page_field_map(self, doc: Dict[str, Any]) -> Dict[str, int]:
        if self._cached_page_fmap is not None:
            return self._cached_page_fmap
        self._cached_page_fmap = {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}
        return self._cached_page_fmap

    def _get_content_field_map(self, doc: Dict[str, Any]) -> Dict[str, int]:
        if self._cached_content_fmap is not None:
            return self._cached_content_fmap
        self._cached_content_fmap = {f["name"].strip(): i for i, f in enumerate(doc.get("Fields", []))}
        return self._cached_content_fmap

    def _resolve_category_uuid(self, cat_input: str) -> str:
        clean = (cat_input or "").strip()
        if not clean:
            return UNCATEGORIZED_STATIC_UUID
        # Check if already a known UUID
        cat = self.category_writer.get_category_by_uuid(clean)
        if cat:
            return cat["category_uuid"]
        # Look up by slug
        cat = self.category_writer.get_category_by_slug(clean)
        if cat:
            return cat["category_uuid"]
        return UNCATEGORIZED_STATIC_UUID

    def _unique_page_slug(self, base_slug: str, category_uuid: str, exclude_uuid: str = None) -> str:
        pages = self.get_all_pages()
        existing = {
            p["page_slug"] for p in pages
            if p.get("category_fk") == category_uuid and p.get("page_uuid") != exclude_uuid
        }
        if base_slug not in existing:
            return base_slug
        n = 2
        while f"{base_slug}-{n}" in existing:
            n += 1
        return f"{base_slug}-{n}"

    def get_all_pages(self) -> List[Dict[str, Any]]:
        page_file = self._resolve_page_file()
        doc = MFDBCore.bejson_core_load_file(page_file)
        f_map = self._get_page_field_map(doc)
        results = []
        for row in doc.get("Values", []):
            rec = {col: _sanitize_cell(row[idx]) for col, idx in f_map.items()}
            # Backwards compatibility aliases
            rec["title"] = rec.get("page_title")
            rec["slug"] = rec.get("page_slug")
            rec["created_at"] = rec.get("page_created_at")
            rec["featured_img"] = rec.get("page_featured_asset_fk")
            results.append(rec)
        return results

    def get_full_page_data(self, page_uuid: str) -> Optional[Dict[str, Any]]:
        clean_uuid = page_uuid.strip()
        target_page = None
        for p in self.get_all_pages():
            if p["page_uuid"] == clean_uuid:
                target_page = p.copy()
                break

        if not target_page:
            return None

        # Load child PageContent
        content_file = self._resolve_content_file()
        c_doc = MFDBCore.bejson_core_load_file(content_file)
        c_fmap = self._get_content_field_map(c_doc)

        fk_idx = c_fmap.get("page_fk", c_fmap.get("page_uuid_fk", 1))
        content_row = None
        for row in c_doc.get("Values", []):
            if str(row[fk_idx]).strip() == clean_uuid:
                content_row = row
                break

        if content_row:
            for col, idx in c_fmap.items():
                target_page[col] = _sanitize_cell(content_row[idx])
            # Backwards compatibility aliases
            target_page["html_body"] = target_page.get("content_html_body")
            target_page["markdown_body"] = target_page.get("content_markdown_body")
            target_page["source_files"] = target_page.get("content_source_files") or []
            target_page["video_url"] = target_page.get("content_video_url") or ""
            target_page["pdf_url"] = target_page.get("content_pdf_url") or ""
        else:
            target_page["html_body"] = ""
            target_page["markdown_body"] = ""
            target_page["source_files"] = []
            target_page["video_url"] = ""
            target_page["pdf_url"] = ""

        return target_page

    def create_page(self, title: str, category_input: str, page_type: str, content_data: Dict[str, Any]) -> str:
        clean_title = title.strip()
        category_uuid = self._resolve_category_uuid(category_input)
        page_uuid = str(uuid.uuid4())
        content_uuid = str(uuid.uuid4())
        page_slug = self._unique_page_slug(slugify(clean_title), category_uuid)
        now_iso = get_utc_now()

        # 1. Write Page Record
        page_file = self._resolve_page_file()
        p_doc = MFDBCore.bejson_core_load_file(page_file)
        p_fmap = self._get_page_field_map(p_doc)

        new_page_row = [None] * len(p_fmap)
        new_page_row[p_fmap["page_uuid"]] = page_uuid
        new_page_row[p_fmap["category_fk"]] = category_uuid
        new_page_row[p_fmap["author_fk"]] = content_data.get("author_fk", "")
        new_page_row[p_fmap["page_featured_asset_fk"]] = content_data.get("featured_img") or content_data.get("page_featured_asset_fk") or ""
        new_page_row[p_fmap["page_title"]] = clean_title
        new_page_row[p_fmap["page_slug"]] = page_slug
        new_page_row[p_fmap["page_type"]] = page_type
        new_page_row[p_fmap["page_created_at"]] = now_iso
        new_page_row[p_fmap["page_updated_at"]] = now_iso

        p_doc.setdefault("Values", []).append(new_page_row)
        BEJSONCore.bejson_core_atomic_write(page_file, p_doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "Page", len(p_doc["Values"]))

        # 2. Write 1:1 PageContent Record
        content_file = self._resolve_content_file()
        c_doc = MFDBCore.bejson_core_load_file(content_file)
        c_fmap = self._get_content_field_map(c_doc)

        new_content_row = [None] * len(c_fmap)
        new_content_row[c_fmap["content_uuid"]] = content_uuid
        new_content_row[c_fmap["page_fk"]] = page_uuid
        new_content_row[c_fmap["content_html_body"]] = content_data.get("html_body", "")
        new_content_row[c_fmap["content_markdown_body"]] = content_data.get("markdown_body", "")
        new_content_row[c_fmap["content_source_files"]] = content_data.get("source_files", [])
        new_content_row[c_fmap["content_video_url"]] = content_data.get("video_url", "")
        new_content_row[c_fmap["content_pdf_url"]] = content_data.get("pdf_url", "")
        new_content_row[c_fmap["content_updated_at"]] = now_iso

        c_doc.setdefault("Values", []).append(new_content_row)
        BEJSONCore.bejson_core_atomic_write(content_file, c_doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "PageContent", len(c_doc["Values"]))

        logger.info("Created Page: '%s' (UUID: %s, Category: %s)", clean_title, page_uuid, category_uuid)
        return page_uuid

    def update_page(self, page_uuid: str, title: str, category_input: str, page_type: str, content_data: Dict[str, Any]) -> bool:
        clean_uuid = page_uuid.strip()
        category_uuid = self._resolve_category_uuid(category_input)
        clean_title = title.strip()
        now_iso = get_utc_now()

        # 1. Update Page table
        page_file = self._resolve_page_file()
        p_doc = MFDBCore.bejson_core_load_file(page_file)
        p_fmap = self._get_page_field_map(p_doc)

        target_p_idx = None
        for i, row in enumerate(p_doc.get("Values", [])):
            if str(row[p_fmap["page_uuid"]]).strip() == clean_uuid:
                target_p_idx = i
                break

        if target_p_idx is None:
            return False

        new_slug = self._unique_page_slug(slugify(clean_title), category_uuid, exclude_uuid=clean_uuid)
        p_doc["Values"][target_p_idx][p_fmap["page_title"]] = clean_title
        p_doc["Values"][target_p_idx][p_fmap["page_slug"]] = new_slug
        p_doc["Values"][target_p_idx][p_fmap["category_fk"]] = category_uuid
        p_doc["Values"][target_p_idx][p_fmap["page_type"]] = page_type
        if "author_fk" in content_data:
            p_doc["Values"][target_p_idx][p_fmap["author_fk"]] = content_data["author_fk"]
        if "featured_img" in content_data or "page_featured_asset_fk" in content_data:
            p_doc["Values"][target_p_idx][p_fmap["page_featured_asset_fk"]] = content_data.get("featured_img") or content_data.get("page_featured_asset_fk") or ""
        p_doc["Values"][target_p_idx][p_fmap["page_updated_at"]] = now_iso

        BEJSONCore.bejson_core_atomic_write(page_file, p_doc)

        # 2. Update PageContent table
        content_file = self._resolve_content_file()
        c_doc = MFDBCore.bejson_core_load_file(content_file)
        c_fmap = self._get_content_field_map(c_doc)

        fk_idx = c_fmap.get("page_fk", c_fmap.get("page_uuid_fk", 1))
        target_c_idx = None
        for i, row in enumerate(c_doc.get("Values", [])):
            if str(row[fk_idx]).strip() == clean_uuid:
                target_c_idx = i
                break

        if target_c_idx is not None:
            if "html_body" in content_data:
                c_doc["Values"][target_c_idx][c_fmap["content_html_body"]] = content_data["html_body"]
            if "markdown_body" in content_data:
                c_doc["Values"][target_c_idx][c_fmap["content_markdown_body"]] = content_data["markdown_body"]
            if "source_files" in content_data:
                c_doc["Values"][target_c_idx][c_fmap["content_source_files"]] = content_data["source_files"]
            if "video_url" in content_data:
                c_doc["Values"][target_c_idx][c_fmap["content_video_url"]] = content_data["video_url"]
            if "pdf_url" in content_data:
                c_doc["Values"][target_c_idx][c_fmap["content_pdf_url"]] = content_data["pdf_url"]
            c_doc["Values"][target_c_idx][c_fmap["content_updated_at"]] = now_iso
            BEJSONCore.bejson_core_atomic_write(content_file, c_doc)

        logger.info("Updated Page: '%s' (UUID: %s)", clean_title, clean_uuid)
        return True

    def delete_page(self, page_uuid: str) -> bool:
        clean_uuid = page_uuid.strip()

        # 1. Delete from Page entity
        page_file = self._resolve_page_file()
        p_doc = MFDBCore.bejson_core_load_file(page_file)
        p_fmap = self._get_page_field_map(p_doc)

        target_p_idx = None
        for i, row in enumerate(p_doc.get("Values", [])):
            if str(row[p_fmap["page_uuid"]]).strip() == clean_uuid:
                target_p_idx = i
                break

        if target_p_idx is None:
            return False

        p_doc["Values"].pop(target_p_idx)
        BEJSONCore.bejson_core_atomic_write(page_file, p_doc)
        MFDBCore._update_manifest_record_count(self.manifest_path, "Page", len(p_doc["Values"]))

        # 2. ENFORCE CASCADE DELETION on PageContent
        content_file = self._resolve_content_file()
        c_doc = MFDBCore.bejson_core_load_file(content_file)
        c_fmap = self._get_content_field_map(c_doc)

        fk_idx = c_fmap.get("page_fk", c_fmap.get("page_uuid_fk", 1))
        initial_c_len = len(c_doc.get("Values", []))
        c_doc["Values"] = [row for row in c_doc.get("Values", []) if str(row[fk_idx]).strip() != clean_uuid]
        
        if len(c_doc["Values"]) < initial_c_len:
            BEJSONCore.bejson_core_atomic_write(content_file, c_doc)
            MFDBCore._update_manifest_record_count(self.manifest_path, "PageContent", len(c_doc["Values"]))
            logger.info("Cascade DELETE: Removed child PageContent record for %s", clean_uuid)

        logger.info("Deleted Page: %s", clean_uuid)
        return True
