import pytest
from app import db, models
from sqlalchemy import delete
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    models.Base.metadata.create_all(bind=db.engine)
    with db.SessionLocal() as session:
        session.execute(delete(models.ScanFinding))
        session.execute(delete(models.ScanRecord))
        session.commit()
        yield session
        session.rollback()


def test_create_get_scan_and_cwe_breakdown(db_session: Session) -> None:
    record = models.create_scan(
        db_session,
        language="python",
        vulnerable=True,
        overall_confidence=0.99,
        findings=[
            {"cwe": "CWE-89", "source": "bandit"},
            {"cwe": None, "source": "model"},
        ],
    )

    fetched = models.get_scan(db_session, record.id)
    assert fetched is not None
    assert fetched.id == record.id
    assert fetched.language == "python"
    assert fetched.vulnerable is True
    assert models.get_scan(db_session, "missing") is None
    assert models.cwe_breakdown(db_session) == [
        {"cwe": "CWE-89", "source": "bandit", "count": 1}
    ]


def test_scans_over_time_uses_shared_session(db_session: Session) -> None:
    record = models.create_scan(
        db_session,
        language="python",
        vulnerable=False,
        overall_confidence=0.0,
    )

    timeline = models.scans_over_time(db_session)
    assert len(timeline) == 1
    assert timeline[0]["scan_id"] == record.id
    assert timeline[0]["vulnerable"] is False
