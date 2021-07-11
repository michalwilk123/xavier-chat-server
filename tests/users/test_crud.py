"""
Unit tests for crud operations on users.
Database connection is mocked.
"""
import pytest
from app.models.user_model import UserData, UserDataDTO
from fastapi import status
from requests.auth import HTTPBasicAuth
from tests.conftest import client

alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    one_time_keys=["3xAhdgOYu4UeuXjdEfsS"],
)


def test_create():
    bad_req = client.post("/user")
    assert (
        bad_req.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), "Request containing no data should fail"

    ok_response = client.post("/user", json=alice_user.dict())
    assert (
        ok_response.status_code == status.HTTP_200_OK
    ), "Request should be successful"
    assert ok_response.json() == "OK"

    auth = HTTPBasicAuth(
        username=alice_user.login, password=alice_user.signature
    )

    del_response = client.delete("/user", auth=auth)
    assert (
        del_response.status_code == status.HTTP_200_OK
    ), "delete should run successfully"

    client.post("/user", json=alice_user.dict())
    reapeated_resp = client.post("/user", json=alice_user.dict())
    assert (
        reapeated_resp.status_code == status.HTTP_406_NOT_ACCEPTABLE
    ), "Good response for repeating request!"
    client.delete("/user", auth=auth)


def test_read():
    client.post("/user", json=alice_user.dict())

    response = client.get("/user", params={"login": "alice"})
    assert (
        response.status_code == status.HTTP_200_OK
    ), "Request should be correct"

    alice_user_resp = UserDataDTO(
        login="alice",
        public_id_key="SW2en3QnUIBLjTprP7gS",
        public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
        number_of_otk=1,
    )
    assert response.json() == alice_user_resp.dict()

    with pytest.raises(KeyError):
        response.json()["signature"]
        response.json()["one_time_keys"]

    auth = HTTPBasicAuth(
        username=alice_user.login, password=alice_user.signature
    )
    client.delete("/user", auth=auth)

    response = client.get("/user", params={"login": "non existing alice"})
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "Data should not be found"


def test_delete():
    client.post("/user", json=alice_user.dict())
    auth = HTTPBasicAuth(
        username=alice_user.login, password=alice_user.signature
    )
    response = client.delete("/user", auth=auth)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "OK"

    response = client.delete("/user", auth=auth)
    assert response.status_code == status.HTTP_404_NOT_FOUND
