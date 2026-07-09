<div align="center">

# ⚓ DevDock

### **Your Downloads Folder. Finally Under Control.**

**AI-Powered Developer Workspace Manager for Windows 11**

<p>
Automatically organize developer files, projects, SSH keys, cloud configurations, documents, and downloads using intelligent rules + AI — all running silently in the background.
</p>

<p>

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>

<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>

<img src="https://img.shields.io/badge/Groq-AI-f55036?style=for-the-badge"/>

<img src="https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows&logoColor=white"/>

<img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge"/>

</p>

> **Download it. Forget about it. DevDock does the rest.**

---

### 🎬 Demo

> *(Replace with your demo GIF later)*

![DevDock Demo](docs/devdock-demo.gif)

</div>

---

# 🤔 Ever downloaded...

* 🔑 SSH Keys
* ☁️ AWS PEM Files
* 🐳 Dockerfiles
* ☸ Kubernetes YAMLs
* 📦 GitHub Projects
* 📄 PDFs
* 🎓 College Notes
* 🖼 Screenshots
* 📜 Certificates
* 📁 ZIP Archives

...and then spent **10 minutes searching for them later?**

### Meet **DevDock**.

DevDock is an intelligent Windows application that watches your **Downloads** folder in real time.

It automatically detects what you downloaded, understands what it is, creates the required folders if needed, organizes everything, keeps detailed logs, and updates a beautiful dashboard.

No manual sorting.

No messy Downloads folder.

No wasted time.

---

# 😵 Before DevDock

```text
Downloads/

resume_final.pdf
resume_final_final.pdf
id_rsa
terraform.tf
Dockerfile
Screenshot (245).png
notes.pdf
invoice.pdf
movie.mp4
project.zip
another_project.zip
```

# 😎 After DevDock

```text
Downloads/

Documents/
Images/
Videos/
Projects/

Programming/
    Python/
    Java/
    JavaScript/

DevOps/
    AWS/
    Docker/
    Kubernetes/
    Terraform/
    SSH Keys/

Certificates/

Archives/
```

---

# ✨ Features

## ⚡ Real-Time Monitoring

DevDock watches your Downloads folder using native Windows file events.

The moment a file is downloaded...

DevDock immediately organizes it.

---

## 🧠 Intelligent Classification

Uses a hybrid classification engine.

### Rule-Based Detection

Perfect for:

* Docker
* Terraform
* Kubernetes
* AWS
* SSH Keys
* Programming Files
* Images
* Videos
* Archives

Fast.

Offline.

No API calls.

---

### 🤖 AI Classification (Groq)

When DevDock isn't sure...

Groq AI understands documents like:

* Resume
* Invoice
* Certificate
* Research Paper
* College Notes
* Personal Documents

It returns:

* Category
* Confidence Score
* Reason

---

## 📦 Smart Project Detection

Downloaded a ZIP?

DevDock detects:

* Python
* Node.js
* Java
* Rust
* Go

Automatically creates the correct project workspace.

---

## 🔒 Sensitive File Protection

Automatically detects:

* SSH Keys
* AWS Credentials
* Private Keys
* Certificates
* Password Files
* Environment Files

Sensitive files are highlighted inside the dashboard.

---

## 📋 Daily Logs

Every action is recorded.

TXT Logs

```text
logs/

2026/
    July/
        2026-07-09.txt
```

SQLite Database

Every move.

Every classification.

Every AI decision.

Nothing gets lost.

---

## 📊 Local Dashboard

Runs locally.

```
http://localhost:8000
```

Dashboard includes:

* 📈 Statistics
* 📂 File History
* 🔍 Search
* 📊 Charts
* 🧠 AI Decisions
* 📋 Activity Logs
* 📦 Duplicate Files
* ⚙ Settings

---

## 🔁 Startup Recovery

Forgot to run DevDock yesterday?

No worries.

When DevDock starts:

✔ Scans Downloads

✔ Finds missed files

✔ Organizes everything

✔ Starts monitoring again

Nothing is ever missed.

---

# ⚙️ How DevDock Works

```text
               Windows Starts
                      │
                      ▼
             DevDock Starts
                      │
                      ▼
         Scan Existing Downloads
                      │
                      ▼
        Start Real-Time Monitoring
                      │
                      ▼
          New File Downloaded
                      │
                      ▼
        Rule-Based Classification
                │
      Match? ───┤
        │       │
      Yes       No
        │       │
        ▼       ▼
   Organize   Groq AI
        │       │
        └───┬───┘
            ▼
    Intelligent Organizer
            │
      ┌─────┼──────────┐
      ▼     ▼          ▼

 SQLite   TXT Logs   Notification

            │
            ▼
     Dashboard Updates
```

---

# 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/RandomRohit-hub/DevDock.git
cd DevDock
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at → [console.groq.com](https://console.groq.com)

### 4. Run

```bash
cd backend
python main.py
```

Or double-click **`start.bat`**

### 5. Open Dashboard

```
http://localhost:8000
```

---

# 🚀 DevDock at a Glance

* ⚡ Real-Time Monitoring
* 🧠 AI File Classification
* 📂 Automatic Folder Creation
* ☁️ DevOps File Detection
* 💻 Programming File Detection
* 📦 Project Detection
* 🔒 Sensitive File Detection
* 🔁 Restore Files
* 📋 Daily TXT Logs
* 🗄 SQLite Database
* 📊 Analytics Dashboard
* 🔔 Windows Notifications
* 🖥 System Tray Support
* 🚀 Startup Recovery
* ⚙ Custom Rules

---

# 💻 Tech Stack

### Desktop

* 🐍 Python
* 👀 Watchdog
* 📁 PyStray
* 🔔 Winotify

### Backend

* ⚡ FastAPI
* 🗄 SQLite

### Frontend

* ⚛ React (CDN)
* 🎨 Tailwind CSS (CDN)
* 📊 Chart.js (CDN)

### AI

* 🧠 Groq API (`llama-3.3-70b-versatile`)

### Utilities

* python-dotenv
* Pillow
* PyPDF2
* python-docx
* Hashlib
* Zipfile

---

# 📁 Project Structure

```text
DevDock/

backend/
    main.py
    watcher.py
    classifier.py
    groq_classifier.py
    organizer.py
    project_detector.py
    duplicate_detector.py
    database.py
    logger.py
    dashboard.py
    notifications.py
    tray.py
    security.py
    config.py
    static/
        index.html

.env.example
requirements.txt
start.bat
```

---

# 🛣 Roadmap

* ✅ Real-Time Monitoring
* ✅ AI Classification
* ✅ Dashboard
* ✅ Duplicate Detection
* ✅ Startup Recovery
* ✅ DevOps Detection
* ✅ Sensitive File Protection
* ✅ Custom Rules
* ✅ Restore Feature
* ⏳ VS Code Integration
* ⏳ GitHub Integration
* ⏳ Plugin System
* ⏳ Cloud Backup
* ⏳ Cross Platform Support
* ⏳ OneDrive Integration

---

# 🌟 Why DevDock?

Because developers should spend their time writing code...

not cleaning the Downloads folder.

DevDock quietly handles the boring work while you focus on building great software.

---

<div align="center">

## ⭐ Enjoying DevDock?

If DevDock made your workflow cleaner, consider giving this repository a **⭐ Star**.

It helps others discover the project and supports future development.

### **Less time organizing files. More time shipping code. 🚀**

</div>
