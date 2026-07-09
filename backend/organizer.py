"""
DevDock Organizer Module
Moves files to their correct destination folders, creates folder structure,
handles duplicates, and records all actions to the database and logs.
"""

import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from config import BASE_FOLDER_STRUCTURE, settings
from database import db
from logger import devdock_logger
from classifier import rule_classifier
from groq_classifier import groq_classifier
from duplicate_detector import compute_sha256, duplicate_detector
from security import security_checker
from project_detector import project_detector

logger = logging.getLogger(__name__)

# Thread-safe event bus for notifications
_event_listeners: List[Callable] = []
_listener_lock = threading.Lock()


def subscribe(listener: Callable) -> None:
    with _listener_lock:
        _event_listeners.append(listener)


def unsubscribe(listener: Callable) -> None:
    with _listener_lock:
        if listener in _event_listeners:
            _event_listeners.remove(listener)


def _emit_event(event: Dict[str, Any]) -> None:
    with _listener_lock:
        listeners = list(_event_listeners)
    for fn in listeners:
        try:
            fn(event)
        except Exception as e:
            logger.warning(f"Event listener error: {e}")


class Organizer:
    """
    Core file organizer: classifies, moves, records, and notifies.
    Thread-safe and suitable for use with Watchdog file system events.
    """

    def __init__(self):
        self._lock = threading.Lock()

    # ─── Folder Structure ─────────────────────────────────────────────────────

    def ensure_folder_structure(self, base_path: Path) -> None:
        """Create the complete DevDock folder hierarchy in base_path."""
        for folder, subfolders in BASE_FOLDER_STRUCTURE.items():
            parent = base_path / folder
            parent.mkdir(parents=True, exist_ok=True)
            for sub in subfolders:
                (parent / sub).mkdir(parents=True, exist_ok=True)
        logger.info(f"Folder structure ensured at: {base_path}")

    # ─── Single File Organization ─────────────────────────────────────────────

    def organize_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Classify and move a single file. Returns a result dict or None on skip.

        This is the main entry point for the watcher.
        """
        with self._lock:
            return self._organize(file_path)

    def _organize(self, file_path: Path) -> Optional[Dict[str, Any]]:
        if not file_path.exists() or not file_path.is_file():
            return None

        # Skip hidden files and temp files
        if file_path.name.startswith(".") or file_path.name.endswith((".tmp", ".part", ".crdownload")):
            logger.debug(f"Skipping temp/hidden file: {file_path.name}")
            return None

        # Skip already organized files (files inside DevDock subfolders)
        if self._is_inside_devdock_subfolder(file_path):
            return None

        logger.info(f"Organizing: {file_path.name}")

        # ── Security Check ────────────────────────────────────────────────────
        is_sensitive, sensitive_reason = security_checker.is_sensitive(file_path)

        # ── Compute hash ──────────────────────────────────────────────────────
        sha256 = compute_sha256(file_path)
        file_size = file_path.stat().st_size if file_path.exists() else 0

        # ── Duplicate Detection ───────────────────────────────────────────────
        is_dup = False
        dup_original = None
        if sha256:
            is_dup, dup_original = duplicate_detector.is_duplicate(file_path)
            if is_dup:
                db.register_duplicate(sha256)

        # ── Project Detection (for archives) ──────────────────────────────────
        project_result = project_detector.detect(file_path)

        # ── Classification ────────────────────────────────────────────────────
        ai_used = False
        rule_result = rule_classifier.classify(file_path)

        if project_result:
            project_type, project_dest = project_result
            category = f"Project ({project_type})"
            destination_subfolder = project_dest
            confidence = 96
            reason = f"Archive contains {project_type} project markers"
        elif rule_result:
            category, destination_subfolder, confidence, reason = rule_result
        else:
            # Fall back to Groq AI
            groq_classifier.update_key(settings.groq_api_key)
            groq_result = groq_classifier.classify(file_path)
            if groq_result:
                category, destination_subfolder, confidence, reason = groq_result
                ai_used = True
            else:
                category, destination_subfolder, confidence, reason = (
                    "Unknown", "Others", 40, "Could not classify"
                )

        # ── Determine destination folder ──────────────────────────────────────
        monitored = Path(settings.monitored_folders[0]) if settings.monitored_folders else file_path.parent
        base_dir = self._get_base_dir(file_path, monitored)
        dest_folder = base_dir / destination_subfolder
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / file_path.name

        # ── Handle duplicates ─────────────────────────────────────────────────
        action = "moved"
        if is_dup:
            dup_action = settings.get("duplicate_action", "rename")
            action_taken, final_dest = duplicate_detector.handle_duplicate(
                file_path, dest_path, dup_action
            )
            if action_taken == "skipped":
                self._record(
                    file_path, dest_path, sha256, category, confidence, reason,
                    ai_used, file_size, is_sensitive, is_dup, sha256,
                    "skipped", True
                )
                return {"status": "skipped", "filename": file_path.name, "reason": "duplicate"}

            if final_dest:
                dest_path = final_dest
            action = f"moved (duplicate: {action_taken})"

        # ── Move the file ─────────────────────────────────────────────────────
        status = "organized"
        error_msg = None
        try:
            shutil.move(str(file_path), str(dest_path))
        except Exception as e:
            logger.error(f"Failed to move {file_path.name}: {e}")
            status = "error"
            error_msg = str(e)

        # ── Log & Record ──────────────────────────────────────────────────────
        record_id = self._record(
            file_path, dest_path, sha256, category, confidence, reason,
            ai_used, file_size, is_sensitive, is_dup,
            dup_original, status, not ai_used
        )

        devdock_logger.log_entry(
            filename=file_path.name,
            extension=file_path.suffix,
            category=category,
            original_location=str(file_path),
            new_location=str(dest_path) if status == "organized" else "",
            action=action,
            status=status,
            rule_based=not ai_used,
            confidence=confidence,
            reason=reason,
            error=error_msg,
        )

        db.log_activity(
            action=action,
            filename=file_path.name,
            details=f"{str(file_path)} → {str(dest_path)}",
            status=status,
        )

        result = {
            "record_id": record_id,
            "filename": file_path.name,
            "category": category,
            "destination": str(dest_path),
            "status": status,
            "ai_used": ai_used,
            "confidence": confidence,
            "reason": reason,
            "is_sensitive": is_sensitive,
            "is_duplicate": is_dup,
        }

        _emit_event({"type": "file_organized", **result})
        return result

    def _get_base_dir(self, file_path: Path, monitored: Path) -> Path:
        """Determine the base DevDock directory for a file."""
        # Always organize relative to the monitored folder
        return monitored

    def _is_inside_devdock_subfolder(self, file_path: Path) -> bool:
        """Avoid re-organizing files that are already in managed subfolders."""
        known_subfolders = set(BASE_FOLDER_STRUCTURE.keys())
        for part in file_path.parts:
            if part in known_subfolders:
                return True
        return False

    def _record(
        self, file_path: Path, dest_path: Path, sha256: Optional[str],
        category: str, confidence: int, reason: str, ai_used: bool,
        file_size: int, is_sensitive: bool, is_dup: bool,
        dup_of: Optional[str], status: str, rule_based: bool,
    ) -> int:
        """Insert a database record for the organized file."""
        record = {
            "filename": file_path.name,
            "extension": file_path.suffix,
            "sha256_hash": sha256,
            "category": category,
            "original_path": str(file_path),
            "destination_path": str(dest_path),
            "timestamp": datetime.now().isoformat(),
            "ai_used": int(ai_used),
            "confidence": confidence,
            "reason": reason,
            "status": status,
            "rule_based": int(rule_based),
            "is_sensitive": int(is_sensitive),
            "is_duplicate": int(is_dup),
            "duplicate_of": dup_of,
            "file_size": file_size,
        }
        return db.insert_record(record)

    # ─── Startup Recovery ─────────────────────────────────────────────────────

    def startup_scan(self, folder: Path) -> int:
        """
        Scan a folder for unorganized files and organize them.
        Called once on startup to catch files downloaded while offline.
        Returns the number of files organized.
        """
        self.ensure_folder_structure(folder)
        count = 0
        known_subfolders = set(BASE_FOLDER_STRUCTURE.keys())

        try:
            for file_path in folder.iterdir():
                if file_path.is_file() and not file_path.name.startswith("."):
                    result = self.organize_file(file_path)
                    if result and result.get("status") in ("organized",):
                        count += 1
        except Exception as e:
            logger.error(f"Startup scan error: {e}")

        logger.info(f"Startup scan complete. Organized {count} files.")
        return count

    # ─── Restore ──────────────────────────────────────────────────────────────

    def restore_file(self, record_id: int) -> Dict[str, Any]:
        """Restore a previously moved file to its original location."""
        record = db.get_record_by_id(record_id)
        if not record:
            return {"success": False, "error": "Record not found"}

        dest = Path(record.get("destination_path", ""))
        original = Path(record.get("original_path", ""))

        if not dest.exists():
            return {"success": False, "error": "File not found at destination"}

        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(original))
            db.mark_restored(record_id)
            db.log_activity("restore", record.get("filename"), f"Restored to {original}", "success")
            return {"success": True, "restored_to": str(original)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─── Drag & Drop / Manual Organize ────────────────────────────────────────

    def organize_folder(self, folder_path: Path) -> List[Dict[str, Any]]:
        """Organize all files in an arbitrary folder (drag & drop support)."""
        results = []
        if not folder_path.is_dir():
            return results

        for file in folder_path.rglob("*"):
            if file.is_file():
                result = self.organize_file(file)
                if result:
                    results.append(result)

        return results


# Singleton
organizer = Organizer()
