"""
Unit tests for crud operations on users.
Database connection is mocked.
"""
import pytest
from httpx import AsyncClient
from app.main import app
from app.config import get_db_settings
from app.models.user_model import UserData, UserDataDTO
from fastapi import status
from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth

alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    number_of_otk=1,
    one_time_keys=["3xAhdgOYu4UeuXjdEfsS"],
)


@pytest.mark.asyncio
async def test_create(mocker):
    mocker.patch("app.db.user.add_user", return_value=True)

    async with AsyncClient(app=app, base_url=get_db_settings().base_url) as ac:
        bad_req = await ac.post("/user")
        assert bad_req.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, "User request error!"

        ok_response = await ac.post("/user", json=alice_user.dict())
        assert ok_response.status_code == status.HTTP_200_OK, "Request should be successful"
        assert ok_response.json() == "OK"

        mocker.patch("app.db.user.add_user", return_value=False)

        reapeated_resp = await ac.post("/user", json=alice_user.dict())
        assert (
            reapeated_resp.status_code == status.HTTP_406_NOT_ACCEPTABLE
        ), "Good response for bad request!"


@pytest.mark.asyncio
async def test_read(mocker):
    mocker.patch("app.db.user.get_user_data", return_value=alice_user)

    async with AsyncClient(app=app, base_url=get_db_settings().base_url) as ac:
        response = await ac.get("/user", params={"login": "alice"})

        assert response.status_code == status.HTTP_200_OK, "Request should be correct"

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

        mocker.patch("app.db.user.get_user_data", return_value=None)
        response = await ac.get("/user", params={"login": "non existing alice"})
        assert response.status_code == status.HTTP_404_NOT_FOUND, "Data should not be found"


def test_delete(mocker):
    mocker.patch("app.db.user.delete_user", return_value=True)
    client = TestClient(app)
    auth = HTTPBasicAuth(username=alice_user.login, password=alice_user.signature)
    response = client.delete("/user", auth=auth)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "OK"

    mocker.patch("app.db.user.delete_user", return_value=False)

    response = client.delete("/user", auth=auth)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



