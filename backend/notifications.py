"""
DevDock Notifications Module
Windows toast notifications using winotify.
"""

import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from winotify import Notification, audio
    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False
    logger.warning("winotify not installed. Desktop notifications disabled.")


class NotificationService:
    """Sends Windows toast notifications for DevDock events."""

    APP_ID = "DevDock"
    ICON_PATH = ""  # Set to icon path when packaged

    def __init__(self):
        self._enabled = True

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def notify(
        self,
        title: str,
        message: str,
        icon: Optional[str] = None,
        duration: str = "short",
    ) -> None:
        """Send a Windows toast notification in a background thread."""
        if not self._enabled or not WINOTIFY_AVAILABLE:
            logger.info(f"[Notification] {title}: {message}")
            return

        threading.Thread(
            target=self._send,
            args=(title, message, icon, duration),
            daemon=True,
        ).start()

    def _send(self, title: str, message: str, icon: Optional[str], duration: str) -> None:
        try:
            toast = Notification(
                app_id=self.APP_ID,
                title=title,
                msg=message,
                duration=duration,
                icon=icon or self.ICON_PATH,
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            logger.warning(f"Notification failed: {e}")

    def notify_organized(self, filename: str, destination: str, category: str) -> None:
        """Standard notification for a successfully organized file."""
        self.notify(
            title=f"✔ {category} Organized",
            message=f"{filename}\nMoved to {destination}",
        )

    def notify_sensitive(self, filename: str, reason: str) -> None:
        """Warning notification for a sensitive file."""
        self.notify(
            title="⚠️ Sensitive File Detected",
            message=f"{filename}\n{reason}",
            duration="long",
        )

    def notify_duplicate(self, filename: str) -> None:
        """Notification for a duplicate file."""
        self.notify(
            title="🔄 Duplicate File",
            message=f"{filename} is a duplicate and was handled per your settings.",
        )

    def notify_startup(self, count: int) -> None:
        """Notification shown on startup after organizing missed files."""
        if count > 0:
            self.notify(
                title="DevDock — Startup Recovery",
                message=f"Organized {count} file(s) downloaded while DevDock was offline.",
            )
        else:
            self.notify(
                title="DevDock Running",
                message="Monitoring your Downloads folder in the background.",
            )

    def notify_error(self, filename: str, error: str) -> None:
        """Error notification."""
        self.notify(
            title="❌ DevDock Error",
            message=f"Failed to organize: {filename}\n{error[:100]}",
            duration="long",
        )


# Singleton
notification_service = NotificationService()
