import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.main import app
from app.deps import get_db
from app import crud, models, schemas

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "role": models.UserRole.REPORTER
    }
    user = crud.create_user(db_session, schemas.UserCreate(**user_data))
    return user

@pytest.fixture
def test_admin_user(db_session):
    user_data = {
        "email": "admin@example.com",
        "password": "adminpassword",
        "role": models.UserRole.ADMIN
    }
    user = crud.create_user(db_session, schemas.UserCreate(**user_data))
    return user

@pytest.fixture
def test_issue(db_session, test_user):
    issue_data = {
        "title": "Test Issue",
        "description": "Test Description",
        "severity": models.IssueSeverity.MEDIUM,
        "status": models.IssueStatus.OPEN
    }
    issue = crud.create_issue(db_session, schemas.IssueCreate(**issue_data), test_user.id)
    return issue 