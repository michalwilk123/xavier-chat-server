from app.db.models import OneTimeKey, User
from typing import Dict, Tuple, Optional, List
from sqlalchemy.orm import Session


# NOTE: could make some logs
class CryptoControllerException(Exception):
    ...


def get_user_otks(
    db: Session, login: str, /, key_used: Optional[bool]
) -> Optional[List[Tuple[int, str]]]:
    res = db.query(OneTimeKey).join(User).filter(User.login == login)

    if key_used is not None:
        res = res.filter(OneTimeKey.used == key_used)

    res = res.all()

    if res is None:
        return None

    return [(key.index, key.value) for key in res]


def get_free_otk(db: Session, login: str) -> Optional[Tuple[int, str]]:
    res = (
        db.query(OneTimeKey)
        .join(User)
        .filter(User.login == login)
        .filter(OneTimeKey.used == False)
        .first()
    )

    if res is None:
        return None

    otk_val = get_otk_from_idx(db, login, res.index)

    if otk_val is None:
        return None

    return res.index, otk_val


def delete_used_otk(db: Session, login: str):

    res = (
        db.query(OneTimeKey)
        .join(User)
        .filter(User.login == login)
        .filter(OneTimeKey.used == True)
        .all()
    )

    # this is so inefficient
    # i am so sorry...
    for entry in res:
        db.delete(entry)

    db.commit()


def get_otk_from_idx(db: Session, login: str, idx: int) -> Optional[str]:
    res = (
        db.query(OneTimeKey)
        .join(User)
        .filter(User.login == login)
        .filter(OneTimeKey.index == idx)
        .first()
    )

    if res is None:
        return None

    if res.used is True:
        return None

    otk_value = res.value
    res.used = True
    db.commit()
    return otk_value


def set_one_time_keys(db: Session, login: str, otk_collection: Dict[int, str]) -> bool:
    user = db.query(User).filter(User.login == login).first()

    if user is None:
        return False

    otk_list = [
        OneTimeKey(value=otk_collection[idx], index=idx) for idx in otk_collection
    ]

    for otk in otk_list:
        user.one_time_keys.append(otk)

    db.commit()
    return True


def set_otk_and_replace(
    db: Session, login: str, otk_collection: Dict[int, str]
) -> bool:
    res = (
        db.query(OneTimeKey)
        .join(User)
        .filter(User.login == login)
        .filter(OneTimeKey.index.in_(otk_collection.keys()))
        .all()
    )

    for entry in res:
        db.delete(entry)

    return set_one_time_keys(db, login, otk_collection)
