from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import UserContact


def send_chat_message_to_absent_user(db: Session, login: str, message: str):
    raise NotImplementedError("Offline messages not supported")


def get_pending_messages(db: Session, login: str) -> List[dict]:
    raise NotImplementedError("Offline messages not supported")


def get_conversation_address(
    db: Session, login: str, participant: str
) -> Optional[str]:
    raise NotImplementedError


def check_contact_exists(db: Session, init_id: int, particip_id: int) -> bool:
    return bool(
        db.query(UserContact)
        .filter(
            (
                UserContact.initializer_id
                == init_id & UserContact.participant_id
                == particip_id
            )
            | (
                UserContact.initializer_id
                == particip_id & UserContact.participant_id
                == init_id
            )
        )
        .all()
    )

