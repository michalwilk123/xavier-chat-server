import pytest
from starlette import status

from app.models.crypto import OtkCollection, OtkSimple
from app.models.invites import InviteModel
from app.models.user import UserData
from tests.conftest import test_client

from .utils import generate_signature

alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    one_time_keys=[],
)

bob_user = UserData(
    login="bob",
    public_id_key="72f3e414c697c9653a57",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="72f3e414c697c9653a57",
    one_time_keys=[],
)

bob_to_alice_invite = InviteModel(
    sender_login="bob",
    signature="72f3e414c697c9653a57",
    recv_login="alice",
    public_id_key="72f3e414c697c9653a57",
    public_ephemeral_key="681b3b20ef410eb2ed68",
    additional_msg="Hello this is bob",
)

alice_otk_coll = OtkCollection(
    collection=[
        OtkSimple(index=2, value="2b43e7a06321ed270d8e"),
        OtkSimple(index=3, value="2f465565466eb9ccc322"),
        OtkSimple(index=4, value="111ebd098c3e938afe7b"),
    ]
)

GENERATED_KEYS = 10


@pytest.fixture
def create_users():
    a_sig = generate_signature(alice_user.login, alice_user.signature)
    b_sig = generate_signature(bob_user.login, bob_user.signature)
    test_client.post("/users", json=alice_user.dict())
    test_client.post("/users", json=bob_user.dict())
    yield a_sig, b_sig
    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)


@pytest.fixture
def generate_and_use_keys(mocker, create_users):
    res = test_client.post(
        "/crypto/generate-otks",
        params={"limit": GENERATED_KEYS},
        json=create_users[0],
    )
    assert (
        res.status_code == status.HTTP_200_OK
    ), "could not create keys for test case fixture"

    data = {"invite": bob_to_alice_invite.dict()}

    mocker.patch("app.db.invites.invite_exists", return_value=False)

    for _ in range(GENERATED_KEYS // 2):
        test_client.post("/invites", json=data | create_users[1])

    return create_users


def test_populate_used_keys(generate_and_use_keys):
    a_sig, b_sig = generate_and_use_keys
    res = test_client.get(
        "/crypto/one-time-keys", params={"used": True}, json=a_sig
    )
    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == GENERATED_KEYS // 2

    res = test_client.get(
        "/crypto/one-time-keys", params={"used": False}, json=a_sig
    )
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == GENERATED_KEYS - GENERATED_KEYS // 2

    res = test_client.post("/crypto/generate-otks", json=a_sig)
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == "OK"

    res = test_client.get(
        "/crypto/one-time-keys", params={"used": False}, json=a_sig
    )
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == GENERATED_KEYS


def test_assign_new_keys(create_users):
    a_sig, b_sig = create_users

    res = test_client.get("/crypto/one-time-keys", json=a_sig)
    assert len(res.json()) == 0, res.json()

    data = {"otk_collection": alice_otk_coll.dict()} | a_sig
    res = test_client.post("/crypto/one-time-keys", json=data)
    assert res.json() == "OK", res.json()

    res = test_client.get("/crypto/one-time-keys", json=a_sig)
    assert len(res.json()) == len(alice_otk_coll.collection), res.json()

    res.json().sort(key=lambda x: x[0])

    for ori, res_key in zip(alice_otk_coll.collection, res.json()):
        assert (
            ori.index == res_key[0]
        ), f"bad index: value: {res_key[0]}, original: {ori.index}"
        assert (
            ori.value == res_key[1]
        ), f"bad index: value: {res_key[1]}, original: {ori.value}"


def test_override_keys(create_users):
    a_sig, b_sig = create_users
    NUM_OF_KEYS = 4
    test_client.post(
        "/crypto/generate-otks", params={"limit": NUM_OF_KEYS}, json=a_sig
    )

    data = {"otk_collection": alice_otk_coll.dict()} | a_sig
    res = test_client.post("/crypto/one-time-keys", json=data)
    assert res.json() == "OK", res.json()

    res = test_client.get("/crypto/one-time-keys", json=a_sig)
    # keys on positions 2,3 should be overrided
    assert len(res.json()) == 5, f"result: {len(res.json())} target: 5"


def test_generate_keys(create_users):
    a_sig, b_sig = create_users
    NUM_OF_KEYS = 10
    res = test_client.post(
        "/crypto/generate-otks", params={"limit": NUM_OF_KEYS}, json=a_sig
    )
    assert res.status_code == status.HTTP_200_OK, (
        "Could not create keys for the user. "
        f"Response message: {res.json()}"
    )
    res = test_client.get("/crypto/one-time-keys", json=a_sig)

    assert res.status_code == status.HTTP_200_OK, (
        "Could not retrieve keys for the user. "
        f"Response message: {res.json()}"
    )

    assert len(res.json()) == NUM_OF_KEYS, (
        "number of created keys does not match the initial "
        f"requirements. We got {len(res.json())} "
        f"keys instead of {NUM_OF_KEYS}"
    )
