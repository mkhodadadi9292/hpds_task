# src/app1/models.py

from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base


Base1 = declarative_base()


class User(Base1):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
