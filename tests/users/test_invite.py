from app.main import app
from app.models import UserData, InviteModel
from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth
from fastapi import status


alice_user = UserData(
    login="alice",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C",
    number_of_otk=1,
    one_time_keys=["3xAhdgOYu4UeuXjdEfsS"],
)

alice_to_bob_invite = InviteModel(
    my_login="alice",
    signature="uZc4bH5uz1x7MfA7qx4C",
    contact_login="bob",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_ephemeral_key="HycupqtSDpE6z0ohgdrF",
    otk_index=1
)


def test_send_invite(mocker):
    mocker.patch("app.db.user.delete_user", return_value=True)
    mocker.patch("app.db.user.get_user_data", return_value=True)
    client = TestClient(app)
    auth = HTTPBasicAuth(username=alice_user.login, password=alice_user.signature)
    response = client.delete("/user", auth=auth)
    res = client.post("/user/contacts", json=alice_to_bob_invite.dict())
    print(f"{res.json()=}")


    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "OK"

    mocker.patch("app.db.user.delete_user", return_value=False)

    response = client.delete("/user", auth=auth)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_send_invite_bad_user(mocker):
    return
    def mocked_user_info(login:str):
        return login in ["alice", "bob"]

    # mocker.patch("app.db.user.get_user_data", side_effect=mocked_user_info)
    mocker.patch("app.routers.user.get_user_info", side_effect=mocked_user_info)
    mocker.patch("app.routers.contacts.send_invite", return_value="OK")

    # mocker.patch("app.db.contacts.store_invite", return_value=False)


def test_recieve_invite(mocker):
    ...

def test_recieve_no_invites(mocker):
    ...
