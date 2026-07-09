"""
DevDock Watcher Module
Real-time file system monitoring using Watchdog.
"""

import logging
import time
import threading
from pathlib import Path
from typing import List, Optional

from config import settings
from organizer import organizer

logger = logging.getLogger(__name__)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog not installed. File monitoring disabled.")


class DevDockEventHandler(FileSystemEventHandler):
    """Handles file system events from Watchdog and triggers organization."""

    def __init__(self, debounce_seconds: float = 1.5):
        super().__init__()
        self._debounce: dict = {}
        self._debounce_seconds = debounce_seconds
        self._lock = threading.Lock()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule(Path(event.dest_path))

    def _schedule(self, file_path: Path) -> None:
        """Debounce: wait for file to finish downloading before organizing."""
        with self._lock:
            # Cancel any existing timer for this path
            if file_path in self._debounce:
                self._debounce[file_path].cancel()

            timer = threading.Timer(
                self._debounce_seconds,
                self._process,
                args=(file_path,),
            )
            self._debounce[file_path] = timer
            timer.start()

    def _process(self, file_path: Path) -> None:
        with self._lock:
            self._debounce.pop(file_path, None)

        if not file_path.exists():
            return

        # Wait for file to be fully written (size stable)
        if not self._wait_for_stable(file_path):
            return

        try:
            organizer.organize_file(file_path)
        except Exception as e:
            logger.error(f"Error organizing {file_path.name}: {e}")

    def _wait_for_stable(self, file_path: Path, checks: int = 3, interval: float = 0.5) -> bool:
        """
        Wait until file size is stable (file finished downloading).
        Returns False if file disappears.
        """
        prev_size = -1
        for _ in range(checks):
            try:
                size = file_path.stat().st_size
                if size == prev_size:
                    return True
                prev_size = size
                time.sleep(interval)
            except FileNotFoundError:
                return False
        return True


class WatcherService:
    """Manages Watchdog observers for multiple monitored folders."""

    def __init__(self):
        self._observer: Optional["Observer"] = None
        self._running = False
        self._paused = False
        self._monitored: List[str] = []

    def start(self) -> bool:
        """Start monitoring all configured folders."""
        if not WATCHDOG_AVAILABLE:
            logger.error("Watchdog is not installed. Cannot start monitoring.")
            return False

        if self._running:
            logger.warning("Watcher already running.")
            return True

        folders = settings.monitored_folders
        if not folders:
            logger.warning("No folders configured for monitoring.")
            return False

        self._observer = Observer()
        handler = DevDockEventHandler()

        for folder_str in folders:
            folder = Path(folder_str)
            if not folder.exists():
                logger.warning(f"Monitored folder does not exist: {folder}")
                continue
            self._observer.schedule(handler, str(folder), recursive=False)
            self._monitored.append(str(folder))
            logger.info(f"Monitoring: {folder}")

        try:
            self._observer.start()
            self._running = True
            logger.info("Watcher service started.")
            return True
        except Exception as e:
            logger.error(f"Failed to start observer: {e}")
            return False

    def stop(self) -> None:
        """Stop the Watchdog observer."""
        if self._observer and self._running:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._running = False
            logger.info("Watcher service stopped.")

    def pause(self) -> None:
        """Pause file monitoring (observer keeps running but events are ignored via flag)."""
        self._paused = True
        logger.info("Watcher paused.")

    def resume(self) -> None:
        """Resume file monitoring."""
        self._paused = False
        logger.info("Watcher resumed.")

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def monitored_folders(self) -> List[str]:
        return self._monitored

    def add_folder(self, folder_path: str) -> bool:
        """Dynamically add a new folder to monitor."""
        if not WATCHDOG_AVAILABLE or not self._observer:
            return False
        folder = Path(folder_path)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        handler = DevDockEventHandler()
        self._observer.schedule(handler, str(folder), recursive=False)
        self._monitored.append(folder_path)
        logger.info(f"Added monitored folder: {folder_path}")
        return True


# Singleton
watcher_service = WatcherService()
