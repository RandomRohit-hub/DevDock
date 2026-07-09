"""
DevDock Configuration Module
Manages all application settings, paths, and constants.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── Base Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "settings.json"
DB_FILE = DATA_DIR / "devdock.db"
WEEKLY_REPORTS_DIR = LOGS_DIR / "weekly_reports"

# ─── Default Monitored Folders ────────────────────────────────────────────────
USER_HOME = Path.home()
DEFAULT_MONITORED_FOLDERS = [
    str(USER_HOME / "Downloads"),
]

# ─── Folder Structure ─────────────────────────────────────────────────────────
BASE_FOLDER_STRUCTURE = {
    "Documents": [],
    "Images": [],
    "Videos": [],
    "Music": [],
    "Archives": [],
    "Projects": ["Python", "Node", "Java", "Rust", "Go", "Git Repositories"],
    "Programming": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "Go", "Rust", "C#", "PHP", "Other"],
    "DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux", "SSH Keys", "Certificates", "Configs"],
    "AI": [],
    "Certificates": [],
    "Datasets": [],
    "Others": [],
}

# ─── File Classification Rules ────────────────────────────────────────────────
FILE_RULES: Dict[str, Any] = {
    # SSH Keys
    "ssh_keys": {
        "filenames": ["id_rsa", "id_ed25519", "id_ecdsa", "authorized_keys", "known_hosts",
                      "id_rsa.pub", "id_ed25519.pub", "id_ecdsa.pub"],
        "destination": "DevOps/SSH Keys",
        "category": "SSH Key",
    },
    # AWS
    "aws": {
        "extensions": [".pem"],
        "patterns": ["aws-credentials", "credentials"],
        "destination": "DevOps/AWS",
        "category": "AWS",
    },
    # Docker
    "docker": {
        "filenames": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"],
        "patterns": ["docker-compose"],
        "destination": "DevOps/Docker",
        "category": "Docker",
    },
    # Terraform
    "terraform": {
        "extensions": [".tf", ".tfvars", ".tfstate"],
        "filenames": ["terraform.tfvars", ".terraform.lock.hcl"],
        "destination": "DevOps/Terraform",
        "category": "Terraform",
    },
    # Kubernetes
    "kubernetes": {
        "filenames": ["deployment.yaml", "service.yaml", "ingress.yaml", "kubeconfig",
                      "deployment.yml", "service.yml", "ingress.yml"],
        "patterns": ["kube", "k8s"],
        "destination": "DevOps/Kubernetes",
        "category": "Kubernetes",
    },
    # Programming — Python
    "python": {
        "extensions": [".py", ".pyw", ".pyx", ".pxd", ".ipynb"],
        "filenames": ["requirements.txt", "setup.py", "setup.cfg", "pyproject.toml", "Pipfile"],
        "destination": "Programming/Python",
        "category": "Python",
    },
    # Programming — JavaScript / TypeScript
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs", ".cjs"],
        "filenames": ["package.json", ".babelrc", ".eslintrc", "webpack.config.js"],
        "destination": "Programming/JavaScript",
        "category": "JavaScript",
    },
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "filenames": ["tsconfig.json"],
        "destination": "Programming/TypeScript",
        "category": "TypeScript",
    },
    # Programming — Java
    "java": {
        "extensions": [".java", ".class", ".jar"],
        "filenames": ["pom.xml", "build.gradle", "build.xml"],
        "destination": "Programming/Java",
        "category": "Java",
    },
    # Programming — Go
    "go": {
        "extensions": [".go"],
        "filenames": ["go.mod", "go.sum"],
        "destination": "Programming/Go",
        "category": "Go",
    },
    # Programming — Rust
    "rust": {
        "extensions": [".rs"],
        "filenames": ["Cargo.toml", "Cargo.lock"],
        "destination": "Programming/Rust",
        "category": "Rust",
    },
    # Programming — C / C++
    "c_cpp": {
        "extensions": [".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
        "destination": "Programming/C++",
        "category": "C/C++",
    },
    # Programming — C#
    "csharp": {
        "extensions": [".cs", ".csproj", ".sln"],
        "destination": "Programming/C#",
        "category": "C#",
    },
    # Programming — PHP
    "php": {
        "extensions": [".php", ".phtml"],
        "destination": "Programming/PHP",
        "category": "PHP",
    },
    # Documents
    "documents": {
        "extensions": [".pdf", ".docx", ".doc", ".txt", ".md", ".odt", ".rtf", ".xlsx", ".xls", ".pptx", ".ppt", ".csv"],
        "destination": "Documents",
        "category": "Document",
    },
    # Images
    "images": {
        "extensions": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp", ".tiff", ".tif", ".raw"],
        "destination": "Images",
        "category": "Image",
    },
    # Videos
    "videos": {
        "extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"],
        "destination": "Videos",
        "category": "Video",
    },
    # Music
    "music": {
        "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
        "destination": "Music",
        "category": "Music",
    },
    # Archives
    "archives": {
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2"],
        "destination": "Archives",
        "category": "Archive",
    },
    # Datasets
    "datasets": {
        "extensions": [".csv", ".json", ".xml", ".parquet", ".feather", ".h5", ".hdf5", ".npy", ".npz"],
        "destination": "Datasets",
        "category": "Dataset",
    },
    # AI / ML
    "ai_ml": {
        "extensions": [".pkl", ".pickle", ".model", ".onnx", ".pb", ".pt", ".pth", ".h5", ".keras"],
        "destination": "AI",
        "category": "AI/ML Model",
    },
    # Certificates
    "certificates": {
        "extensions": [".crt", ".cer", ".p12", ".pfx", ".p7b", ".p7c"],
        "filenames": ["certificate.pem", "cert.pem", "ca.pem"],
        "destination": "Certificates",
        "category": "Certificate",
    },
}

# ─── Sensitive File Patterns ──────────────────────────────────────────────────
SENSITIVE_PATTERNS = [
    ".env", "credentials", "secret", "password", "passwd", "private_key",
    "id_rsa", "id_ed25519", "id_ecdsa", "aws_secret", "api_key", "token",
    "passwords.txt", ".pem", "certificate",
]

SENSITIVE_EXTENSIONS = [".env", ".pem", ".key", ".p12", ".pfx"]

# ─── Project Detection Markers ────────────────────────────────────────────────
PROJECT_MARKERS = {
    "package.json": ("Node.js", "Projects/Node"),
    "requirements.txt": ("Python", "Projects/Python"),
    "pom.xml": ("Maven/Java", "Projects/Java"),
    "Cargo.toml": ("Rust", "Projects/Rust"),
    "go.mod": ("Go", "Projects/Go"),
    "build.gradle": ("Gradle/Java", "Projects/Java"),
    "CMakeLists.txt": ("C/C++", "Projects/C"),
    "Makefile": ("Make", "Projects/Other"),
    ".git": ("Git", "Projects/Git Repositories"),
}

# ─── Default Settings ─────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "groq_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "monitored_folders": DEFAULT_MONITORED_FOLDERS,
    "auto_start": True,
    "notifications_enabled": True,
    "dashboard_port": 8000,
    "organize_on_startup": True,
    "duplicate_action": "ask",  # ask | skip | rename | replace | keep_both
    "custom_rules": [],
    "theme": "dark",
    "minimize_to_tray": True,
    "log_retention_days": 30,
    "weekly_report_day": "Sunday",
    "sensitive_file_warnings": True,
}


class Settings:
    """Manages DevDock application settings with persistence."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load settings from disk, applying defaults for missing keys."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                self._data = {**DEFAULT_SETTINGS, **stored}
            except Exception as e:
                logger.warning(f"Could not load settings: {e}. Using defaults.")
                self._data = dict(DEFAULT_SETTINGS)
        else:
            self._data = dict(DEFAULT_SETTINGS)
            self.save()

    def save(self) -> None:
        """Persist settings to disk."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def update(self, data: Dict[str, Any]) -> None:
        self._data.update(data)
        self.save()

    def all(self) -> Dict[str, Any]:
        return dict(self._data)

    @property
    def groq_api_key(self) -> str:
        return self._data.get("groq_api_key", "")

    @property
    def monitored_folders(self) -> List[str]:
        return self._data.get("monitored_folders", DEFAULT_MONITORED_FOLDERS)

    @property
    def dashboard_port(self) -> int:
        return self._data.get("dashboard_port", 8000)

    @property
    def notifications_enabled(self) -> bool:
        return self._data.get("notifications_enabled", True)

    @property
    def custom_rules(self) -> List[Dict]:
        return self._data.get("custom_rules", [])


# Singleton settings instance
settings = Settings()
