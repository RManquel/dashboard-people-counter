# Stadium People Counter — Full-Stack Dashboard

Real-time stadium occupancy dashboard. People-counter devices POST events to a FastAPI backend → PostgreSQL persists & aggregates → WebSocket broadcasts live updates → React frontend renders a beautiful live dashboard.

## Architecture

```
Internet
    │
    ▼
Application Load Balancer (AWS ALB)
    │
    ├──► ECS Fargate — Frontend (Nginx → React SPA)
    │         │
    │         └── proxy /api/* and /ws → Backend
    │
    └──► ECS Fargate — Backend (FastAPI + Uvicorn)
              │
              └── RDS PostgreSQL
```

## Project Structure

```
dashboard_people_counter/
├── backend/                  # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── main.py           # App factory + lifespan
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   ├── models.py         # ORM: Event, OccupancyStats
│   │   ├── schemas.py        # Pydantic request/response models
│   │   ├── websocket.py      # ConnectionManager
│   │   ├── mqtt.py           # Optional MQTT subscriber
│   │   └── routers/
│   │       ├── alert.py      # POST /api/alert
│   │       ├── stats.py      # GET  /api/stats
│   │       ├── history.py    # GET  /api/history
│   │       ├── health.py     # GET  /health
│   │       └── ws.py         # WS   /ws
│   ├── alembic/              # DB migrations
│   ├── tests/                # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── pages/DashboardPage.jsx
│   │   ├── components/
│   │   │   ├── StatCard.jsx
│   │   │   ├── OccupancyChart.jsx   # Recharts line chart
│   │   │   └── CapacityRing.jsx     # SVG progress ring
│   │   └── hooks/
│   │       ├── useWebSocket.js
│   │       └── useFlash.js
│   ├── nginx.conf
│   └── Dockerfile
├── infrastructure/           # Terraform (AWS)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── vpc/
│       ├── alb/
│       ├── ecs/
│       └── rds/
├── scripts/
│   ├── dev.sh               # Start Docker Compose
│   ├── build.sh             # Build + tag images
│   └── deploy.sh            # Push to ECR + ECS deploy
├── docker-compose.yml
└── .env.example
```

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev without Docker)
- Python 3.12+ (for local backend dev without Docker)
- AWS CLI + Terraform (for AWS deployment)

---

## Quick Start — Docker Compose (Recommended)

```bash
# 1. Clone and enter the project
cd dashboard_people_counter

# 2. Copy the env template
cp .env.example backend/.env

# 3. Start all services (postgres + backend + frontend)
docker compose up --build

# Services available at:
#   Frontend dashboard:  http://localhost
#   Backend API:         http://localhost:8000
#   WebSocket:           ws://localhost:8000/ws
```

### Send a test event

```bash
# Entry event
curl -X POST http://localhost:8000/api/alert \
  -H "Content-Type: application/json" \
  -d '{"device_id": "gate_north", "direction": "in", "timestamp": 1710000000}'

# Exit event
curl -X POST http://localhost:8000/api/alert \
  -H "Content-Type: application/json" \
  -d '{"device_id": "gate_south", "direction": "out", "timestamp": 1710000060}'

# Check current stats
curl http://localhost:8000/api/stats
```

---

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start a local Postgres (or use Docker just for DB)
docker run -d \
  -e POSTGRES_DB=stadium_db \
  -e POSTGRES_USER=stadium \
  -e POSTGRES_PASSWORD=stadium \
  -p 5432:5432 \
  postgres:16-alpine

# Set env vars
cp ../.env.example .env

# Run migrations (optional — app auto-creates tables in dev)
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Run Tests

```bash
cd backend
pip install aiosqlite  # For in-memory SQLite tests
pytest -v
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/alert` | Receive people counter event |
| `GET`  | `/api/stats` | Current occupancy stats |
| `GET`  | `/api/history` | Per-minute activity for last 60 min |
| `GET`  | `/health` | Health check |
| `WS`   | `/ws` | WebSocket for live stats updates |

