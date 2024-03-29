from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vindecode.database import Base
from vindecode.main import app, get_db, get_external_client
from vindecode.vinextclient import VINExternalClient

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

ext_test_client = MagicMock(spec=VINExternalClient)


def override_get_db():
    """
    Overrides the app's get_db method to return the test database
    :return: A database session that is closed when a request is finished.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_external_client():
    """
    Overrides the app's get_external_client to return a Mocked HTTP client for testing
    :return: a Mocked HTTP client
    """
    return ext_test_client


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_external_client] = override_get_external_client

client = TestClient(app)


def test_lookup_new_vin_success():
    """
    Tests that when the lookup endpoint is given a new VIN, it calls the external client,
    and responds that the VIN has not been cached.
    """
    success_response = {
        "ErrorCode": "0",
        "Make": "TestMake",
        "Model": "TestModel",
        "ModelYear": "TestModelYear",
        "BodyClass": "TestBodyClass",
    }
    ext_test_client.get_vin.return_value = success_response

    vin = "1XPWD40X1ED215307"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == vin
    assert data["make"] == success_response["Make"]
    assert data["model"] == success_response["Model"]
    assert data["model_year"] == success_response["ModelYear"]
    assert data["body_class"] == success_response["BodyClass"]
    assert not data["cached"]


def test_lookup_cached_vin_success():
    """
    Tests that when the lookup endpoint is given a VIN that has previously been cached,
    it does not the external client, and responds that the VIN has been cached.
    """
    vin = "1XPWD40X1ED215307"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["vin"] == "1XPWD40X1ED215307"
    assert data["make"] == "TestMake"
    assert data["model"] == "TestModel"
    assert data["model_year"] == "TestModelYear"
    assert data["body_class"] == "TestBodyClass"
    assert data["cached"]
    ext_test_client.assert_not_called()


def test_lookup_invalid_vin():
    """
    Tests that when the external client responds with status code 200, but an error in the content,
    the endpoint throws a 400 response with the specified error fields.
    """
    fail_response = {
        "ErrorCode": "1",
        "ErrorText": "1 - Check Digit (9th position) does not calculate properly",
        "AdditionalErrorText": "",
    }
    ext_test_client.get_vin.return_value = fail_response

    vin = "19XZE4F96KE027095"
    response = client.get("/lookup/{}".format(vin))
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["ErrorCode"] == fail_response["ErrorCode"]
    assert data["ErrorText"] == fail_response["ErrorText"]
    assert data["AdditionalErrorText"] == fail_response["AdditionalErrorText"]


def test_export():
    """
    Tests that the export endpoint returns streaming data
    """
    response = client.get("/export/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/octet-stream"


def test_remove_success():
    """
    Tests that when the remove endpoint is given a VIN that has previously been cached,
    it successfully deletes that record from the cache
    """
    vin = "1XPWD40X1ED215307"
    response = client.delete("/remove/{}".format(vin))
    assert response.status_code == 200
    assert response.json() == {"vin": vin, "deleted": True}


def test_remove_fail():
    """
    Tests that when the remove endpoint is given a new VIN, it throws a 404 error
    """
    vin = "4V4NC9EJXEN171694"
    response = client.delete("/remove/{}".format(vin))
    assert response.status_code == 404
