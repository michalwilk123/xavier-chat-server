from app.models.invites import InviteModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import User, UserInvite


class InviteModelException(Exception):
    ...


def invite_from_orm_to_model(invite: UserInvite) -> InviteModel:
    return InviteModel(
        sender_login=invite.sender.login,
        recv_login=invite.reciever.login,
        public_id_key=invite.public_id_key,
        public_ephemeral_key=invite.public_ephemeral_key,
        otk_index=invite.otk_index,
        additional_msg=invite.additional_msg,
    )


def get_invites(db: Session, login: str) -> List[InviteModel]:
    res = (
        db.query(UserInvite)
        .join(User, UserInvite.reciever)
        .filter(User.login == login)
        .all()
    )

    return [invite_from_orm_to_model(inv) for inv in res]


def delete_invite(db: Session, sender_id: int, reciever_id: int) -> None:
    db.query(UserInvite).filter(
        (UserInvite.sender_id == sender_id) & (UserInvite.reciever_id == reciever_id)
    ).delete()


def add_invite(
    db: Session,
    invite: InviteModel,
    sender_id: int,
    reciever_id: int,
):
    if invite.otk_index is None:
        raise InviteModelException("The otk index must be assigned")

    orm_invite = UserInvite(
        additional_msg=invite.additional_msg,
        public_id_key=invite.public_id_key,
        public_ephemeral_key=invite.public_ephemeral_key,
        sender_id=sender_id,
        reciever_id=reciever_id,
        otk_index=invite.otk_index,
    )

    db.add(orm_invite)
    db.commit()
    db.refresh(orm_invite)


def invite_exists(db: Session, sender_id: int, reciever_id: int) -> bool:
    return (
        db.query(UserInvite)
        .filter(
            (UserInvite.sender_id == sender_id)
            & (UserInvite.reciever_id == reciever_id)
        )
        .first()
        is not None
    )


def get_invite_by_ephemeral_key(
    db: Session, login: str, ephem_key: str
) -> Optional[tuple[InviteModel, int, int]]:
    res = (
        db.query(UserInvite)
        .filter(UserInvite.public_ephemeral_key == ephem_key)
        .join(User, UserInvite.reciever)
        .filter(User.login == login)
        .all()
    )

    if not res:
        return None

    if len(res) > 1:
        raise RuntimeError(
            "WARNING! Got 2 identical invites to the same"
            " user. This situation should not ever happen"
        )

    res = res[0]

    return invite_from_orm_to_model(res), res.sender_id, res.reciever_id
