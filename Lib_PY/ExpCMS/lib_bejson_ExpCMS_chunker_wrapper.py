"""
Library:        lib_bejson_ExpCMS_chunker_wrapper.py
Family:         ExpCMS
Description:    Site backup/restore layer for the Experimental CMS. Wraps
                lib_bejson_ExpCMS_mfdb_chunker_v6 to provide chunk-based
                site snapshots exported as zip archives and restores from them.
                Used by EXPCMS.py for the Backups admin panel.
Version:        1.1.0
Date:           2026-08-12
Author:         Elton Boehnen
Contact:        eltonboehnen@gmail.com | boehnenelton2024.pages.dev | github.com/boehnenelton
Format_Creator: Elton Boehnen
RELATIONAL_ID:  bc74e669-cc58-4cd9-ac9d-5820f7fb77f8

Changelog:
  1.1.0 - Audit fix M2: backup_site()/restore_site() now target
          self.cms.workspace_root (the real MFDB masters: db_global/ +
          db_content/) instead of self.www_root (the built static site).
          Previously "restore" only ever replaced rendered HTML that the
          next build would overwrite anyway, and the chunker's
          chunker_config.json/.mfdb/ output polluted the served site
          until the next build wiped it. Neither problem exists once the
          target is the never-served workspace root.
  1.0.3 - Audit fix M1: restore_site()'s zip_filename came straight from
          the POST body; a value like "../../foo.zip" escaped backup_dir.
          Now stripped via os.path.basename() and re-verified with
          bejson_safe_join() before touching the filesystem.
  1.0.2 - Fixed "Backup failed: Not a directory: .../Processing/www":
          __init__ created backup_dir but never created www_root, so
          backup_site()'s chunk pass failed on any install where the
          static site hadn't been generated yet. Now mkdir's both.
  1.0.1 - Migrated to ExpCMS Library family. Renamed from
          lib_expcms_chunker_wrapper.py. Internal ChunkerV6 import
          updated to lib_bejson_ExpCMS_mfdb_chunker_v6. Header
          added per Section 6.4.
  1.0.0 - Initial release.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

import lib_bejson_ExpCMS_mfdb_chunker_v6 as ChunkerV6
import lib_bejson_Core_bejson_path_guard as PathGuard

class CMS_Chunker_Wrapper:
    def __init__(self, cms_manager):
        self.cms = cms_manager
        self.www_root = Path(cms_manager.www_root)
        self.backup_dir = Path(cms_manager.data_root) / "backups"
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        if not self.www_root.exists():
            self.www_root.mkdir(parents=True)

    def backup_site(self, changelog: str = "Automated CMS Backup", tags: str = "backup,cms"):
        """Chunk the CMS content/config workspace (the MFDB masters) and
        export as a zip.

        BUGFIX (2026-08-11, audit M2): this used to chunk self.www_root -
        the generated static site - not the MFDB masters, despite
        README.md documenting "backup/restore (zips the MFDB masters)".
        Restoring from a backup therefore never recovered any CMS content;
        it only replaced rendered HTML output, which the next /repack or
        rebuild would overwrite anyway. Now chunks self.cms.workspace_root
        (db_global/ + db_content/, the actual live databases every CRUD
        method reads/writes). This also fixes the second half of M2: the
        chunker writes chunker_config.json + a .mfdb/ folder into whatever
        directory it's pointed at - previously that meant www_root (the
        served site) got polluted with them until the next build wiped it;
        workspace_root is never served, so that's no longer a problem."""
        try:
            backup_root = Path(self.cms.workspace_root)
            backup_root.mkdir(parents=True, exist_ok=True)

            # 1. Perform Chunking
            # Note: ChunkerV6 creates .mfdb/ folder inside target_dir
            result = ChunkerV6.do_chunk(str(backup_root), changelog=changelog, tags=tags)
            if not result.get("ok"):
                return {"success": False, "error": result.get("message")}

            detail = result.get("detail", {})
            version = detail.get("version")
            manifest_path = detail.get("manifest")
            
            # 2. Export as Zip to backups folder
            timestamp = ChunkerV6.get_timestamp()
            zip_filename = f"site_backup_{version}_{timestamp}.zip"
            zip_path = self.backup_dir / zip_filename
            
            export_result = ChunkerV6.do_export(str(manifest_path), version, str(zip_path))
            if export_result.get("ok"):
                # 3. Automatic Bump for next backup
                ChunkerV6.do_bump(str(backup_root), part="patch")
                return {"success": True, "zip_path": str(zip_path), "version": version, "message": "Site chunked and exported successfully."}
            else:
                return {"success": False, "error": export_result.get("message")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def restore_site(self, zip_filename: str):
        """Import a zip and unchunk into the CMS content/config workspace
        (db_global/ + db_content/) - the MFDB masters.

        BUGFIX (2026-08-11, audit M2): this used to swap restored files
        into self.www_root (the generated static site), which matches
        backup_site()'s old (also fixed) target but never actually
        restored any CMS content - only rendered HTML that the next
        build would overwrite anyway. Now swaps into
        self.cms.workspace_root, matching the new backup_site() target.
        Caller (EXPCMS.py's /backups route) is expected to run
        cms.mount_system(force=True) and rebuild the static site after a
        successful restore, since the live manifests just changed out
        from under any in-memory state."""
        try:
            # BUGFIX (2026-08-11, audit M1): zip_filename came straight from
            # the POST body; a value like "../../foo.zip" escaped
            # backup_dir. Strip to a bare filename and re-verify containment.
            safe_name = os.path.basename(zip_filename)
            if safe_name != zip_filename or not safe_name:
                return {"success": False, "error": "Invalid backup filename."}
            try:
                zip_path = Path(PathGuard.bejson_safe_join(str(self.backup_dir), safe_name))
            except ValueError:
                return {"success": False, "error": "Invalid backup filename."}
            if not zip_path.exists():
                return {"success": False, "error": f"Backup file not found: {zip_filename}"}

            restore_target = Path(self.cms.workspace_root)
            restore_target.mkdir(parents=True, exist_ok=True)

            # Create a clean temp workspace (sibling of the restore target,
            # not inside it, so it never collides with db_global/db_content)
            restore_workspace = restore_target.parent / ".restore_workspace"
            if restore_workspace.exists(): shutil.rmtree(restore_workspace)
            restore_workspace.mkdir(parents=True)
            (restore_workspace / "data").mkdir()
            
            temp_manifest = restore_workspace / "104a.mfdb.bejson"
            
            # 1. Import Zip
            import_result = ChunkerV6.do_import(str(temp_manifest), str(zip_path), overwrite=True)
            if not import_result.get("ok"):
                return {"success": False, "error": import_result.get("message")}
            
            # 2. Get version from imported manifest
            versions = ChunkerV6.list_versions(str(temp_manifest))
            if not versions:
                return {"success": False, "error": "No versions found in backup zip."}
            
            target_version = versions[0]["version"] # Take latest/first
            
            # 3. Unchunk
            unchunk_result = ChunkerV6.do_unchunk(str(temp_manifest), target_version)
            if not unchunk_result.get("ok"):
                return {"success": False, "error": unchunk_result.get("message")}
            
            restored_files_dir = Path(unchunk_result.get("out_dir"))
            
            # 4. Swap workspace content (db_global/, db_content/, any
            #    other files the backup captured). Skip our own scratch
            #    dirs and any active .mfdb_lock so a concurrent process
            #    doesn't get confused mid-swap; mount_system() re-creates
            #    locks as needed on the next call.
            if restore_target.exists():
                for item in restore_target.iterdir():
                    if item.name in (".restore_workspace", ".mfdb"):
                        continue
                    if item.is_dir(): shutil.rmtree(item)
                    else: item.unlink()
            else:
                restore_target.mkdir(parents=True)
            
            for item in restored_files_dir.iterdir():
                shutil.move(str(item), str(restore_target / item.name))
            
            # Cleanup
            shutil.rmtree(restore_workspace)
            
            return {
                "success": True,
                "message": f"Content workspace restored to version {target_version}. "
                           "Run a repack + site rebuild to bring the built site in sync."
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_backups(self):
        """List available zip backups in the backup folder."""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for f in self.backup_dir.glob("*.zip"):
            stats = f.stat()
            backups.append({
                "filename": f.name,
                "size_kb": round(stats.st_size / 1024, 2),
                "mtime": datetime.fromtimestamp(stats.st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M")
            })
        return sorted(backups, key=lambda x: x["mtime"], reverse=True)

