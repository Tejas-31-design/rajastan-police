"""
Pytest configuration and shared fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.ml.url_analyzer import URLAnalyzer
from app.ml.sms_classifier import SMSClassifier


@pytest.fixture(scope="session")
def url_analyzer():
    return URLAnalyzer.get_instance()


@pytest.fixture(scope="session")
def sms_classifier():
    return SMSClassifier.get_instance()


@pytest.fixture(scope="function")
def db_session():
    """In-memory SQLite session for clustering tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
