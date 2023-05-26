import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vindecode.crud import create_decoded_vin
from vindecode.database import Base
from vindecode.schemas import DecodedVINCreate
from vindecode.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_vins(test_db):
    db_vin = DecodedVINCreate(
        vin="1XPWD40X1ED215307",
        make="PETERBILT",
        model="388",
        model_year="2014",
        body_class="Truck-Tractor"
    )
    create_decoded_vin(test_db, db_vin)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_lookup_success(test_db_vins, test_db):
    vin = "1XPWD40X1ED215307"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XPWD40X1ED215307"
    assert data["make"] == "PETERBILT"
    assert data["model"] == "388"
    assert data["model_year"] == "2014"
    assert data["body_class"] == "Truck-Tractor"


def test_lookup_not_found(test_db):
    vin = "1XKWDB0X57J211825"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 404


def test_create_new_vin_success(test_db):
    vin_data = {
            "vin": "1XKWDB0X57J211825",
            "make": "KENWORTH",
            "model": "W9 Series",
            "model_year": "2007",
            "body_class": "Truck-Tractor"
        }
    response = client.post(
        "/vins/",
        json=vin_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data == vin_data


def test_create_existing_vin_success(test_db):
    vin_data = {
            "vin": "1XPWD40X1ED215307",
            "make": "PETERBILT",
            "model": "388",
            "model_year": "2014",
            "body_class": "Truck-Tractor"
        }
    response = client.post(
        "/vins/",
        json=vin_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data == vin_data


def test_remove():
    response = client.get("/remove/1XPWD40X1ED215307")
    assert response.status_code == 200
    assert response.json() == {
        "remove vin": "1XPWD40X1ED215307"
    }


def test_export():
    response = client.get("/export/")
    assert response.status_code == 200
    assert response.json() == {
        "export": "complete"
    }
