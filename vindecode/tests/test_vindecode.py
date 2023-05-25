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


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_lookup():
    response = client.get("/lookup/1XPWD40X1ED215307")
    assert response.status_code == 200
    assert response.json() == {
        "vin": "1XPWD40X1ED215307"
    }


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
