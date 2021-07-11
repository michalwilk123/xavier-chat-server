from typing import Optional
from app.models.user_model import UserData
from sqlalchemy.orm import Session
from app.db.models import User
from .crypto import set_one_time_keys


class UserDataException(Exception):
    ...


def add_user(db: Session, user: UserData) -> bool:
    res = get_user_data(db, user.login)

    if res is not None:
        return False

    keys = user.one_time_keys
    user_dict = user.dict()
    del user_dict["one_time_keys"]
    item = User(**user_dict)

    if set_one_time_keys(db, user.login, keys) is False:
        return False

    db.add(item)
    db.commit()
    db.refresh(item)
    res = get_user_data(db, user.login)
    return True


def delete_user(db: Session, login: str) -> bool:
    if get_user_data(db, login) is None:
        return False

    db.query(User).filter(User.login == login).delete()
    db.commit()
    return True


def get_user_data(db: Session, login: str) -> Optional[UserData]:
    result = db.query(User).filter(User.login == login).first()

    if result is None:
        return None

    return UserData.from_orm(result)


def user_auth(db: Session, login: str, signature: str) -> bool:
    # res = db.users.find_one({"login": login, "signature": signature})
    # return res is not None
    return False
