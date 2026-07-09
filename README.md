<div align="center">

<h1>🚀 DevDock</h1>
<p><strong>AI-Powered Developer Workspace Manager for Windows 11</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-AI-f55036?style=for-the-badge&logo=groq&logoColor=white"/>
  <img src="https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<p>DevDock silently watches your Downloads folder, automatically classifies every file using rules + Groq AI, organizes it into a structured hierarchy, detects duplicates and sensitive files, and gives you a beautiful local web dashboard — all in the background like OneDrive or Windows Defender.</p>

![DevDock Dashboard](https://raw.githubusercontent.com/RandomRohit-hub/DevDock/main/docs/dashboard-preview.png)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Real-Time Monitoring** | Watchdog event-based monitoring — zero CPU when idle |
| 🧠 **AI Classification** | Groq LLM classifies ambiguous files (resumes, invoices, research papers) |
| 📁 **Auto Organization** | Moves files into structured folders: DevOps, Programming, Projects, etc. |
| 🔒 **Sensitive File Detection** | Flags `.pem`, SSH keys, AWS credentials before moving |
| 🔄 **Duplicate Detection** | SHA-256 hashing — skip, rename, replace, or keep both |
| 📦 **Project Detection** | Detects Node/Python/Rust/Go projects inside downloaded archives |
| 🔁 **Restore Feature** | Every move is reversible from the dashboard |
| 📋 **Daily Logs** | Structured TXT logs at `logs/YYYY/Month/YYYY-MM-DD.txt` |
| 📊 **Web Dashboard** | Local React SPA at `http://localhost:8000` with Chart.js charts |
| 🖥️ **System Tray** | Runs silently — pause, resume, organize, exit from tray |
| 🔔 **Notifications** | Native Windows 11 toast notifications |
| ⚙️ **Custom Rules** | Define your own rules — no coding needed |
| 🚀 **Startup Recovery** | Organizes everything downloaded while DevDock was offline |

---

## 📋 Requirements

- **Windows 10 / 11**
- **Python 3.10 or higher** → [Download Python](https://www.python.org/downloads/)
- **Groq API Key** (free) → [Get yours at console.groq.com](https://console.groq.com)
- Git (optional, for cloning)

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/RandomRohit-hub/DevDock.git
cd DevDock
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run DevDock

**Option A — Double-click** `start.bat`

**Option B — Terminal:**
```bash
cd backend
python main.py
```

### 4. Open the Dashboard

DevDock automatically opens your browser to:
```
http://localhost:8000
```

---

## 🔑 Adding Your Groq API Key

1. Go to [console.groq.com](https://console.groq.com) → create a free account → copy your API key
2. Open the dashboard at `http://localhost:8000`
3. Click **Settings** in the left sidebar
4. Paste your key into **Groq API Key** and click **Save Settings**

> **Without a Groq key**, DevDock still works perfectly — it uses rule-based classification for all common file types. Groq AI is only called for ambiguous documents like resumes, invoices, and research papers.

---

## 📂 What DevDock Creates

DevDock automatically creates this folder structure inside your Downloads folder:

```
Downloads/
├── Documents/
├── Images/
├── Videos/
├── Music/
├── Archives/
├── Certificates/
├── Datasets/
├── AI/
├── Others/
│
├── Programming/
│   ├── Python/        ← .py, requirements.txt, setup.py
│   ├── JavaScript/    ← .js, .jsx, package.json
│   ├── TypeScript/    ← .ts, .tsx, tsconfig.json
│   ├── Go/            ← .go, go.mod
│   ├── Rust/          ← .rs, Cargo.toml
│   ├── Java/          ← .java, pom.xml, build.gradle
│   ├── C++/           ← .cpp, .c, .h
│   ├── C#/            ← .cs, .csproj
│   ├── PHP/           ← .php
│   └── Other/
│
├── DevOps/
│   ├── AWS/           ← *.pem, credentials
│   ├── Docker/        ← Dockerfile, docker-compose.yml
│   ├── Kubernetes/    ← deployment.yaml, kubeconfig
│   ├── Terraform/     ← *.tf, *.tfvars
│   ├── SSH Keys/      ← id_rsa, id_ed25519, *.pub
│   ├── Azure/
│   ├── GCP/
│   ├── Linux/
│   ├── Certificates/
│   └── Configs/
│
└── Projects/
    ├── Python/        ← Archives containing requirements.txt
    ├── Node/          ← Archives containing package.json
    ├── Java/          ← Archives containing pom.xml
    ├── Rust/          ← Archives containing Cargo.toml
    ├── Go/            ← Archives containing go.mod
    └── Git Repositories/
```

---

## 🧠 How Classification Works

```
New file arrives in Downloads
         │
         ▼
① Custom Rules      ── your own rules from Settings
         │ no match
         ▼
② Rule-Based        ── extension, filename, pattern matching
   Classifier          (instant, no API call)
         │ no match
         ▼
③ Groq AI           ── reads file snippet → returns JSON
   Classifier          { category, confidence, reason }
         │
         ▼
File moved to correct subfolder
```

**Rule-based classification handles ~90% of files instantly.** Groq AI is only called for ambiguous documents.

---

## 🖥️ Dashboard Pages

| Page | Description |
|---|---|
| **Home** | Stats cards, category doughnut chart, weekly activity bar chart, recent activity feed |
| **All Files** | Searchable, filterable table of every organized file with restore button |
| **Duplicate Files** | SHA-256 grouped duplicate file list |
| **Activity Logs** | Full audit trail of every action DevDock took |
| **Settings** | Groq API key, duplicate handling, notifications, custom rules |

---

## ⚙️ Custom Rules

Create your own rules in the **Settings** page — no coding needed.

**Examples:**

| Condition | Value | Destination |
|---|---|---|
| filename contains | `leetcode` | `Programming/DSA` |
| extension equals | `.csv` | `Datasets` |
| filename starts with | `invoice` | `Documents/Invoices` |

---

## 🔒 Sensitive File Handling

DevDock automatically detects and flags these files before moving:

- Private SSH keys (`id_rsa`, `id_ed25519`, `id_ecdsa`)
- AWS credentials and `.pem` files
- Files containing `password`, `secret`, `api_key` in name
- Files whose content contains private key headers

Sensitive files are moved to their correct location **and** flagged with a 🔒 badge in the dashboard.

---

## 🔁 Restoring Files

Every file DevDock moves can be sent back to its original location:

1. Go to **All Files** in the dashboard
2. Find the file
3. Click **Restore**

---

## 🛠️ System Tray

Right-click the DevDock icon in the Windows System Tray:

| Option | Action |
|---|---|
| 🌐 Open Dashboard | Opens `http://localhost:8000` in browser |
| ⚡ Organize Now | Manual scan of monitored folders |
| ⏸ Pause Monitoring | Temporarily stop file watching |
| ▶ Resume Monitoring | Resume after pause |
| 📋 Open Logs Folder | Opens the logs directory in Explorer |
| ⚙ Settings | Opens Settings page in browser |
| ✕ Exit DevDock | Gracefully stops all services |

---

## 📁 Project Structure

```
DevDock/
├── start.bat                  ← Launch script (double-click to run)
├── requirements.txt           ← Python dependencies
├── .gitignore
│
└── backend/
    ├── main.py                ← Entry point & orchestrator
    ├── config.py              ← Settings, rules, folder structure
    ├── database.py            ← SQLite persistence
    ├── logger.py              ← Daily TXT log writer
    ├── organizer.py           ← Core file pipeline
    ├── watcher.py             ← Watchdog real-time monitor
    ├── classifier.py          ← Rule-based classifier
    ├── groq_classifier.py     ← Groq AI fallback classifier
    ├── duplicate_detector.py  ← SHA-256 duplicate detection
    ├── security.py            ← Sensitive file detection
    ├── project_detector.py    ← Archive project detection
    ├── dashboard.py           ← FastAPI REST API (20+ endpoints)
    ├── notifications.py       ← Windows toast notifications
    ├── tray.py                ← System tray icon
    └── static/
        └── index.html         ← React SPA dashboard
```

---

## 🔌 API Reference

DevDock exposes a full REST API at `http://localhost:8000/api/`

```
GET  /api/status          → Watcher status
GET  /api/stats           → Dashboard statistics
GET  /api/files           → File records (search, filter, paginate)
POST /api/organize/now    → Trigger manual scan
POST /api/restore         → Restore file to original location
GET  /api/rules           → Custom rules
POST /api/rules           → Create custom rule
GET  /api/settings        → Current settings
PUT  /api/settings        → Update settings
POST /api/watcher/pause   → Pause monitoring
POST /api/watcher/resume  → Resume monitoring
GET  /api/duplicates      → Duplicate file groups
GET  /api/logs            → List log files
POST /api/reports/weekly  → Generate weekly report
```

Full interactive docs: `http://localhost:8000/docs`

---

## 🧱 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.13 | Rich ecosystem, OS integration, file I/O |
| API Server | FastAPI + Uvicorn | Fastest Python async framework |
| File Monitoring | Watchdog | OS-native events, zero CPU when idle |
| Database | SQLite | Zero config, single file, WAL concurrency |
| AI | Groq API (llama-3.3-70b) | Fastest LLM inference (~200ms responses) |
| Document Parsing | PyPDF2, python-docx | Text extraction for AI classification |
| System Tray | pystray + Pillow | Native Win32 system tray integration |
| Notifications | winotify | Native Windows 11 toast notifications |
| Dashboard UI | React 18 + Chart.js | CDN-loaded, no build step needed |
| Styling | Tailwind CSS CDN | Utility-first, no build tooling |

---

## 🐛 Troubleshooting

**Dashboard doesn't open?**
```bash
# Check if port 8000 is free
netstat -ano | findstr :8000
# Run manually
cd backend && python main.py
```

**Files not being organized?**
- Check that your Downloads folder path is correct in Settings
- Ensure DevDock is not paused (check System Tray)
- Run "Organize Now" from the tray or dashboard

**Groq AI not working?**
- Verify your API key in Settings
- Check your Groq account at [console.groq.com](https://console.groq.com)
- DevDock falls back to rule-based classification automatically

**pystray / tray icon error?**
```bash
pip install pystray Pillow --upgrade
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  <p>Built with ❤️ for developers who hate messy Downloads folders</p>
  <p><strong>⭐ Star this repo if DevDock saved your sanity!</strong></p>
</div>
