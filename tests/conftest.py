"""Pytest configuration and fixtures."""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.krishi.database import Base, get_db
from src.krishi.main import app


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_vendor_data():
    """Sample vendor data for testing."""
    return {
        "phone": "9876543210",
        "name": "Test Vendor",
        "role": "vendor",
        "password": "testpass123",
        "address": "Test Village"
    }


@pytest.fixture
def sample_consumer_data():
    """Sample consumer data for testing."""
    return {
        "phone": "9876543211",
        "name": "Test Consumer", 
        "role": "consumer",
        "password": "testpass123",
        "address": "Test Village"
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "product_name": "Tomatoes",
        "price": 40.0,
        "unit": "kg",
        "quantity": 50.0,
        "freshness": 4
    }
