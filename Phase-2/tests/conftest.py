import pytest
from app import app as flask_app
from db import Base, engine, SessionLocal
import os

@pytest.fixture
def app():
    """Create application for the tests."""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    })
    return flask_app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def session():
    """Create database session for the tests."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    } 