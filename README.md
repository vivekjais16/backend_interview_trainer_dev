# ⚡ AI Python Backend & MNC Interview Trainer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An open-source, interactive, Jupyter-style **AI Backend Interview Trainer** tailored for **MNC Technical Rounds** (Google, Amazon, Microsoft, Uber, Stripe, Razorpay). Features a sandboxed **Python Interpreter**, **SQL Compiler with EXPLAIN query plan analysis**, **Theoretical Mind Maps**, and **Adaptive GenAI Bar Raiser Cross-Questioning** calibrated strictly to candidate years of experience.
> 
> **100% Free & Open-Source for Everyone to Prepare According to Their Experience Level!**

---

## 🎯 Why This Platform?

Most technical interview preparation resources either focus purely on algorithmic LeetCode or static theory. Real MNC backend interviews evaluate:
1. **Low-level language internals** (GIL, CPython memory allocator, MRO, garbage collection generations).
2. **High-concurrency failure modes** (Event loop starvation, connection pool exhaustion, lost updates).
3. **Database execution realities** (B+ Tree indexing, leftmost prefix rule, MVCC, Next-Key deadlocks, EXPLAIN cost).
4. **Ruthless cross-questioning** ("You chose a Redis distributed lock, what happens when garbage collection halts the worker and the TTL expires before completion?").

This platform bridges that gap by providing a hands-on, notebook-driven simulation of real MNC system design and backend technical rounds.

---

## ✨ Key Features

### 1. 🎓 Adaptive Experience Calibration
Select your experience level, and the entire platform (questions, depth of analysis, cross-question grilling, and rubrics) dynamically recalibrates:
- **🟢 Junior (0 - 2 YOE)**: Core Python internals, mutable default arguments, object reference equality, basic SQL joins & window functions (`DENSE_RANK()`), REST APIs, and Big-O complexities.
- **🟡 Mid-Level (3 - 5 YOE)**: Concurrency models (`asyncio` event loop blocking vs `to_thread`), FastAPI dependency injection lifecycle, SQLAlchemy N+1 query optimization, composite index leftmost prefix rule, transaction isolation.
- **🟣 Senior (6 - 9 YOE)**: Flash-sale race condition prevention, atomic conditional SQL decrements, distributed locks (Redis Redlock vs Lua), idempotent payment webhook state machines, MySQL deadlock mitigation under high writes.
- **🔴 Staff / Architect (10+ YOE)**: Dual-write consistency (Transactional Outbox Pattern + Debezium CDC), distributed consensus, zero-downtime online schema migrations, multi-region database replication lag, and P99 incident troubleshooting.

---

### 2. 🐍 Sandboxed Python Interpreter
- Run Python 3.12 code directly in the browser with **sub-millisecond execution tracking**.
- **AST Security Guard**: Prevents dangerous system calls (`os.system`, `subprocess`, socket manipulation).
- **Infinite Loop & Deadlock Watchdog**: Multiprocess execution timeout protection.
- Immediate standard output (`stdout`), standard error (`stderr`), and returned values.

---

### 3. 🗄️ Isolated SQL Compiler & Query Plan Analyzer
- Practice real-world SQL against 3 pre-populated enterprise schemas:
  - 🛒 **E-Commerce & Orders**: `customers`, `products`, `orders`, `order_items` with indexed foreign keys.
  - 💳 **FinTech Payments & Ledger**: `accounts`, `transactions` with unique `idempotency_key` constraints.
  - 🏢 **HR & Enterprise Analytics**: `departments`, `employees`, `performance_reviews`.
- **Automatic `EXPLAIN QUERY PLAN`**: Teaches candidates whether their query performs an instant B-Tree index lookup or a costly full table scan (`SCAN TABLE`).

---

### 4. 🧠 Interactive Theoretical Mind Maps
- Visual Mermaid architecture diagrams for core backend domains:
  - **Python Internals & Memory Architecture**
  - **High-Throughput Asyncio & Concurrency**
  - **FastAPI, Pydantic V2 & Production Microservices**
  - **MySQL InnoDB Internals, Indexing & Transactions**
  - **MNC Production Troubleshooting & System Design**
- Deep node breakdowns with **"What MNC Interviewers Look For"**, code snippets, and common traps.

---

