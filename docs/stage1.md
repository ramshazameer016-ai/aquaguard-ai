# AquaGuard AI — Stage 1: Project Foundation + Database

## 1. Architecture Foundation

AquaGuard AI transforms citizen observations of unusual water conditions into evidence-backed water-health intelligence.

The architectural centerpiece is:
> **Explainable evidence fusion for citizen-reported water-health anomalies.**

### Core Conceptual Axioms

1. **Citizen reports are evidence, NOT confirmed truth.**
   A citizen observation indicates that something unusual was perceived (e.g. dead fish, discolored water, chemical odor). It does not scientifically prove pollution.
2. **Never automatically confirm pollution.**
   AquaGuard AI does not have fields such as `pollution_confirmed`. It maintains epistemic humility.
3. **Evidence Confidence belongs to an event, NOT to a citizen.**
   We do not score citizen trustworthiness; we quantify how strongly combined multimodal evidence supports a potential aquatic anomaly event.
4. **Environmental data provides context, NOT causation.**
   Sensory and contextual measurements (e.g. water temperature, rainfall, dissolved oxygen) provide backdrop, but do not automatically establish causality.
5. **Simulated data must be explicitly labeled.**
   All synthetic or demonstration records have `is_simulated=True` and must be visually demarcated from real data.
6. **Human-in-the-loop verification.**
   Consequential decisions (alerts, enforcement, regulatory action) require human verification by authorized reviewers.

---

## 2. Directory Structure

```text
AquaGuard-AI/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   └── __init__.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   └── models.py
│   │   │
│   │   └── config/
│   │       ├── __init__.py
│   │       └── settings.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_stage1.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   └── .gitkeep
│
├── ai/
│   └── .gitkeep
│
├── data/
│   ├── seed/
│   │   ├── reports.json
│   │   └── environmental_observations.json
│   │
│   └── simulated/
│       └── README.md
│
├── docs/
│   └── stage1.md
│
├── .gitignore
├── pytest.ini
├── README.md
└── docker-compose.yml
```

---

## 3. Database Schema & Tables

AquaGuard AI utilizes **PostgreSQL** with the **PostGIS** extension enabled to support geospatial types (`Geometry(Point, 4326)`) and spatial queries (`ST_DWithin`, `ST_Distance`, `ST_X`, `ST_Y`).

### Primary Foundation Tables (Stage 1 Core)

1. **`reports`**
   - Represents a citizen observation.
   - Fields: `id` (PK, autoincrement), `location` (Geometry Point 4326), `description` (Text), `category` (String), `observed_at` (DateTime TZ), `created_at` (DateTime TZ), `image_path` (String), `reporter_hash` (String).
   - *Constraint*: No `pollution_confirmed` column exists.

2. **`events`**
   - Represents a potential aquatic-health anomaly aggregated from evidence.
   - Fields: `id` (PK, autoincrement), `title` (String), `location` (Geometry Point 4326), `status` (String, default: `'potential'`), `created_at` (DateTime TZ), `updated_at` (DateTime TZ).

3. **`environmental_observations`**
   - Environmental context measurements (rainfall, dissolved oxygen, water temperature, turbidity).
   - Fields: `id` (PK, autoincrement), `location` (Geometry Point 4326), `observed_at` (DateTime TZ), `parameter` (String), `value` (Float), `unit` (String), `source` (String), `data_quality` (String), `is_simulated` (Boolean, mandatory), `created_at` (DateTime TZ).

4. **`ai_analysis`**
   - Foundation for future vision and NLP indicator analysis on citizen reports.
   - Fields: `id` (PK, autoincrement), `report_id` (FK -> `reports.id`), `analysis_type` (String), `indicators` (JSON), `summary` (Text), `model_name` (String), `model_version` (String), `created_at` (DateTime TZ).

5. **`evidence_items`**
   - Granular evidence items associated with an anomaly event.
   - Fields: `id` (PK, autoincrement), `event_id` (FK -> `events.id`), `evidence_type` (String: `photo`, `text`, `community`, `weather`, `water_quality`, `historical`), `source_id` (String), `description` (Text), `direction` (String: `supporting`, `conflicting`, `neutral`), `data_quality` (String), `is_simulated` (Boolean), `created_at` (DateTime TZ).

