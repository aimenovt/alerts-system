# Event Processing Platform Backend

Production-ready FastAPI backend scaffold with clean architecture, async PostgreSQL access, JWT authentication, Alembic migrations, and Docker Compose.

## Tech Stack

- FastAPI
- PostgreSQL
- RabbitMQ (aio-pika)
- SQLAlchemy (async)
- Psycopg 3 async driver
- Alembic
- Pydantic Settings
- JWT (`python-jose`)
- Docker / Docker Compose

## Quick Start

1. Copy environment file:
   - `cp .env.example .env` (Linux/macOS) or `Copy-Item .env.example .env` (PowerShell)
2. Run with Docker:
   - `docker compose up --build`
3. Open docs:
   - `http://localhost:8001/docs`
4. RabbitMQ management UI:
   - `http://localhost:15672` (user/password from `.env`)

## RabbitMQ Architecture

```text
POST /events → API saves event (status=queued) → publish to RabbitMQ
                                              ↓
                                    worker consumes message
                                              ↓
                              status: processing → processed
```

- **API** = producer (publish only)
- **worker** = consumer (`python -m app.workers.main`)
- Failed messages go to dead-letter queue `events.processing.dlq`

Local dev without Docker RabbitMQ: set `RABBITMQ_ENABLED=false` in `.env` (events stay `queued`).

## Local Development

1. Bootstrap dependencies and smoke test:
   - `./scripts/bootstrap.sh` (Linux/macOS)
   - `.\scripts\bootstrap.ps1` (Windows PowerShell)
2. Run API:
   - `uvicorn app.main:app --reload`
3. Apply migrations:
   - `alembic upgrade head`

## Migration Workflow

- Create migration:
  - `alembic revision --autogenerate -m "create initial tables"`
- Apply migration:
  - `alembic upgrade head`
