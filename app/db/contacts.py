from app.db.models import UserContact, User
from sqlalchemy.orm import Session
from app.models.messages import SingleContact
from app.db.user import get_user_data


def create_new_contact(db: Session, sender_id: int, reciever_id: int) -> None:
    orm_contact = UserContact(initializer_id=sender_id, recipient_id=reciever_id)
    db.add(orm_contact)
    db.commit()


def contact_exists(db: Session, sender_id: int, reciever_id: int) -> bool:
    return (
        db.query(UserContact)
        .filter(
            (UserContact.initializer_id == sender_id)
            & (UserContact.recipient_id == reciever_id)
        )
        .first()
        is not None
    )

def get_contacts(db: Session, login: str) -> list[SingleContact]:
    contact_list = []
    user_id = get_user_data(db, login, get_id=True)

    if user_id is None:
        return contact_list

    user_id = user_id.user_id

    contacts_init = db.query(UserContact).join(User, UserContact.initializer_id == user_id).all()
    contacts_recv = db.query(UserContact).join(User, UserContact.recipient_id == user_id).all()

    for cont in contacts_init:
        contact_list.append(
            SingleContact(
                contact_name=cont.initializer.login,
                conversation_channel=cont.conversation_address,
            )
        )

    for cont in contacts_recv:
        contact_list.append(
            SingleContact(
                contact_name=cont.recipient.login,
                conversation_channel=cont.conversation_address,
            )
        )

    return contact_list