from app.models import UserData, InviteModel
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
    otk_index=1,
)


def test_send_invite(client):
    ...


def test_send_invite_bad_user():
    ...


def test_recieve_invite():
    ...


def test_recieve_no_invites():
    ...
