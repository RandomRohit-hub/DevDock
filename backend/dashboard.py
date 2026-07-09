"""
DevDock Dashboard (FastAPI)
Local REST API powering the React dashboard at http://localhost:8000
"""

import logging
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings, LOGS_DIR
from database import db
from organizer import organizer
from watcher import watcher_service
from logger import devdock_logger
from notifications import notification_service

logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="DevDock API",
    description="AI-Powered Developer Workspace Manager",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static dashboard
_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(str(_static_dir / "index.html"))


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class SettingsUpdate(BaseModel):
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    monitored_folders: Optional[List[str]] = None
    notifications_enabled: Optional[bool] = None
    duplicate_action: Optional[str] = None
    sensitive_file_warnings: Optional[bool] = None
    auto_start: Optional[bool] = None
    organize_on_startup: Optional[bool] = None
    dashboard_port: Optional[int] = None


class CustomRuleCreate(BaseModel):
    name: str
    condition: str   # filename_contains | extension_equals | filename_starts_with
    value: str
    destination: str


class OrganizeFolderRequest(BaseModel):
    folder_path: str


class RestoreRequest(BaseModel):
    record_id: int


# ─── Health & Status ──────────────────────────────────────────────────────────

@app.get("/api/status")
async def get_status():
    return {
        "status": "running",
        "watcher_active": watcher_service.is_running,
        "watcher_paused": watcher_service.is_paused,
        "monitored_folders": watcher_service.monitored_folders,
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


# ─── Statistics & Dashboard ───────────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats():
    return db.get_stats()


@app.get("/api/activity")
async def get_activity(limit: int = Query(50, ge=1, le=500)):
    return db.get_recent_activity(limit=limit)


# ─── File Records ─────────────────────────────────────────────────────────────

@app.get("/api/files")
async def get_files(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    ai_only: bool = False,
    duplicates_only: bool = False,
    sensitive_only: bool = False,
):
    records = db.get_records(
        limit=limit,
        offset=offset,
        category=category,
        search=search,
        date_from=date_from,
        date_to=date_to,
        ai_only=ai_only,
        duplicates_only=duplicates_only,
        sensitive_only=sensitive_only,
    )
    total = db.count_records()
    return {"files": records, "total": total, "offset": offset, "limit": limit}


@app.get("/api/files/{record_id}")
async def get_file(record_id: int):
    record = db.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ─── Duplicates ───────────────────────────────────────────────────────────────

@app.get("/api/duplicates")
async def get_duplicates():
    return db.get_duplicate_groups()


# ─── Custom Rules ─────────────────────────────────────────────────────────────

@app.get("/api/rules")
async def get_rules():
    return db.get_custom_rules()


@app.post("/api/rules")
async def create_rule(rule: CustomRuleCreate):
    rule_id = db.add_custom_rule(
        name=rule.name,
        condition=rule.condition,
        value=rule.value,
        destination=rule.destination,
    )
    return {"id": rule_id, "message": "Rule created successfully"}


@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: int):
    db.delete_custom_rule(rule_id)
    return {"message": "Rule deleted"}


@app.patch("/api/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: int, enabled: bool):
    db.toggle_custom_rule(rule_id, enabled)
    return {"message": f"Rule {'enabled' if enabled else 'disabled'}"}


# ─── Settings ─────────────────────────────────────────────────────────────────

@app.get("/api/settings")
async def get_settings():
    data = settings.all()
    # Never expose the raw API key to the frontend
    if data.get("groq_api_key"):
        data["groq_api_key"] = "***" + data["groq_api_key"][-4:]
    return data


@app.put("/api/settings")
async def update_settings(update: SettingsUpdate):
    changes = update.model_dump(exclude_none=True)
    settings.update(changes)
    # If API key was updated, mask it in response
    if "groq_api_key" in changes:
        notification_service.notify("DevDock", "Groq API key updated.", duration="short")
    return {"message": "Settings updated", "updated": list(changes.keys())}


# ─── Watcher Control ──────────────────────────────────────────────────────────

@app.post("/api/watcher/pause")
async def pause_watcher():
    watcher_service.pause()
    return {"status": "paused"}


@app.post("/api/watcher/resume")
async def resume_watcher():
    watcher_service.resume()
    return {"status": "resumed"}


@app.post("/api/watcher/add-folder")
async def add_folder(request: OrganizeFolderRequest):
    success = watcher_service.add_folder(request.folder_path)
    return {"success": success, "folder": request.folder_path}


# ─── Manual Organization ──────────────────────────────────────────────────────

@app.post("/api/organize/now")
async def organize_now():
    """Trigger a manual startup scan of all monitored folders."""
    results = []
    for folder_str in settings.monitored_folders:
        folder = Path(folder_str)
        count = organizer.startup_scan(folder)
        results.append({"folder": folder_str, "organized": count})
    return {"results": results}


@app.post("/api/organize/folder")
async def organize_folder(request: OrganizeFolderRequest):
    """Organize all files in a specific folder (drag & drop)."""
    folder = Path(request.folder_path)
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder not found")
    results = organizer.organize_folder(folder)
    return {"organized": len(results), "results": results}


# ─── Restore ──────────────────────────────────────────────────────────────────

@app.post("/api/restore")
async def restore_file(request: RestoreRequest):
    result = organizer.restore_file(request.record_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# ─── Logs ─────────────────────────────────────────────────────────────────────

@app.get("/api/logs")
async def list_logs():
    return {"logs": devdock_logger.get_log_files()}


@app.get("/api/logs/read")
async def read_log(path: str):
    safe_path = Path(path)
    # Security: only allow reading from the logs directory
    try:
        safe_path.relative_to(LOGS_DIR)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"content": devdock_logger.read_log(str(safe_path))}


# ─── Weekly Reports ───────────────────────────────────────────────────────────

@app.post("/api/reports/weekly")
async def generate_weekly_report():
    stats = db.get_stats()
    path = devdock_logger.generate_weekly_report(stats)
    return {"path": str(path), "message": "Weekly report generated"}


# ─── Dashboard Server ─────────────────────────────────────────────────────────

class DashboardServer:
    """Runs the FastAPI server in a background thread."""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None

    def start(self, port: int = 8000, open_browser: bool = False) -> None:
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        logger.info(f"Dashboard API started on http://127.0.0.1:{port}")

        if open_browser:
            import time; time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")

    def stop(self) -> None:
        if self._server:
            self._server.should_exit = True


dashboard_server = DashboardServer()
