# Placement Portal Application

## Overview

This repository contains a Flask backend and a Vue frontend for a placement portal system.
It includes:
- user authentication for admins, companies, and students
- company and drive approval workflows
- drive search and application export
- Redis/Celery background jobs and scheduled notifications
- email/webhook notifications for reminders, exports, and reports

## Local Development

### 1. Backend setup

```bash
cd /mnt/c/Users/HP/Desktop/MAD-2 Project/Placement-Portal-Application-/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend setup

```bash
cd /mnt/c/Users/HP/Desktop/MAD-2 Project/Placement-Portal-Application-/frontend
npm install
```

### 3. Environment configuration

Copy the example env file into the backend config location and set the required values:

```bash
cd /mnt/c/Users/HP/Desktop/MAD-2 Project/Placement-Portal-Application-
cp .env.example backend/.env
```

Edit `backend/.env` and configure:

- `JWT_SECRET_KEY` — strong secret for JWT tokens
- `REDIS_URL` — e.g. `redis://localhost:6379/0`
- `MAIL_SERVER` — e.g. `smtp.gmail.com`
- `MAIL_PORT` — e.g. `587`
- `MAIL_USE_TLS` — `True` for TLS SMTP
- `MAIL_USERNAME` — SMTP login email
- `MAIL_PASSWORD` — SMTP password or Gmail App Password
- `ADMIN_EMAIL` — admin recipient for reports/test emails
- `APP_BASE_URL` — e.g. `http://localhost:5000`
- `NOTIFICATION_WEBHOOK_URL` — optional webhook URL for JSON notifications

> For Gmail SMTP, use an App Password (not your regular Gmail password) after enabling 2-Step Verification.

### 4. Running backend, frontend, and Celery

#### Backend only

```bash
cd backend
source .venv/bin/activate
python app.py
```

#### Frontend only

```bash
cd frontend
npm run dev
```

#### Run frontend and backend together

```bash
cd frontend
npm run start
```

#### Start Celery worker

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m celery -A services.celery_app worker --loglevel=info
```

#### Start Celery beat scheduler

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m celery -A services.celery_app beat --loglevel=info
```

#### Using Docker Compose

```bash
docker compose up --build
```

Start only backend:

```bash
docker compose up backend
```

Start backend with worker and beat:

```bash
docker compose up backend celery celery-beat
```

Stop all services:

```bash
docker compose down
```

## Application URLs

- Backend API: `http://localhost:5000/api`
- Frontend app: typically the Vite dev server at `http://localhost:5173`

## Mail / notification troubleshooting

### Debug endpoints

The backend exposes two diagnostic endpoints:

- `GET /api/debug/mail-status` — checks whether mail configuration is present
- `POST /api/debug/mail-test` — sends a test SMTP email to `ADMIN_EMAIL`

Use these after restarting the backend.

### Expected behavior

- scheduled daily reminders run at `19:30` IST
- monthly reports run on the 1st at `06:00` IST
- student export jobs complete when triggered
- webhook/email notifications only send if configured in `.env`

### Common issues

- Mail login errors usually mean Gmail requires an App Password
- If Celery worker is not running, scheduled tasks will be scheduled but not executed
- If Redis is not reachable, Celery will fail to enqueue jobs

## Storage locations

- Exported CSV files: `backend/instance/exports`
- Generated reports: `backend/instance/reports`
- SQLite DB: `backend/instance/placement_portal.db`

## Notes

- The backend auto-creates the SQLite database on first startup and seeds a default admin account:
  - email: `admin@placementportal.com`
  - password: `admin123`
- Admins must approve company accounts before companies can create drives.
- Company drives start as `pending` and require admin approval.
- The frontend `npm run start` command launches the backend and Vite dev server together.
- If you change `.env`, restart backend and Celery processes to reload settings.
