"""
DevDock Main Entry Point
Orchestrates startup, recovery, monitoring, tray, and dashboard.
"""

import logging
import signal
import sys
import threading
import time
from pathlib import Path

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("devdock")

from config import settings, LOGS_DIR, DATA_DIR
from database import db
from logger import devdock_logger
from organizer import organizer
from watcher import watcher_service
from dashboard import dashboard_server
from notifications import notification_service
from tray import tray_service


class DevDock:
    """
    Main DevDock application orchestrator.
    Coordinates all subsystems: organizer, watcher, dashboard, tray.
    """

    def __init__(self):
        self._running = False
        self._weekly_report_thread: threading.Thread = None

    def start(self) -> None:
        """Full application startup sequence."""
        logger.info("=" * 60)
        logger.info("  DevDock v1.0.0 — Starting...")
        logger.info("=" * 60)

        # Ensure all directories exist
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        devdock_logger.log_startup()

        # ── Step 1: Startup Recovery ──────────────────────────────────────────
        recovered = 0
        if settings.get("organize_on_startup"):
            logger.info("Running startup recovery scan...")
            for folder_str in settings.monitored_folders:
                folder = Path(folder_str)
                if folder.exists():
                    count = organizer.startup_scan(folder)
                    recovered += count
                else:
                    logger.warning(f"Monitored folder missing: {folder}")

            notification_service.notify_startup(recovered)
            logger.info(f"Startup recovery: {recovered} file(s) organized.")

        # ── Step 2: Start Real-Time Monitoring ────────────────────────────────
        started = watcher_service.start()
        if started:
            logger.info("Real-time file monitoring active.")
        else:
            logger.warning("File monitoring could not start (watchdog may not be installed).")

        # ── Step 3: Start Dashboard API ───────────────────────────────────────
        port = settings.dashboard_port
        dashboard_server.start(port=port, open_browser=True)
        logger.info(f"Dashboard: http://localhost:{port}")

        # ── Step 4: Start System Tray ─────────────────────────────────────────
        tray_service.set_watcher(watcher_service)
        tray_service.set_dashboard_port(port)
        tray_service.start()

        # ── Step 5: Weekly Report Scheduler ──────────────────────────────────
        self._start_weekly_scheduler()

        self._running = True
        logger.info("DevDock is running. Press Ctrl+C to exit.")

        # ── Keep main thread alive ────────────────────────────────────────────
        self._main_loop()

    def _main_loop(self) -> None:
        """Main keep-alive loop."""
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
            self.stop()

    def stop(self) -> None:
        """Graceful shutdown sequence."""
        logger.info("Shutting down DevDock...")
        self._running = False
        watcher_service.stop()
        dashboard_server.stop()
        tray_service.stop()
        logger.info("DevDock stopped.")

    def _start_weekly_scheduler(self) -> None:
        """Start background thread that generates weekly reports."""
        def scheduler():
            import schedule
            try:
                day = settings.get("weekly_report_day", "Sunday")
                schedule.every().week.do(self._generate_weekly_report)
                while self._running:
                    schedule.run_pending()
                    time.sleep(3600)  # Check every hour
            except Exception:
                # schedule not installed, skip
                pass

        self._weekly_report_thread = threading.Thread(target=scheduler, daemon=True)
        self._weekly_report_thread.start()

    def _generate_weekly_report(self) -> None:
        stats = db.get_stats()
        path = devdock_logger.generate_weekly_report(stats)
        logger.info(f"Weekly report generated: {path}")
        notification_service.notify(
            "DevDock Weekly Report",
            f"Report saved to {path.name}",
            duration="short",
        )


def _handle_signal(sig, frame):
    logger.info(f"Signal {sig} received. Exiting...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    app = DevDock()
    app.start()
