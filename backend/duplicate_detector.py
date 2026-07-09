"""
DevDock Duplicate Detector Module
SHA-256 hashing + duplicate detection and resolution.
"""

import hashlib
import logging
import shutil
from pathlib import Path
from typing import Optional, Tuple

from database import db

logger = logging.getLogger(__name__)


def compute_sha256(file_path: Path, chunk_size: int = 65536) -> Optional[str]:
    """Compute SHA-256 hash of a file. Returns None on error."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash {file_path}: {e}")
        return None


class DuplicateDetector:
    """Detects and handles duplicate files using SHA-256 hashes."""

    def is_duplicate(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Check if a file is a duplicate based on its SHA-256 hash.
        Returns (is_duplicate, existing_record_path).
        """
        sha256 = compute_sha256(file_path)
        if not sha256:
            return False, None

        existing = db.get_record_by_hash(sha256)
        if existing and existing.get("destination_path"):
            return True, existing.get("destination_path")
        return False, None

    def handle_duplicate(
        self,
        src: Path,
        dest: Path,
        action: str = "rename",
    ) -> Tuple[str, Optional[Path]]:
        """
        Handle a duplicate file according to the specified action.

        Args:
            src: Source file path
            dest: Intended destination path
            action: One of 'skip' | 'rename' | 'replace' | 'keep_both'

        Returns:
            (action_taken, final_destination)
        """
        if action == "skip":
            logger.info(f"Skipping duplicate: {src.name}")
            return "skipped", None

        elif action == "replace":
            logger.info(f"Replacing duplicate: {dest}")
            return "replaced", dest

        elif action == "rename":
            new_dest = self._get_unique_path(dest)
            logger.info(f"Renaming duplicate to: {new_dest.name}")
            return "renamed", new_dest

        elif action == "keep_both":
            new_dest = self._get_unique_path(dest)
            logger.info(f"Keeping both — duplicate saved as: {new_dest.name}")
            return "kept_both", new_dest

        # Default: rename
        new_dest = self._get_unique_path(dest)
        return "renamed", new_dest

    def _get_unique_path(self, path: Path) -> Path:
        """Generate a unique file path by appending a counter."""
        counter = 1
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        while True:
            new_path = parent / f"{stem}_copy{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1


# Singleton
duplicate_detector = DuplicateDetector()
