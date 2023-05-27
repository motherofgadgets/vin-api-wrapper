import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vindecode.database import Base
from vindecode.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_lookup_new_vin_success():
    vin = "1XPWD40X1ED215307"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XPWD40X1ED215307"
    assert data["make"] == "PETERBILT"
    assert data["model"] == "388"
    assert data["model_year"] == "2014"
    assert data["body_class"] == "Truck-Tractor"
    assert not data["cached"]


def test_lookup_cached_vin_success():
    vin = "1XPWD40X1ED215307"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XPWD40X1ED215307"
    assert data["make"] == "PETERBILT"
    assert data["model"] == "388"
    assert data["model_year"] == "2014"
    assert data["body_class"] == "Truck-Tractor"
    assert data["cached"]


def test_export():
    response = client.get("/export/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/octet-stream"


def test_remove_success():
    vin = "1XPWD40X1ED215307"
    response = client.delete("/remove/{}".format(vin))
    assert response.status_code == 200
    assert response.json() == {
        "vin": vin,
        "deleted": True
    }


def test_remove_fail():
    vin = "4V4NC9EJXEN171694"
    response = client.delete("/remove/{}".format(vin))
    assert response.status_code == 404
