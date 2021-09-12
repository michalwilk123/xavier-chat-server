from .utils import generate_signature
from app.models import UserData, InviteModel
from app.db.models import UserInvite, User
from tests.conftest import test_client, TestingSessionLocal
from fastapi import status
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

charlie_user = UserData(
    login="charlie",
    public_id_key="3ljLaMW1+hfFwxNK+pof+g==",
    public_signed_pre_key="7i4jroRKeCvPts5Z/Gj9SQ=",
    signature="HqiYj8DtOgJ3Imwj0Txa2A=",
    one_time_keys=["Ot2nBLuTxuQY6yGozB5HJw==", "YFEBSQ/EQ2LC1kDMXpfZtQ=="],
)

dave_user = UserData(
    login="dave",
    public_id_key="gDzbgQxsHwhqcCM+1IRhmQ==",
    public_signed_pre_key="RX2EBV/ODKx4bOMtgZu3FQ==",
    signature="f1CljDTKh2oEhRC9wrO1NQ==",
    one_time_keys=["SMUniZwM2DE29bEsi6xN9A==", "90FO1M5zb48hnpU/iZsLhg=="],
)

alice_to_charlie_invite = InviteModel(
    sender_login="alice",
    signature="uZc4bH5uz1x7MfA7qx4C",
    recv_login="charlie",
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

charlie_to_bob_invite = InviteModel(
    sender_login="charlie",
    signature="HqiYj8DtOgJ3Imwj0Txa2A",
    recv_login="bob",
    public_id_key="dZOGYYQAoPfM6QWh/Ohirg==",
    public_ephemeral_key="8CHP0RoGEn35isxdACewYg==",
    additional_msg="Hello this is charlie",
)

dave_to_charlie_invite = InviteModel(
    sender_login="dave",
    signature="f1CljDTKh2oEhRC9wrO1NQ==",
    recv_login="charlie",
    public_id_key="3ljLaMW1+hfFwxNK+pof+g==",
    public_ephemeral_key="oooP0RoGEn35isxdACewYg==",
    additional_msg="Hello this is dave",
)

# user signatures
a_sig = generate_signature(alice_user.login, alice_user.signature)
b_sig = generate_signature(bob_user.login, bob_user.signature)
c_sig = generate_signature(charlie_user.login, charlie_user.signature)
d_sig = generate_signature(dave_user.login, dave_user.signature)


@pytest.fixture
def create_users():
    test_client.post("/users", json=alice_user.dict())
    test_client.post("/users", json=bob_user.dict())
    test_client.post("/users", json=charlie_user.dict())
    test_client.post("/users", json=dave_user.dict())

    yield 

    test_client.delete("/users", json=a_sig)
    test_client.delete("/users", json=b_sig)
    test_client.delete("/users", json=c_sig)
    test_client.delete("/users", json=d_sig)


@pytest.fixture
def send_invites(create_users):
    data0 = {"invite": bob_to_alice_invite.dict()}
    data1 = {"invite": alice_to_charlie_invite.dict()}
    data2 = {"invite": charlie_to_bob_invite.dict()}

    # bob sends an invite to the alice
    test_client.post("/invites", json=data0 | b_sig)
    test_client.post("/invites", json=data1 | a_sig)
    test_client.post("/invites", json=data2 | c_sig)

    yield
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


@pytest.fixture
def resolve_invites(send_invites):
    # fetching invites
    # charlie did not answer the invite
    inv0 = test_client.get("/invites", json=a_sig).json()
    inv1 = test_client.get("/invites", json=b_sig).json()
    inv2 = test_client.get("/invites", json=c_sig).json()

    ephem_key0 = inv0[0]["public_ephemeral_key"]
    ephem_key1 = inv1[0]["public_ephemeral_key"]
    ephem_key2 = inv2[0]["public_ephemeral_key"]

    test_client.post(f"/invites/answer/{ephem_key0}/accept", json=a_sig)
    test_client.post(f"/invites/answer/{ephem_key1}/accept", json=b_sig)
    test_client.post(f"/invites/answer/{ephem_key2}/reject", json=c_sig)

def test_fixtures(resolve_invites):
    ...

def test_start_with_no_contacts(create_users):
    res = test_client.get("/invites", json=a_sig)
    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 0, res.json()

    res = test_client.get("/contacts", json=a_sig)
    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 0, res.json()


def test_get_contact_list(resolve_invites):
    res = test_client.get("/contacts", json=a_sig)

    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 1, res.json()


def test_get_empty_contact_list(resolve_invites):
    res = test_client.get("/contacts", json=d_sig)

    assert res.status_code == status.HTTP_200_OK, res.json()
    assert len(res.json()) == 0, res.json()

def test_contact_recieved_from_two_parties(send_invites):
    data1 = {"invite": dave_to_charlie_invite.dict()}
    test_client.post("/invites", json=data1 | d_sig)

    inv0, inv1 = test_client.get("/invites", json=c_sig).json()

    ephem_key1 = inv0["public_ephemeral_key"]
    ephem_key2 = inv1["public_ephemeral_key"]
    test_client.post(f"/invites/answer/{ephem_key1}/accept", json=c_sig)
    test_client.post(f"/invites/answer/{ephem_key2}/accept", json=c_sig)

    res_dave = test_client.get("/contacts", json=d_sig)
    res_charlie = test_client.get("/contacts", json=c_sig)

    assert res_dave.status_code == status.HTTP_200_OK
    assert res_charlie.status_code == status.HTTP_200_OK
    assert len(res_dave.json()) == 1, res_dave.json()
    assert len(res_charlie.json()) == 2, res_charlie.json()

