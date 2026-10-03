# AquaGuard AI

> **See it. Understand it. Verify it. Act on it.**

> **CRITICAL SCIENTIFIC PRINCIPLE**:
> AquaGuard AI does not confirm pollution. Evidence Confidence represents how strongly available evidence supports a potential aquatic-health anomaly.

---

## 1. Problem Statement

Water-health anomalies—such as toxic algal blooms, industrial spills, sewage overflows, and sudden hypoxic fish kills—frequently go undetected until acute ecological or public health crises emerge. While citizens living along waterways are often the first to notice unusual odors, colors, dead organisms, or surface films, municipal authorities struggle to separate actionable signals from noise.

Conversely, sensor arrays cannot be everywhere, satellite passes lack hyper-local resolution, and single photographs cannot scientifically prove pollution.

---

## 2. Core Innovation: Explainable Evidence Fusion

AquaGuard AI addresses this challenge through:

> **Explainable evidence fusion for citizen-reported water-health anomalies.**

AquaGuard AI transforms raw citizen observations into evidence-backed water-health intelligence by combining:
* Citizen visual observations and text descriptions,
* Community report clusters (spatial-temporal clustering),
* Environmental context data (hydrology, weather, water temperature, dissolved oxygen),
* Historical site baseline patterns, and
* Multimodal AI indicator extraction.

Rather than making unsupported automated claims, AquaGuard AI synthesizes these streams into an explainable **Evidence Confidence** score that prioritizes potential anomalies for human investigation.

---

## 3. Key Concepts

### Evidence Confidence (NOT Citizen Trust Score)
- **Evidence Confidence belongs to an event, NOT to an individual citizen.**
- We never rate or score citizen trustworthiness.
- The score reflects the convergence, consistency, and quality of independent evidence items (supporting vs. conflicting).

### Human-in-the-Loop Verification
- A photograph or citizen report is evidence, **not automatically confirmed truth**.
- AquaGuard AI **NEVER** automatically claims pollution has been detected or confirmed.
- Consequential actions (formal warnings, enforcement, drinking water advisories) require human verification by domain experts and environmental authorities.

### Environmental Context vs. Causation
- Environmental data (e.g. heavy rainfall upstream, seasonal temperature swings) provides vital context; it does not automatically establish pollution causation.
- Any simulated/demo environmental data is strictly labeled with `is_simulated=true`.

---

## 4. Technology Stack

- **Backend**: Python 3.11+ / FastAPI
- **Database**: PostgreSQL with PostGIS extension (spatial types: `Geometry(Point, 4326)`)
- **ORM & Drivers**: SQLAlchemy 2.0, GeoAlchemy2, psycopg / psycopg2-binary
- **Configuration**: Pydantic Settings
- **Testing**: Pytest, FastAPI TestClient, HTTPX
- **Infrastructure**: Docker & Docker Compose (optional local PostgreSQL+PostGIS)

---

## 5. Stage 1 Scope: Project Foundation + Database

Stage 1 establishes the rock-solid architecture foundation and spatial database schema:

- Clean, modular backend project structure.
- PostgreSQL + PostGIS integration with spatial geometries and indexes.
- 11 database schema models:
  - **Core tables**: `reports`, `events`, `environmental_observations`, `ai_analysis`, `evidence_items`, `evidence_scores`.
  - **Structural lifecycle tables**: `verification_events`, `event_history`, `alerts`, `risk_predictions`, `recommended_actions`.
- Explicit simulated data handling (`is_simulated` mandatory flag and guidelines).
- Validated seed JSON datasets (`reports.json`, `environmental_observations.json`).
- Health and database verification endpoints (`GET /health`, `GET /health/db`).
- Complete automated test suite (`pytest -v backend/tests/test_stage1.py`).

*Note: Business logic, report submission APIs, image ingestion, AI models, and frontend dashboards are intentionally deferred to subsequent stages.*

---

## 6. Getting Started

### 1. Database Setup

#### Option A: Docker Compose
```bash
docker compose up -d
```

#### Option B: Local PostgreSQL + PostGIS
Ensure PostgreSQL with PostGIS is running and reachable on port `5432`:
```bash
# Verify PostGIS extension
psql -U postgres -d aquaguard -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 2. Environment Configuration

Copy the example environment configuration:
```bash
cp backend/.env.example backend/.env
```

Default configuration:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aquaguard
ENVIRONMENT=development
APP_NAME=AquaGuard AI
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 3. Install Dependencies & Run Backend

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Endpoints

- **Health check**:
  ```bash
  curl http://localhost:8000/health
  # Response: {"status":"ok","service":"AquaGuard AI"}
  ```

- **Database & PostGIS health**:
  ```bash
  curl http://localhost:8000/health/db
  # Response: {"status":"ok","service":"AquaGuard AI","database":{"connected":true,"postgis_enabled":true,...}}
  ```

- **Swagger Documentation**: Open `http://localhost:8000/docs` in your browser.

---

## 7. Running Tests

Run the Stage 1 test suite:

```bash
pytest -v backend/tests/test_stage1.py
```

All 8 foundational tests verify application health, database connectivity, PostGIS operations, table schemas, spatial storage, and simulated data constraints.

---

## 8. License & Status

Stage 1 is complete and ready as the foundation for Stage 2 (Citizen Reporting Module).
