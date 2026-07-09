"""
DevDock Security Module
Detects and flags sensitive files before organization.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from config import SENSITIVE_PATTERNS, SENSITIVE_EXTENSIONS

logger = logging.getLogger(__name__)


class SecurityChecker:
    """Identifies sensitive files that need special handling."""

    SENSITIVE_CONTENT_MARKERS = [
        b"BEGIN RSA PRIVATE KEY",
        b"BEGIN EC PRIVATE KEY",
        b"BEGIN OPENSSH PRIVATE KEY",
        b"aws_access_key_id",
        b"aws_secret_access_key",
        b"password",
        b"secret_key",
        b"api_key",
        b"private_key",
        b"-----BEGIN CERTIFICATE-----",
        b"BEGIN PGP PRIVATE KEY",
    ]

    def is_sensitive(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Check if a file is sensitive by name, extension, and content sniffing.
        Returns (is_sensitive, reason).
        """
        name_lower = file_path.name.lower()
        stem_lower = file_path.stem.lower()
        ext_lower = file_path.suffix.lower()

        # Check by filename patterns
        for pattern in SENSITIVE_PATTERNS:
            if pattern.lower() in name_lower:
                reason = f"Filename matches sensitive pattern: '{pattern}'"
                logger.warning(f"Sensitive file detected: {file_path.name} — {reason}")
                return True, reason

        # Check by extension
        if ext_lower in SENSITIVE_EXTENSIONS:
            reason = f"Sensitive extension: {ext_lower}"
            logger.warning(f"Sensitive file detected: {file_path.name} — {reason}")
            return True, reason

        # Sniff first 4KB for sensitive content markers
        if file_path.is_file() and file_path.stat().st_size < 10 * 1024 * 1024:  # < 10 MB
            try:
                with open(file_path, "rb") as f:
                    header = f.read(4096)
                for marker in self.SENSITIVE_CONTENT_MARKERS:
                    if marker in header:
                        reason = f"File contains sensitive content: '{marker.decode(errors='ignore')}'"
                        logger.warning(f"Sensitive content in: {file_path.name} — {reason}")
                        return True, reason
            except Exception:
                pass  # If we can't read it, assume not sensitive for now

        return False, None

    def get_warning_message(self, file_path: Path, reason: str) -> str:
        """Generate a user-facing warning message for a sensitive file."""
        return (
            f"⚠️ Sensitive File Detected\n\n"
            f"File: {file_path.name}\n"
            f"Reason: {reason}\n\n"
            f"DevDock recommends reviewing this file before moving it."
        )


# Singleton
security_checker = SecurityChecker()
