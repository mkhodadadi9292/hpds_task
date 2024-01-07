from database.base import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .constants import UserStatus


class Roles(Base):
    __tablename__ = "Roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)


class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(255), unique=True, nullable=False)
    username = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), )
    role_id = Column(ForeignKey("Roles.id"), nullable=False)
