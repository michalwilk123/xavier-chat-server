from typing import Tuple
from app.models import UserData, InviteModel
from tests.conftest import test_client
from fastapi import status
from .utils import generate_signature

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


def clear_and_create_alice_bob() -> Tuple[dict, dict]:
    a_sig = generate_signature(alice_user.login, alice_user.signature)
    b_sig = generate_signature(bob_user.login, bob_user.signature)
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)
    test_client.post("/users", json=alice_user.dict())
    test_client.post("/users", json=bob_user.dict())
    return a_sig, b_sig


def test_auth_integrity():
    data = {"invite": alice_to_bob_invite.dict()}
    a_sig = generate_signature(alice_user.login, alice_user.signature)
    b_sig = generate_signature(bob_user.login, bob_user.signature)
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)

    signature = generate_signature(alice_user.login, alice_user.signature, -1)
    response = test_client.post("/users/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_401_UNAUTHORIZED
    ), "Signature has timed out, and it should cause the authorization to fail"

    signature = generate_signature(
        alice_user.login, alice_user.signature, 1000, "fake_checksum"
    )
    response = test_client.post("/users/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "User does not exist. An exception should be thrown"

    test_client.post("/users", json=alice_user.dict())
    response = test_client.post("/users/invites", json=data | signature)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
        "The check sum of the signature is incorrent and cause the "
        "authorization to fail."
    )

    # valid signature
    signature = generate_signature(alice_user.login, alice_user.signature)
    response = test_client.post("/users/invites", json=data | signature)
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "second user does not exist and this should cause the error"

    # creating bob user
    test_client.post("/users", json=bob_user.dict())

    response = test_client.post("/users/invites", json=data | signature)

    assert (
        response.status_code == status.HTTP_200_OK
    ), "User sent valid data. Should not raise any exceptions."

    bob_signature = generate_signature(bob_user.login, bob_user.signature)

    test_client.delete("/users", json=signature)
    test_client.delete("/users", json=bob_signature)


def test_send_invite_normal():
    a_sig, b_sig = clear_and_create_alice_bob()
    data = {"invite": bob_to_alice_invite.dict()}

    # bob sends an invite to alice
    response = test_client.post("/users/invites", json=data | b_sig)
    assert (
        response.status_code == status.HTTP_200_OK
    ), "invite request should be successful"

    # cleaning up
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)


def test_otks_consumed():
    ...


def test_get_invites():
    ...
    # a_sig, b_sig = clear_and_create_alice_bob()

    # data = {"invite": bob_to_alice_invite.dict()}

    # # bob sends an invite to the alice
    # response = test_client.post("/users/invites", json=data | b_sig)
    # assert (
    #     response.status_code == status.HTTP_200_OK
    # ), "invite request should be successful"

    # # alice checks her inbox for incoming invites
    # response = test_client.post("/users/invites", json=a_sig)
    # assert (
    #     response.status_code == status.HTTP_200_OK
    # ), "invite retriecal should end up successful"

    # test_client.delete("/users", json=a_sig)
    # test_client.delete("/users", json=b_sig)


def test_recieve_no_invites():
    ...
