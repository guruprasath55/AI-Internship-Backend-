AI Internship Management System Dashboard Backend


This repository provides a lightweight FastAPI backend for an AI Internship Management System dashboard. It handles live tracking of metrics such as total students, total mentors, active batches, and real-time attendance analytics calculated from historical logs.

🛠️ Tech Stack

Framework: FastAPI (Python)

ASGI Web Server: Uvicorn

Database Object-Relational Mapping (ORM): SQLAlchemy

Database Engine: MySQL

🚀 Step-by-Step Setup and Execution Commands
Follow these execution steps in sequence to clear historical database overrides, seed clean records, and bring up your backend server.

# Installation and Setup

### 1. Create a virtual environment and activate it

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate

pip install fastapi uvicorn sqlalchemy pymysql

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE attendance;
TRUNCATE TABLE students;
SET FOREIGN_KEY_CHECKS = 1;

python generate_data.py

uvicorn main:app --reload --port 8000
