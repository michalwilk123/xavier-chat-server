from app.db.models import User, UserInvite
from typing import Tuple
from app.models import UserData, InviteModel
from tests.conftest import TestingSessionLocal, test_client
from fastapi import status
from .utils import generate_signature
import pytest

alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    one_time_keys=["3xAhdgOYu4UeuXjdEfsS", "5bf6ed035e71295f"],
)

bob_user = UserData(
    login="bob",
    public_id_key="72f3e414c697c9653a57",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="72f3e414c697c9653a57",
    one_time_keys=["543n5jk3gOYu4UeuXjdEfsS", "3a9c7d1d51acf1ee"],
)

alice_to_bob_invite = InviteModel(
    sender_login="alice",
    signature="uZc4bH5uz1x7MfA7qx4C",
    recv_login="bob",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_ephemeral_key="HycupqtSDpE6z0ohgdrF",
    additional_msg="Hello this is alice",
    otk_index=1,
)

bob_to_alice_invite = InviteModel(
    sender_login="bob",
    signature="72f3e414c697c9653a57",
    recv_login="alice",
    public_id_key="72f3e414c697c9653a57",
    public_ephemeral_key="681b3b20ef410eb2ed68",
    additional_msg="Hello this is bob",
)


@pytest.fixture
def clear_and_create_alice_bob() -> Tuple:
    a_sig = generate_signature(alice_user.login, alice_user.signature)
    b_sig = generate_signature(bob_user.login, bob_user.signature)
    test_client.post("/users", json=alice_user.dict())
    test_client.post("/users", json=bob_user.dict())

    yield a_sig, b_sig
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)


@pytest.fixture
def create_invite(clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob

    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to the alice
    test_client.post("/invites", json=data | b_sig)

    yield a_sig, b_sig, bob_to_alice_invite.dict()
    db = TestingSessionLocal()

    invites_to_delete = (
        db.query(UserInvite)
        .join(User, UserInvite.sender)
        .filter(User.signature == b_sig["login"])
        .all()
    )

    for inv in invites_to_delete:
        inv.delete()

    db.commit()


def test_auth_integrity():
    data = {"invite": alice_to_bob_invite.dict()}
    a_sig = generate_signature(alice_user.login, alice_user.signature)
    b_sig = generate_signature(bob_user.login, bob_user.signature)
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)

    signature = generate_signature(alice_user.login, alice_user.signature, -1)
    response = test_client.post("/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_401_UNAUTHORIZED
    ), "Signature has timed out, and it should cause the authorization to fail"

    signature = generate_signature(
        alice_user.login, alice_user.signature, 1000, "fake_checksum"
    )
    response = test_client.post("/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "User does not exist. An exception should be thrown"

    test_client.post("/users", json=alice_user.dict())
    response = test_client.post("/invites", json=data | signature)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
        "The check sum of the signature is incorrent and cause the "
        "authorization to fail."
    )

    # valid signature
    signature = generate_signature(alice_user.login, alice_user.signature)
    response = test_client.post("/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "second user does not exist and this should cause the error"

    # creating bob user
    test_client.post("/users", json=bob_user.dict())

    response = test_client.post("/invites", json=data | signature)

    assert (
        response.status_code == status.HTTP_200_OK
    ), "User sent valid data. Should not raise any exceptions."

    bob_signature = generate_signature(bob_user.login, bob_user.signature)

    test_client.delete("/users", json=signature)
    test_client.delete("/users", json=bob_signature)


def test_send_invite_normal(clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob

    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to alice
    response = test_client.post("/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "invite request should be successful"


def test_get_invites(clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob

    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to the alice
    response = test_client.post("/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "invite request should be successful"

    # alice checks her inbox for incoming invites
    response = test_client.get("/invites", json=a_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "invite retrieval should end up successful"
    assert len(response.json()) == 1, "expecting 1 new invite from the bob"


def test_otks_consumed(mocker, clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob
    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to alice
    response = test_client.post("/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "first invite request should be successful"

    mocker.patch("app.db.invites.invite_exists", return_value=False)

    # bob sends an invite to alice second time
    response = test_client.post("/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "there should be enough keys for second request"

    # bob sends an invite to alice third time
    # he should run out of the available keys
    response = test_client.post("/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "Alice should run out of keys"


def test_recieve_no_invites(clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob

    # alice checks her inbox for incoming invites
    response = test_client.get("/invites", json=a_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "invite retrieval should end up successful"
    assert response.json() == [], "expecting 0 new invites from the users"


def test_create_invite_duplicate(clear_and_create_alice_bob):
    a_sig, b_sig = clear_and_create_alice_bob

    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to the alice
    response = test_client.post("/invites", json=data | b_sig)
    assert response.status_code == status.HTTP_200_OK, response.json()

    # bob sends second, redundant invite to alice
    response = test_client.post("/invites", json=data | b_sig)
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()


def test_invite_and_accept(create_invite):
    a_sig, _, invite = create_invite

    res = test_client.get("/contacts", json=a_sig)

    response = test_client.post(
        f"/invites/answer/{invite['public_ephemeral_key']}/accept",
        json=a_sig
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    # alice should have 1 new contact
    res = test_client.get("/contacts", json=a_sig)
    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 1, res.json()


def test_invite_and_reject(create_invite):
    a_sig, b_sig, invite = create_invite

    response = test_client.post(
        f"/invites/answer/{invite['public_ephemeral_key']}/reject",
        json=a_sig
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    res = test_client.get("/contacts", json=a_sig)
    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 0, res.json()


def test_invite_and_bad_decision(create_invite):
    a_sig, _, invite = create_invite

    response = test_client.post(
        f"/invites/answer/{invite['public_ephemeral_key']}/ehhe",
        json=a_sig
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.json()
