from app.db import models
from app.models.user import UserData
from tests.conftest import TestingSessionLocal

session = TestingSessionLocal()

alice_user_w_otks = UserData(
    login="alice_w_otk",
    public_id_key="SW2en3QnUIBLjTprP7gS",
    public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
    signature="uZc4bH5uz1x7MfA7qx4C+otk",
    one_time_keys=["9be256eb80ffb678", "f67535c7fa6e1f08"],
)


def test_user_create_w_otks():
    # cleaning up old data
    session.query(models.User).delete()
    session.query(models.OneTimeKey).delete()
    session.commit()

    otks = [
        models.OneTimeKey(value=val, index=idx)
        for val, idx in enumerate(alice_user_w_otks.one_time_keys)
    ]
    db_alice = models.User(
        login="alice_w_otk",
        public_id_key="SW2en3QnUIBLjTprP7gS",
        public_signed_pre_key="e0q24TQgqKQjoaA6aDfc",
        signature="uZc4bH5uz1x7MfA7qx4C+otk",
        one_time_keys=otks,
    )
    session.add(db_alice)
    session.commit()

    session.query(models.User).filter(
        models.User.login == alice_user_w_otks.login
    ).delete()

    res = session.query(models.OneTimeKey).all()

    assert res == [], "the relationship cascade value did not work!"
