from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from database.base import Base


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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role_id = Column(ForeignKey("Roles.id"), nullable=False)
