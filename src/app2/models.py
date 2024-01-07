# src/app2/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, MetaData
from src.app1.models import User
from sqlalchemy.orm import declarative_base

Base2 = declarative_base()


class Order(Base2):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    product_name = Column(String(255))
    quantity = Column(Integer)
