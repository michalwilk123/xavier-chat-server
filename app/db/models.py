from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True)
    public_id_key = Column(String(32), nullable=False)
    public_signed_pre_key = Column(String(32), nullable=False)
    signature = Column(String(32), nullable=False)
    one_time_keys = relationship("OneTimeKey", back_populates="owner")


class OneTimeKey(Base):
    __tablename__ = "one_time_keys"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(32), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="one_time_keys")
