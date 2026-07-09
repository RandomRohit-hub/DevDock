"""
DevDock System Tray Module
Windows system tray icon with context menu using pystray.
"""

import logging
import threading
import webbrowser
from pathlib import Path
from typing import Optional

from config import settings
from notifications import notification_service

logger = logging.getLogger(__name__)

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logger.warning("pystray/Pillow not installed. System tray disabled.")


def _create_icon_image(size: int = 64) -> "Image.Image":
    """Generate a simple DevDock tray icon programmatically."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Dark background circle
    draw.ellipse([2, 2, size - 2, size - 2], fill=(30, 30, 46))
    # Accent ring
    draw.ellipse([4, 4, size - 4, size - 4], outline=(139, 92, 246), width=3)
    # "D" letter
    draw.text((size // 2 - 7, size // 2 - 10), "D", fill=(167, 139, 250))
    return img


class TrayService:
    """Windows System Tray icon and context menu for DevDock."""

    def __init__(self):
        self._icon: Optional["pystray.Icon"] = None
        self._thread: Optional[threading.Thread] = None
        self._watcher_ref = None
        self._dashboard_port = 8000

    def set_watcher(self, watcher) -> None:
        self._watcher_ref = watcher

    def set_dashboard_port(self, port: int) -> None:
        self._dashboard_port = port

    def _build_menu(self) -> "pystray.Menu":
        return pystray.Menu(
            pystray.MenuItem("🌐  Open Dashboard", self._open_dashboard),
            pystray.MenuItem("⚡  Organize Now", self._organize_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⏸   Pause Monitoring", self._pause, visible=self._is_running),
            pystray.MenuItem("▶   Resume Monitoring", self._resume, visible=self._is_paused),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("📋  Open Logs Folder", self._open_logs),
            pystray.MenuItem("⚙   Settings", self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("✕   Exit DevDock", self._exit),
        )

    def _is_running(self, item) -> bool:
        return self._watcher_ref is not None and self._watcher_ref.is_running and not self._watcher_ref.is_paused

    def _is_paused(self, item) -> bool:
        return self._watcher_ref is not None and self._watcher_ref.is_paused

    def _open_dashboard(self, icon=None, item=None) -> None:
        webbrowser.open(f"http://localhost:{self._dashboard_port}")

    def _organize_now(self, icon=None, item=None) -> None:
        from organizer import organizer
        from pathlib import Path
        for folder in settings.monitored_folders:
            organizer.startup_scan(Path(folder))
        notification_service.notify("DevDock", "Manual organization complete.", duration="short")

    def _pause(self, icon=None, item=None) -> None:
        if self._watcher_ref:
            self._watcher_ref.pause()
            notification_service.notify("DevDock", "Monitoring paused.", duration="short")

    def _resume(self, icon=None, item=None) -> None:
        if self._watcher_ref:
            self._watcher_ref.resume()
            notification_service.notify("DevDock", "Monitoring resumed.", duration="short")

    def _open_logs(self, icon=None, item=None) -> None:
        import subprocess
        from config import LOGS_DIR
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{LOGS_DIR}"')

    def _open_settings(self, icon=None, item=None) -> None:
        webbrowser.open(f"http://localhost:{self._dashboard_port}/#/settings")

    def _exit(self, icon=None, item=None) -> None:
        logger.info("DevDock exit requested from tray.")
        if self._watcher_ref:
            self._watcher_ref.stop()
        if self._icon:
            self._icon.stop()

    def start(self) -> None:
        if not PYSTRAY_AVAILABLE:
            logger.warning("Tray service unavailable — pystray not installed.")
            return

        try:
            icon_image = _create_icon_image(64)
        except Exception:
            # Minimal fallback icon
            from PIL import Image
            icon_image = Image.new("RGB", (64, 64), (139, 92, 246))

        self._icon = pystray.Icon(
            name="DevDock",
            icon=icon_image,
            title="DevDock — AI Workspace Manager",
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        logger.info("System tray icon started.")

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def update_tooltip(self, message: str) -> None:
        if self._icon:
            self._icon.title = f"DevDock — {message}"


# Singleton
tray_service = TrayService()
