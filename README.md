# Placement Portal Application

## Run locally with Docker Compose

This repository now includes Redis and Celery support for background jobs and scheduled tasks.

### Start services

```bash
docker compose up --build
```

This starts:
- `backend` at `http://localhost:5000`
- `redis` on `localhost:6379`
- `celery` worker
- `celery-beat` scheduler

### Useful commands

Run only backend:

```bash
docker compose up backend
```

Run backend plus worker and beat:

```bash
docker compose up backend celery celery-beat
```

Stop everything:

```bash
docker compose down
```

### Environment

Copy `.env.example` to `backend/.env` and set values.

Required values:
- `JWT_SECRET_KEY`
- `REDIS_URL`
- `MAIL_SERVER`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `ADMIN_EMAIL`
- `APP_BASE_URL`
- `NOTIFICATION_WEBHOOK_URL` (optional)

### Notes

- The Celery worker processes scheduled jobs via `celery-beat`.
- Email notifications and webhook calls work only if the corresponding environment variables are configured.
- Exported CSV files are stored in `backend/instance/exports`.
- Monthly reports are stored in `backend/instance/reports`.