6. **`evidence_scores`**
   - Storage for the future explainable Evidence Confidence score of an event.
   - Fields: `id` (PK, autoincrement), `event_id` (FK -> `events.id`), `score` (Float), `band` (String: `low`, `moderate`, `high`, `critical`), `calculated_at` (DateTime TZ), `model_version` (String).

### Structural Workflow Foundations (Stages 8–15 Placeholders)

7. **`verification_events`**: Human-reviewer decisions (`confirmed_anomaly`, `natural_phenomenon`, `false_alarm`, `inconclusive`).
8. **`event_history`**: Append-only audit log of state changes for anomaly events.
9. **`alerts`**: Reviewer-approved community and authority alerts.
10. **`risk_predictions`**: Short-term predictive risk outlooks.
11. **`recommended_actions`**: Prescribed field inspections and sampling actions.

---

## 4. Entity Relationships

```text
reports (1) ──────< (0..*) ai_analysis

events (1) ───────< (0..*) evidence_items
events (1) ───────< (0..*) evidence_scores
events (1) ───────< (0..*) verification_events
events (1) ───────< (0..*) event_history
events (1) ───────< (0..*) alerts
events (1) ───────< (0..*) risk_predictions
events (1) ───────< (0..*) recommended_actions
```

---

## 5. Environment Setup & Running

### Prerequisites
- Python 3.11+ (Python 3.12 verified)
- PostgreSQL 16+ or 17+ with PostGIS extension enabled
- (Optional) Docker & Docker Compose

### Starting the Database

#### Option A: Docker Compose
```bash
docker compose up -d
```

#### Option B: Local PostgreSQL + PostGIS (Windows / Linux / macOS)
If using the local portable PostgreSQL 17:
```powershell
& "C:\Users\Admin\pgsql\bin\pg_ctl.exe" -D "C:\Users\Admin\pgsql\data" start
```
Ensure the database exists and PostGIS is enabled:
```sql
CREATE DATABASE aquaguard;
\c aquaguard
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Starting FastAPI

```bash
# Activate your virtual environment
# Windows:
.\aquaguard_venv\Scripts\Activate.ps1

# Install requirements
pip install -r backend/requirements.txt

# Start backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints Available in Stage 1

- `GET /`: Service information, stage scope, and core principles.
- `GET /health`: Basic health check (`{"status": "ok", "service": "AquaGuard AI"}`).
- `GET /health/db`: Database connectivity, PostGIS extension verification, and active tables.
- `GET /docs`: Interactive Swagger OpenAPI documentation.

---

## 6. How to Test

Run the comprehensive Stage 1 test suite:

```bash
pytest -v backend/tests/test_stage1.py
```

The test suite validates:
1. FastAPI app startup and routing.
2. `/health` returns HTTP 200 with service metadata.
3. Database connectivity via `/health/db` and SQLAlchemy engine.
4. PostGIS extension verification (`PostGIS_Version()`).
5. Presence of all 11 foundation and structural tables.
6. Insertion and retrieval of a citizen report.
7. Storage and calculation of spatial point geometries (`ST_X`, `ST_Y`).
8. Insertion of environmental observation with mandatory `is_simulated=True`.
9. Seed JSON validation and round-trip insertion.

---

## 7. What Stage 1 Does NOT Implement (Scope Boundaries)

Stage 1 is strictly limited to the **Project Foundation and Database Schema**. The following are intentionally out of scope:
- Citizen reporting UI / Web application.
- Report submission API (`POST /reports` — Stage 2).
- Image upload / multipart storage workflow.
- CLIP / Vision indicator extraction models (Stage 6).
- Text embeddings / NLP pipelines.
- Real-time environmental API integration.
- Spatial-temporal clustering / DBSCAN.
- Evidence Fusion Engine (Stage 7).
- Evidence Confidence scoring calculation.
- Authority verification dashboard (Stage 8).
- One Health public alerts broadcast.
- Automated sensor IoT ingestion.
