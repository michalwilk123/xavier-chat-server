from typing import Optional
from app.models.user import OrmUserData, UserData
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
    # funneling type to its base orm version
    item = User(**OrmUserData(**user.dict()).dict())

    # trying to set collection of initial keys
    db.add(item)
    db.commit()

    if set_one_time_keys(db, user.login, {i: v for i, v in enumerate(keys)}) is False:
        return False
    return True


def delete_user(db: Session, login: str) -> bool:
    if get_user_data(db, login) is None:
        return False

    if db.query is None:
        return False

    if db.query(User) is None:
        return False

    db.query(User).filter(User.login == login).delete()
    db.commit()
    return True


def get_user_data(db: Session, login: str, get_id: bool = False) -> Optional[UserData]:
    result = db.query(User).filter(User.login == login).first()

    if result is None:
        return None

    return UserData(
        login=result.login,
        public_id_key=result.public_id_key,
        public_signed_pre_key=result.public_signed_pre_key,
        signature=result.signature,
        one_time_keys=[k.value for k in result.one_time_keys],
        user_id=result.id if get_id else None,
    )
