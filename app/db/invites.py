from app.models.invites import InviteModel
from typing import List
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

    # sender = db.query(User).filter(User.login == invite.sender_login).first()
    # reciever = db.query(User).filter(User.login == invite.recv_login).first()
    # if None in (sender, reciever):
    #     return None

    # if invite.otk_index is not None:
    #     user_invite.otk_index = invite.otk_index


def get_invites(db: Session, login: str) -> List[InviteModel]:
    res = (
        db.query(UserInvite)
        .join(User, UserInvite.reciever)
        .filter(User.login == login)
        .all()
    )

    return [invite_from_orm_to_model(inv) for inv in res]


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

    # if invite.otk_index is None:
    #     res = crypto.get_free_otk(db, invite.recv_login)
    #     if res is None:
    #         return None
    #     idx, otk_val = res
    #     orm_invite.otk_index = idx
    # else:
    #     otk_val = crypto.get_otk_from_idx(
    #         db, invite.recv_login, invite.otk_index
    #     )

    # if otk_val is None:
    #     return None

    db.add(orm_invite)
    db.commit()
    db.refresh(orm_invite)