### POST /api/alert

```json
{
  "device_id": "gate_1",
  "direction": "in",
  "timestamp": 1710000000
}
```

| Field | Type | Values |
|-------|------|--------|
| `device_id` | string | Any non-empty string |
| `direction` | string | `"in"` or `"out"` |
| `timestamp` | integer | Unix timestamp (device clock) |

### GET /api/stats

```json
{
  "people_inside": 23450,
  "entries_today": 24100,
  "exits_today": 650
}
```

### WebSocket `/ws`

Connect via `ws://host/ws`. On each alert event, the backend broadcasts:

```json
{
  "event": "stats_update",
  "data": {
    "people_inside": 23451,
    "entries_today": 24101,
    "exits_today": 650
  }
}
```

---

## Optional: MQTT Support

Set the following environment variables to enable MQTT ingestion from `stadium/gate/events`:

```env
MQTT_BROKER_URL=your.mqtt.broker.host
MQTT_PORT=1883
MQTT_TOPIC=stadium/gate/events
```

MQTT message payload must match the same JSON structure as `POST /api/alert`.

---

## AWS Deployment

### Prerequisites

1. AWS CLI configured: `aws configure`
2. Terraform installed: `terraform -version`
3. Two ECR repositories created:
   - `stadium-backend`
   - `stadium-frontend`

### Steps

```bash
# 1. Build and push Docker images
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1
bash scripts/build.sh
bash scripts/deploy.sh   # First run: skip ECS force-deploy step

# 2. Provision infrastructure
cd infrastructure
terraform init
terraform plan \
  -var="db_password=YourSecurePassword" \
  -var="backend_image=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stadium-backend:latest" \
  -var="frontend_image=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/stadium-frontend:latest"

terraform apply -auto-approve ...

# 3. Get the ALB URL
terraform output alb_dns_name

# 4. For subsequent deploys, just re-run after building:
bash scripts/build.sh && bash scripts/deploy.sh
```

### AWS Services Provisioned

| Service | Purpose |
|---------|---------|
| **ECS Fargate** | Runs backend (FastAPI) + frontend (Nginx) containers |
| **ALB** | Routes HTTP traffic, terminates connections |
| **RDS PostgreSQL 16** | Persistent data store, private subnet, encrypted |
| **CloudWatch Logs** | Container log aggregation (30-day retention) |
| **ECR** | Docker image registry |
| **VPC** | Isolated network with public/private subnets, NAT |

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | CORS allowed origins (JSON array) |
| `APP_ENV` | `development` | Environment name |
| `LOG_LEVEL` | `info` | Uvicorn log level |
| `MQTT_BROKER_URL` | *(empty)* | MQTT broker hostname (disables MQTT if empty) |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `MQTT_TOPIC` | `stadium/gate/events` | MQTT topic to subscribe to |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE` | `""` | API base URL (empty = same origin via Nginx proxy) |
| `VITE_WS_URL` | auto | WebSocket URL (auto-detects host) |
| `VITE_STADIUM_CAPACITY` | `50000` | Max capacity for the capacity ring percentage |

---

## Frontend Dashboard Features

- **Hero panel** — large occupancy counter with live flash animation
- **Capacity ring** — SVG ring showing % of maximum capacity (color-coded: blue → amber → red)
- **3 stat cards** — Current Occupancy, Entries Today, Exits Today
- **Live chart** — Recharts line chart with entries and exits per minute (last 60 min)
- **Connection badge** — Live WebSocket status with auto-reconnect
- **Digital clock** — Real-time clock in the header

---

## Security Highlights

- API payload validation via Pydantic (type-safe, rejects invalid `direction` values)
- CORS restricted to configured origins
- `people_inside` never goes below 0 (floor guard)
- Database password passed via environment variable (never hardcoded)
- RDS in private subnet, only accessible from ECS security group
- ECS task non-root user
- Secrets marked `sensitive = true` in Terraform

---

*Built with FastAPI · PostgreSQL · React · Vite · Recharts · Docker · Terraform*
