"""
Unit tests for crud operations on users.
Database connection is mocked.
"""
import pytest
from app.models.user import UserData, UserDataDTO
from fastapi import status
from tests.conftest import test_client
from .utils import generate_signature

alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    one_time_keys=[],
)

alice_user_w_otks = UserData(
    login="alice_w_otk",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C+otk",
    one_time_keys=["9be256eb80ffb678", "f67535c7fa6e1f08"],
)


def test_create():
    signature = generate_signature(alice_user.login, alice_user.signature)
    test_client.delete("/users", json=signature)

    resp = test_client.get("/users/alice")
    assert (
        resp.status_code == status.HTTP_404_NOT_FOUND
    ), "user should not be found"

    resp = test_client.post("/users", json=alice_user.dict())
    assert (
        resp.json() == "OK"
    ), f"request should be correct. Insted we got: {resp.json()}"

    resp = test_client.get("/users/alice")
    assert resp.status_code == status.HTTP_200_OK, "user should be found"

    resp = test_client.delete("/users", json=signature)
    assert (
        resp.json() == "OK"
    ), f"request should be correct. Insted we got: {resp.json()}"

    resp = test_client.get("/users/alice")
    assert (
        resp.status_code == status.HTTP_404_NOT_FOUND
    ), "user should not be found"


def test_create_w_otks():
    signature = generate_signature(
        alice_user_w_otks.login, alice_user_w_otks.signature
    )
    test_client.delete("/users", json=signature)

    resp = test_client.get("/users/alice_w_otk")
    assert (
        resp.status_code == status.HTTP_404_NOT_FOUND
    ), "user should not be found"

    resp = test_client.post("/users", json=alice_user_w_otks.dict())
    assert (
        resp.json() == "OK"
    ), f"request should be correct. Insted we got: {resp.json()}"

    resp = test_client.get("/users/alice_w_otk")
    assert resp.status_code == status.HTTP_200_OK, "user should be found"

    resp = test_client.delete("/users", json=signature)
    assert (
        resp.json() == "OK"
    ), f"request should be correct. Insted we got: {resp.json()}"

    resp = test_client.get("/users/alice_w_otk")
    assert (
        resp.status_code == status.HTTP_404_NOT_FOUND
    ), "user should not be found"


def test_read():
    signature = generate_signature(alice_user.login, alice_user.signature)
    test_client.delete("/users", json=signature)

    response = test_client.get("/users/alice")
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "User should not be found"

    alice_user_resp = UserDataDTO(
        login="alice",
        public_id_key="SW2en3QnUIBLjTprP7gS",
        public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
        number_of_otk=1,
    )

    response = test_client.post("/users", json=alice_user.dict())
    response = test_client.get("/users/alice")

    assert response.json() == alice_user_resp.dict()

    with pytest.raises(KeyError):
        response.json()["signature"]
        response.json()["one_time_keys"]

    test_client.delete("/users", json=signature)
