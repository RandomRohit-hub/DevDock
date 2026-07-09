"""
DevDock Project Detector Module
Detects developer projects inside downloaded archives.
"""

import logging
import zipfile
import tarfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from config import PROJECT_MARKERS

logger = logging.getLogger(__name__)


class ProjectDetector:
    """
    Inspects downloaded archives to detect embedded developer projects.
    Returns a project type and recommended destination if found.
    """

    ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tar.gz", ".bz2", ".tar.bz2", ".tgz"}

    def is_archive(self, file_path: Path) -> bool:
        suffix = file_path.suffix.lower()
        name_lower = file_path.name.lower()
        return suffix in self.ARCHIVE_EXTENSIONS or name_lower.endswith(".tar.gz") or name_lower.endswith(".tar.bz2")

    def detect(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """
        Attempt to detect a project type inside an archive.

        Returns:
            (project_type, destination_subfolder) or None
        """
        if not self.is_archive(file_path):
            return None

        try:
            contents = self._list_archive_contents(file_path)
            if not contents:
                return None

            for filename, project_type, destination in self._check_markers(contents):
                logger.info(f"Project detected in {file_path.name}: {project_type} → {destination}")
                return project_type, destination

        except Exception as e:
            logger.warning(f"Project detection failed for {file_path.name}: {e}")

        return None

    def _list_archive_contents(self, file_path: Path) -> list:
        """List all filenames inside the archive."""
        name_lower = file_path.name.lower()

        if name_lower.endswith(".zip"):
            try:
                with zipfile.ZipFile(file_path, "r") as zf:
                    return [Path(n).name for n in zf.namelist()]
            except Exception:
                return []

        if name_lower.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar")):
            try:
                with tarfile.open(file_path, "r:*") as tf:
                    return [Path(m.name).name for m in tf.getmembers() if m.isfile()]
            except Exception:
                return []

        return []

    def _check_markers(self, filenames: list):
        """Check archive contents against known project markers."""
        filename_set = {f.lower() for f in filenames}

        # .git takes top priority
        if ".git" in filename_set or "config" in filename_set:
            # Heuristic: if there is a .git dir indicator
            yield ".git", "Git Repository", "Projects/Git Repositories"
            return

        for marker, (project_type, destination) in PROJECT_MARKERS.items():
            if marker.lower() in filename_set:
                yield marker, project_type, destination
                return

    def has_git_repo(self, folder: Path) -> bool:
        """Check if a folder contains a .git directory."""
        return (folder / ".git").is_dir()


# Singleton
project_detector = ProjectDetector()
