<div align="center">

# ⚓ DevDock

### AI-Powered Developer Workspace Manager for Windows 11

Automatically organize your Downloads folder using intelligent rules and AI.

No manual sorting. No clutter. No lost files.

<p>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-AI-f55036?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![MIT](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

> **Download files. Forget about organizing them. DevDock handles the rest.**

</div>

---

# 📖 Overview

Developers download hundreds of files every week:

- SSH keys
- AWS PEM files
- ZIP projects
- Dockerfiles
- Kubernetes manifests
- Terraform files
- PDFs
- Screenshots
- Certificates
- College notes

They all end up in one place:

```
Downloads/
```

Eventually, finding anything becomes frustrating.

**DevDock** continuously watches your Downloads folder, understands every new file, automatically moves it to the correct location, logs every action, and keeps everything organized.

---

# ✨ Features

## ⚡ Real-Time Monitoring

- Watches Downloads continuously
- Detects new files instantly
- Organizes files automatically

---

## 🧠 Intelligent Classification

### Rule-Based Engine

Fast offline classification for:

- Docker
- Kubernetes
- Terraform
- AWS
- SSH Keys
- Images
- Videos
- Archives
- Programming files

No API calls required.

---

### AI Classification (Groq)

When rules aren't enough, DevDock asks Groq AI.

Perfect for identifying:

- Resume
- Invoice
- Certificate
- Research Paper
- College Notes
- Personal Documents

Returns:

- Category
- Confidence
- Reasoning

---

## 📦 Smart Project Detection

Automatically detects project archives including:

- Python
- Java
- Node.js
- Rust
- Go

Creates organized workspaces automatically.

---

## 🔒 Sensitive File Detection

Highlights important files including:

- SSH Keys
- AWS Credentials
- PEM Files
- Environment Files
- Private Keys
- Password Files

---

## 📊 Local Dashboard

Runs locally at

```
http://localhost:8000
```

Includes:

- File history
- Search
- Statistics
- Activity logs
- Charts
- Duplicate detection
- AI decisions
- Settings

---

## 📋 Logging

Every action is recorded.

```
logs/
└── 2026/
    └── July/
        └── 2026-07-09.txt
```

Also stored in SQLite for analytics and history.

---

## 🔁 Startup Recovery

If DevDock wasn't running:

- Scans Downloads
- Detects missed files
- Organizes everything
- Resumes monitoring

Nothing gets left behind.

---

# 📂 Before & After

### Before

```text
Downloads/

resume_final.pdf
resume_final_final.pdf
Dockerfile
terraform.tf
Screenshot.png
project.zip
notes.pdf
id_rsa
invoice.pdf
```

### After

```text
Downloads/

Documents/
Images/
Videos/
Archives/
Certificates/

Programming/
    Python/
    Java/
    JavaScript/

Projects/

DevOps/
    AWS/
    Docker/
    Kubernetes/
    Terraform/
    SSH Keys/
```

---

# ⚙️ Architecture

```text
Windows Startup
      │
      ▼
 DevDock Starts
      │
      ▼
 Scan Downloads
      │
      ▼
 Watch for Changes
      │
      ▼
 New File
      │
      ▼
 Rule Engine
   │       │
Match?     No
 │          │
 ▼          ▼
Organize   Groq AI
      │
      ▼
 Move File
      │
      ▼
 SQLite + Logs
      │
      ▼
 Dashboard Update
```

---

# 🚀 Quick Start

## Clone

```bash
git clone https://github.com/RandomRohit-hub/DevDock.git
cd DevDock
```

## Install

```bash
pip install -r requirements.txt
```

## Configure

```bash
cp .env.example .env
```

Add your API key.

```env
GROQ_API_KEY=your_key_here
```

## Run

```bash
cd backend
python main.py
```

or simply run

```
start.bat
```

Open:

```
http://localhost:8000
```

---

# 🚀 Capabilities

- ⚡ Real-Time Monitoring
- 🧠 AI Classification
- 📂 Automatic Folder Creation
- 📦 Project Detection
- 💻 Programming File Detection
- ☁️ DevOps File Detection
- 🔒 Sensitive File Detection
- 📊 Dashboard
- 🗄 SQLite Database
- 📋 Daily Logs
- 🔔 Windows Notifications
- 🖥 System Tray
- 🔁 Startup Recovery
- ⚙ Custom Rules

---

# 💻 Tech Stack

## Desktop

- Python
- Watchdog
- PyStray
- Winotify

## Backend

- FastAPI
- SQLite

## Frontend

- React
- Tailwind CSS
- Chart.js

## AI

- Groq API
- Llama 3.3 70B Versatile

---

# 📁 Project Structure

```text
DevDock/

backend/
│
├── main.py
├── watcher.py
├── classifier.py
├── groq_classifier.py
├── organizer.py
├── project_detector.py
├── duplicate_detector.py
├── database.py
├── logger.py
├── dashboard.py
├── notifications.py
├── tray.py
├── security.py
├── config.py
│
└── static/
    └── index.html

.env.example
requirements.txt
start.bat
```

---

# 🛣 Roadmap

- ✅ Real-Time Monitoring
- ✅ AI Classification
- ✅ Dashboard
- ✅ Duplicate Detection
- ✅ Startup Recovery
- ✅ Sensitive File Detection
- ✅ Custom Rules
- ✅ Restore Files
- ⏳ VS Code Extension
- ⏳ GitHub Integration
- ⏳ Plugin System
- ⏳ Cloud Backup
- ⏳ OneDrive Sync
- ⏳ Cross-Platform Support

---

# 🌟 Why DevDock?

Developers shouldn't waste time cleaning their Downloads folder.

DevDock quietly organizes everything in the background so you can focus on writing code.

---

<div align="center">

## ⭐ Support the Project

If DevDock improved your workflow, consider giving the repository a **⭐ Star**.

**Less time organizing files. More time building software.**

</div>
