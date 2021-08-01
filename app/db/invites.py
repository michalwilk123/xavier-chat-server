from app.models import user
from app.models.invites import InviteModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import User, UserInvite
from app.db import crypto


def invite_from_orm_to_model(db: Session, invite: UserInvite) -> InviteModel:
    return InviteModel(
        my_login=invite.sender.login,
        contact_login=invite.reciever.login,
        additional_msg=invite.additional_msg,
        public_id_key=invite.public_id_key,
        public_ephemeral_key=invite.public_ephemeral_key,
        otk_index=invite.otk_index,
    )


def invite_from_model_to_orm(
    db: Session, invite: InviteModel
) -> Optional[UserInvite]:
    sender = db.query(User).filter(User.login == invite.sender_login).first()
    reciever = db.query(User).filter(User.login == invite.recv_login).first()
    if None in (sender, reciever):
        return None

    user_invite = UserInvite(
        additional_msg=invite.additional_msg,
        public_id_key=invite.public_id_key,
        public_ephemeral_key=invite.public_ephemeral_key,
        sender=sender,
        reciever=reciever,
    )

    if invite.otk_index is not None:
        user_invite.otk_index = invite.otk_index

    return user_invite


def get_invites(db: Session, login: str) -> List[InviteModel]:
    res = db.query(UserInvite).join(User).filter(User.login == login).first()

    if res is None:
        return []

    return [invite_from_orm_to_model(db, inv) for inv in res]


def add_invite(db: Session, invite: InviteModel) -> Optional[dict]:

    orm_invite = invite_from_model_to_orm(db, invite)

    if orm_invite is None:
        return None

    if invite.otk_index is None:
        res = crypto.get_free_otk(db, invite.recv_login)
        if res is None:
            return None
        idx, otk_val = res
        orm_invite.otk_index = idx
    else:
        otk_val = crypto.get_otk_from_idx(
            db, invite.recv_login, invite.otk_index
        )

    if otk_val is None:
        return None

    db.add(orm_invite)
    db.commit()
    db.refresh(orm_invite)

    return {"otk_index": orm_invite.otk_index, "otk_key": otk_val}
