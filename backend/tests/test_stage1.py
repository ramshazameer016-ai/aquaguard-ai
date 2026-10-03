"""AquaGuard AI — Stage 1 Foundation & Database Verification Tests.

Verifies:
1. FastAPI application startup and configuration.
2. /health endpoint returns HTTP 200 with service information.
3. Database connection is functional.
4. PostGIS extension is enabled and functioning.
5. All required schema tables exist.
6. A citizen report can be inserted.
7. A spatial point location (PostGIS) can be stored and retrieved.
8. An environmental observation can be inserted with is_simulated=True.
9. Seed data files are valid and loadable.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text, inspect
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from backend.app.main import app
from backend.app.database.connection import engine, SessionLocal, init_db, check_db_connection
from backend.app.database.models import (
    Base,
    Report,
    Event,
    EnvironmentalObservation,
    AIAnalysis,
    EvidenceItem,
    EvidenceScore,
    VerificationEvent,
    EventHistory,
    Alert,
    RiskPrediction,
    RecommendedAction,
)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database schema is initialized for testing."""
    init_db()
    yield


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Database session fixture with rollback cleanup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_1_fastapi_app_starts(client):
    """Test 1: Verify FastAPI application starts and serves requests."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AquaGuard AI" in data["service"]
    assert "Stage 1" in data["stage"]


def test_2_health_endpoint(client):
    """Test 2: Verify /health returns HTTP 200 with expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AquaGuard AI"


def test_3_database_connection(client):
    """Test 3: Verify database connection works via /health/db and engine."""
    # Test via API
    response = client.get("/health/db")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"]["connected"] is True

    # Test via direct engine connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).scalar()
        assert result == 1


def test_4_postgis_extension_exists():
    """Test 4: Verify PostGIS extension is installed and active."""
    with engine.connect() as conn:
        pgis_version = conn.execute(text("SELECT PostGIS_Version();")).scalar()
        assert pgis_version is not None
        assert "3." in str(pgis_version)


def test_5_required_tables_exist():
    """Test 5: Verify all required foundation and structural tables exist."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    required_tables = {
        "reports",
        "events",
        "environmental_observations",
        "ai_analysis",
        "evidence_items",
        "evidence_scores",
        "verification_events",
        "event_history",
        "alerts",
        "risk_predictions",
        "recommended_actions",
    }

    missing = required_tables - existing_tables
    assert not missing, f"Missing required database tables: {missing}"


def test_6_and_7_report_insertion_and_spatial_location(db_session):
    """Test 6 & 7: Verify a report can be inserted and spatial location stored."""
    # Boston Harbor coordinates: longitude -71.0589, latitude 42.3601
    lon, lat = -71.0589, 42.3601
    point_wkt = f"SRID=4326;POINT({lon} {lat})"

    test_report = Report(
        description="[TEST] Citizen noticed murky discoloration near storm drain.",
        category="discoloration",
        location=WKTElement(f"POINT({lon} {lat})", srid=4326),
        observed_at=datetime.now(timezone.utc),
        image_path="test_artifacts/test_report.jpg",
        reporter_hash="testhash1234567890abcdef1234567890abcdef",
    )

    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)

    assert test_report.id is not None

    # Retrieve and verify spatial query
    retrieved = db_session.query(Report).filter(Report.id == test_report.id).first()
    assert retrieved is not None
    assert retrieved.category == "discoloration"
    assert retrieved.description == "[TEST] Citizen noticed murky discoloration near storm drain."

    # Verify spatial coordinates via PostGIS ST_X / ST_Y
    with engine.connect() as conn:
        coords = conn.execute(
            text("SELECT ST_X(location::geometry), ST_Y(location::geometry) FROM reports WHERE id = :id"),
            {"id": test_report.id},
        ).fetchone()
        assert coords is not None
        assert round(coords[0], 4) == round(lon, 4)
        assert round(coords[1], 4) == round(lat, 4)

    # Clean up test record
    db_session.delete(test_report)
    db_session.commit()


def test_8_environmental_observation_is_simulated(db_session):
    """Test 8: Verify environmental observation insertion with mandatory is_simulated=True."""
    obs = EnvironmentalObservation(
        location=WKTElement("POINT(-71.0592 42.3605)", srid=4326),
        observed_at=datetime.now(timezone.utc),
        parameter="dissolved_oxygen",
        value=4.2,
        unit="mg/L",
        source="test_simulated_sensor",
        data_quality="provisional",
        is_simulated=True,
    )

    db_session.add(obs)
    db_session.commit()
    db_session.refresh(obs)

    assert obs.id is not None
    assert obs.is_simulated is True
    assert obs.parameter == "dissolved_oxygen"
    assert obs.value == 4.2

    # Clean up test record
    db_session.delete(obs)
    db_session.commit()


def test_9_seed_data_validation(db_session):
    """Test 9: Verify seed data JSON files exist, parse correctly, and can be inserted."""
    reports_file = SEED_DIR / "reports.json"
    env_file = SEED_DIR / "environmental_observations.json"

    assert reports_file.exists(), "Seed reports.json must exist"
    assert env_file.exists(), "Seed environmental_observations.json must exist"

    with open(reports_file, "r", encoding="utf-8") as rf:
        reports_data = json.load(rf)
    assert len(reports_data) > 0, "Seed reports must not be empty"

    with open(env_file, "r", encoding="utf-8") as ef:
        env_data = json.load(ef)
    assert len(env_data) > 0, "Seed environmental observations must not be empty"

    inserted_reports = []
    for item in reports_data:
        rep = Report(
            description=item["description"],
            category=item.get("category"),
            location=WKTElement(f"POINT({item['longitude']} {item['latitude']})", srid=4326),
            observed_at=datetime.fromisoformat(item["observed_at"]),
            image_path=item.get("image_path"),
            reporter_hash=item.get("reporter_hash"),
        )
        db_session.add(rep)
        inserted_reports.append(rep)

    inserted_obs = []
    for item in env_data:
        obs = EnvironmentalObservation(
            location=WKTElement(f"POINT({item['longitude']} {item['latitude']})", srid=4326),
            observed_at=datetime.fromisoformat(item["observed_at"]),
            parameter=item["parameter"],
            value=item["value"],
            unit=item["unit"],
            source=item["source"],
            data_quality=item.get("data_quality", "provisional"),
            is_simulated=item["is_simulated"],
        )
        assert obs.is_simulated is True, "Seed environmental data must have is_simulated=True"
        db_session.add(obs)
        inserted_obs.append(obs)

    db_session.commit()

    # Verify counts
    for rep in inserted_reports:
        db_session.refresh(rep)
        assert rep.id is not None
        db_session.delete(rep)

    for obs in inserted_obs:
        db_session.refresh(obs)
        assert obs.id is not None
        db_session.delete(obs)

    db_session.commit()