### 5. 🎙️ GenAI Bar Raiser & Deep Cross-Questioning
- Evaluates candidate architectural explanations, code, and SQL against a 5-dimension MNC rubric.
- **Sharp Probing Follow-Up Cross Questions**: Simulates a FAANG Bar Raiser digging into hand-wavy claims.
- **Multi-Provider Support**:
  - `mock`: Built-in offline deterministic Bar Raiser engine (zero API keys needed, 100% free forever!).
  - `gemini`: Google Gemini 1.5 Flash / Pro.
  - `openai`: OpenAI GPT-4o / GPT-4o-mini.
  - `ollama`: Local open-source models (`llama3`, `mistral`, `deepseek`).

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    User["Candidate Web Browser (Jupyter UI)"] -->|HTTP / JSON| FastAPI["FastAPI Application (Port 8000)"]
    
    subgraph FastAPI Application
        Router["API Router (/api/v1)"]
        
        Router --> Questions["Questions & Roadmap Engine"]
        Router --> PyRunner["Sandboxed Python Runner (AST + Timeout)"]
        Router --> SQLRunner["SQL Compiler & EXPLAIN Analyzer"]
        Router --> InterviewEngine["AI Bar Raiser Interviewer"]
        
        InterviewEngine --> AIAdapter{"AI Provider"}
        AIAdapter -->|Free Default| OfflineEngine["Deterministic MNC Engine"]
        AIAdapter -->|Optional| Gemini["Google Gemini API"]
        AIAdapter -->|Optional| OpenAI["OpenAI GPT-4o API"]
        AIAdapter -->|Optional| Ollama["Local Ollama LLM"]
    end
    
    subgraph Storage Layer
        DBEngine{"Database Engine"}
        FastAPI --> DBEngine
        DBEngine -->|Production Mode| MySQL[("MySQL 8.0 Database")]
        DBEngine -->|Zero-Config Fallback| SQLite[("Local SQLite Database")]
    end
```

---

## 🚀 Quickstart Guide

### Option 1: Fast Local Setup (Zero-Config, Automatic Fallback)

Requires **Python 3.10+**. If MySQL is not running on your machine, the application will **automatically fall back to local SQLite** so you can start preparing immediately!

```bash
# 1. Clone repository
git clone -b dev https://github.com/vivekjais16/backend_interview_trainer_dev.git
cd backend_interview_trainer_dev

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Launch the application
python run.py
```

Open your browser at: **[http://localhost:8000](http://localhost:8000)**

Interactive API Swagger documentation is at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

### Option 2: Full Docker & MySQL 8 Setup (Recommended for Production)

Run the full stack with dedicated MySQL 8.0 container using Docker Compose:

```bash
# Build and run containers
docker-compose up --build -d

# View logs
docker-compose logs -f
```

The MySQL service will automatically start, initialize health checks, and mount persistent volumes.

---

## ⚙️ Environment Configuration (`.env`)

```ini
# Application
APP_NAME="AI Python Backend & MNC Interview Trainer"
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Database Configuration (MySQL default with automatic SQLite fallback)
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/interview_trainer
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_AUTO_FALLBACK_SQLITE=True

# GenAI Engine: "mock", "gemini", "openai", "ollama"
AI_PROVIDER=mock
GEMINI_API_KEY=""
OPENAI_API_KEY=""
OLLAMA_BASE_URL="http://localhost:11434"
AI_MODEL_NAME="gemini-1.5-flash"

# Sandbox Limits
CODE_EXECUTION_TIMEOUT_SECONDS=5
MAX_EXECUTION_MEMORY_MB=128
SQL_MAX_ROWS=100
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Interactive Jupyter-style Web UI |
| `GET` | `/api/v1/questions` | List interview questions with experience level & company filters |
| `GET` | `/api/v1/questions/{id_or_slug}` | Get question detail, scenarios, starter code & cross questions |
| `POST` | `/api/v1/sandbox/python` | Run sandboxed Python code with execution duration & output |
| `POST` | `/api/v1/sandbox/sql` | Execute SQL query with `EXPLAIN` query plan analysis |
| `GET` | `/api/v1/sandbox/sql/schemas` | Get metadata for E-Commerce, FinTech, and HR schemas |
| `POST` | `/api/v1/interview/sessions` | Initialize a new MNC mock interview session |
| `POST` | `/api/v1/interview/turns` | Submit answer/code for AI Bar Raiser evaluation & cross-questions |
| `GET` | `/api/v1/interview/sessions/{id}` | Retrieve complete interview turn history and score |
| `GET` | `/api/v1/mindmaps` | Get all theoretical mindmap roadmaps and Mermaid diagrams |
| `GET` | `/api/v1/mindmaps/{slug}` | Get specific mindmap topic with deep concept breakdowns |
| `GET` | `/api/v1/analytics/stats` | System health check, database status, and question stats |

---

## 🧪 Running Automated Tests

The test suite validates the Python AST sandbox, SQL compiler, schemas, and API routers:

```bash
# Run pytest with detailed verbose output
pytest -v
```

---

## 🌿 Git Branch & Repository

- **Repository**: [https://github.com/vivekjais16/backend_interview_trainer_dev.git](https://github.com/vivekjais16/backend_interview_trainer_dev.git)
- **Active Branch**: `dev`

To push changes to your GitHub branch:
```bash
git add .
git commit -m "feat: complete AI Python backend & MNC interview trainer platform with Jupyter sandbox"
git push -u origin dev
```

---

## 🤝 Contributing

We welcome contributions from engineers across all experience levels!
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/NewMNCQuestion`).
3. Commit your Changes (`git commit -m 'feat: add Kafka partition rebalancing scenario'`).
4. Push to the Branch (`git push origin feature/NewMNCQuestion`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
