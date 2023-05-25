import pytest
from fastapi.testclient import TestClient

from vindecode.main import app


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
