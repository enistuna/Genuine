import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.database import Base, get_db
from src.backend.main import app
import src.backend.models as models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    user = models.User(
        username="testuser",
        full_name="Test User",
        tckn="10000000146",
        password_hash="secret"
    )
    db.add(user)
    
    acc = models.Account(
        user_id=1,
        account_type="checking",
        balance=1000.00,
        iban="TR123456"
    )
    db.add(acc)
    db.commit()
    db.close()

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Genuine Backend API (Turkish)"}

def test_get_user_by_tckn():
    response = client.get("/users/tckn/10000000146")
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Test User"
    assert data["balance"] == 1000.0

