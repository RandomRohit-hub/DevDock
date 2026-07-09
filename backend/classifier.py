"""
DevDock Rule-Based Classifier Module
Classifies files using deterministic rules before calling Groq AI.
"""

import logging
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from config import FILE_RULES
from database import db

logger = logging.getLogger(__name__)


class RuleBasedClassifier:
    """
    Fast, deterministic file classifier using filename, extension,
    and content-sniffing rules. Returns None if a file cannot be
    confidently classified so the AI classifier can take over.
    """

    def classify(self, file_path: Path) -> Optional[Tuple[str, str, int, str]]:
        """
        Attempt to classify a file using rules.

        Returns:
            (category, destination_subfolder, confidence, reason) or None
        """
        # First check custom rules from DB
        result = self._apply_custom_rules(file_path)
        if result:
            return result

        filename = file_path.name
        stem = file_path.stem
        ext = file_path.suffix.lower()
        name_lower = filename.lower()

        # Iterate through built-in rules
        for rule_key, rule in FILE_RULES.items():
            # Exact filename matches (highest priority)
            if "filenames" in rule:
                for fname in rule["filenames"]:
                    if name_lower == fname.lower() or stem.lower() == fname.lower():
                        return (
                            rule["category"],
                            rule["destination"],
                            98,
                            f"Exact filename match: {fname}",
                        )

            # Extension matches
            if "extensions" in rule and ext:
                for rule_ext in rule["extensions"]:
                    if ext == rule_ext.lower():
                        return (
                            rule["category"],
                            rule["destination"],
                            95,
                            f"Extension match: {ext}",
                        )

            # Pattern matches in filename
            if "patterns" in rule:
                for pattern in rule["patterns"]:
                    if pattern.lower() in name_lower:
                        return (
                            rule["category"],
                            rule["destination"],
                            90,
                            f"Filename pattern match: {pattern}",
                        )

        return None  # Could not classify — send to AI

    def _apply_custom_rules(self, file_path: Path) -> Optional[Tuple[str, str, int, str]]:
        """Check user-defined custom rules from database."""
        try:
            rules = db.get_custom_rules()
            name_lower = file_path.name.lower()
            ext = file_path.suffix.lower()

            for rule in rules:
                condition = rule.get("condition", "")
                value = rule.get("value", "").lower()
                destination = rule.get("destination", "Others")

                if condition == "filename_contains" and value in name_lower:
                    return (
                        f"Custom ({rule['name']})",
                        destination,
                        92,
                        f"Custom rule '{rule['name']}': filename contains '{value}'",
                    )
                elif condition == "extension_equals" and ext == (value if value.startswith(".") else f".{value}"):
                    return (
                        f"Custom ({rule['name']})",
                        destination,
                        92,
                        f"Custom rule '{rule['name']}': extension = '{value}'",
                    )
                elif condition == "filename_starts_with" and name_lower.startswith(value):
                    return (
                        f"Custom ({rule['name']})",
                        destination,
                        90,
                        f"Custom rule '{rule['name']}': filename starts with '{value}'",
                    )
        except Exception as e:
            logger.warning(f"Custom rule evaluation failed: {e}")

        return None


# Singleton
rule_classifier = RuleBasedClassifier()
