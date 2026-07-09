"""
DevDock Groq AI Classifier Module
Uses Groq API to classify files that cannot be determined by rules.
Only called when rule-based classification fails.
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Optional imports — gracefully degrade if not installed
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq package not installed. AI classification disabled.")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# Category → destination mapping used for AI responses
AI_CATEGORY_MAP = {
    "resume": "Documents",
    "cv": "Documents",
    "invoice": "Documents",
    "certificate": "Certificates",
    "medical report": "Documents",
    "research paper": "Documents",
    "college notes": "Documents",
    "personal document": "Documents",
    "spreadsheet": "Documents",
    "presentation": "Documents",
    "contract": "Documents",
    "legal document": "Documents",
    "financial document": "Documents",
    "receipt": "Documents",
    "bank statement": "Documents",
    "tax document": "Documents",
    "configuration": "DevOps/Configs",
    "dataset": "Datasets",
    "machine learning model": "AI",
    "notebook": "Programming/Python",
    "script": "Programming/Other",
    "unknown": "Others",
}

SYSTEM_PROMPT = """You are DevDock, an intelligent file classifier for a developer workspace manager.

Your task is to analyze the provided file information and classify it into the most appropriate category.

Respond ONLY with a JSON object in this exact format:
{
  "category": "<category name>",
  "confidence": <integer 0-100>,
  "reason": "<brief explanation>",
  "destination": "<suggested subfolder>"
}

Valid categories include: Resume, Invoice, Certificate, Medical Report, Research Paper,
College Notes, Personal Document, Spreadsheet, Presentation, Contract, Legal Document,
Financial Document, Receipt, Bank Statement, Tax Document, Configuration, Dataset,
Machine Learning Model, Notebook, Script, Unknown.

Keep your response concise and return only the JSON object."""


class GroqClassifier:
    """Classifies files using Groq's LLM API as a fallback classifier."""

    def __init__(self, api_key: str = "", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if not GROQ_AVAILABLE:
            return None
        if not self.api_key:
            return None
        if not self._client:
            try:
                self._client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to init Groq client: {e}")
        return self._client

    def update_key(self, api_key: str) -> None:
        self.api_key = api_key
        self._client = None

    def classify(self, file_path: Path) -> Optional[Tuple[str, str, int, str]]:
        """
        Classify a file using Groq AI.

        Returns:
            (category, destination, confidence, reason) or None on failure
        """
        client = self._get_client()
        if not client:
            logger.debug("Groq client not available — skipping AI classification.")
            return ("Others", "Others", 50, "AI classification unavailable")

        # Extract a snippet of text from the file
        text_snippet = self._extract_text_snippet(file_path)
        prompt = self._build_prompt(file_path, text_snippet)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=256,
            )
            raw = response.choices[0].message.content.strip()
            return self._parse_response(raw)
        except Exception as e:
            logger.error(f"Groq API error for {file_path.name}: {e}")
            return ("Others", "Others", 40, f"AI error: {str(e)[:100]}")

    def _build_prompt(self, file_path: Path, text_snippet: str) -> str:
        return (
            f"Filename: {file_path.name}\n"
            f"Extension: {file_path.suffix}\n"
            f"File size: {self._get_size_str(file_path)}\n"
            f"Text preview (first 500 chars):\n{text_snippet[:500] if text_snippet else 'N/A'}\n\n"
            "Classify this file."
        )

    def _extract_text_snippet(self, file_path: Path) -> str:
        """Extract a small text snippet from supported file types."""
        ext = file_path.suffix.lower()

        if ext == ".pdf" and PYPDF2_AVAILABLE:
            return self._extract_pdf(file_path)
        elif ext in (".txt", ".md", ".log", ".csv", ".json", ".yaml", ".yml", ".xml"):
            return self._extract_text(file_path)
        elif ext in (".docx",) and DOCX_AVAILABLE:
            return self._extract_docx(file_path)

        return ""

    def _extract_pdf(self, file_path: Path) -> str:
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages[:2]:  # Only first 2 pages
                    text += page.extract_text() or ""
                    if len(text) > 800:
                        break
                return text[:800]
        except Exception:
            return ""

    def _extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(800)
        except Exception:
            return ""

    def _extract_docx(self, file_path: Path) -> str:
        try:
            doc = DocxDocument(str(file_path))
            text = "\n".join(p.text for p in doc.paragraphs[:20])
            return text[:800]
        except Exception:
            return ""

    def _get_size_str(self, file_path: Path) -> str:
        try:
            size = file_path.stat().st_size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / 1024 / 1024:.1f} MB"
        except Exception:
            return "unknown"

    def _parse_response(self, raw: str) -> Optional[Tuple[str, str, int, str]]:
        """Parse JSON response from Groq."""
        try:
            # Extract JSON from potential markdown code blocks
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(raw)

            category = data.get("category", "Unknown").strip()
            confidence = int(data.get("confidence", 50))
            reason = data.get("reason", "AI classified").strip()

            # Map category to destination
            dest_from_response = data.get("destination", "")
            destination = (
                dest_from_response
                if dest_from_response
                else AI_CATEGORY_MAP.get(category.lower(), "Others")
            )

            return category, destination, confidence, reason

        except Exception as e:
            logger.error(f"Failed to parse Groq response: {e}\nRaw: {raw[:200]}")
            return ("Unknown", "Others", 30, "Failed to parse AI response")


# Singleton (api_key loaded from settings at runtime)
groq_classifier = GroqClassifier()
