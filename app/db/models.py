from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True)
    public_id_key = Column(String(32), nullable=False)
    public_signed_pre_key = Column(String(32), nullable=False)
    signature = Column(String(32), nullable=False)

    one_time_keys = relationship(
        "OneTimeKey", backref="owner", passive_deletes=True
    )
    sent_invites = relationship(
        "UserInvite",
        back_populates="sender",
        foreign_keys="UserInvite.sender_id",
        passive_deletes=True,
    )
    recieved_invites = relationship(
        "UserInvite",
        back_populates="reciever",
        foreign_keys="UserInvite.reciever_id",
        passive_deletes=True,
    )

    contacts_initialized = relationship(
        "UserContact",
        back_populates="initializer",
        foreign_keys="UserContact.initializer_id",
        passive_deletes=True,
    )

    contacts_recieved = relationship(
        "UserContact",
        back_populates="recipient",
        foreign_keys="UserContact.recipient_id ",
        passive_deletes=True,
    )


class OneTimeKey(Base):
    __tablename__ = "one_time_keys"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(32), nullable=False)
    index = Column(Integer, default=0, nullable=False, autoincrement=True)
    used = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))


class UserInvite(Base):
    __tablename__ = "user_invites"

    id = Column(Integer, primary_key=True, index=True)
    additional_msg = Column(String(128), nullable=False)
    public_id_key = Column(String(256), nullable=False)
    public_ephemeral_key = Column(String(256), nullable=False)
    otk_index = Column(Integer, nullable=True)

    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reciever_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    sender = relationship(
        "User", back_populates="sent_invites", foreign_keys=[sender_id]
    )
    reciever = relationship(
        "User", back_populates="recieved_invites", foreign_keys=[reciever_id]
    )


class UserContact(Base):
    __tablename__ = "user_contacts"

    id = Column(Integer, primary_key=True, index=True)

    initializer_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    recipient_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    initializer = relationship(
        "User",
        back_populates="contacts_initialized",
        foreign_keys=[initializer_id],
    )
    recipient = relationship(
        "User", back_populates="contacts_recieved", foreign_keys=[recipient_id]
    )

    @hybrid_property
    def conversation_address(self):
        return "{} {}".format(self.initializer.login, self.recipient.login)
