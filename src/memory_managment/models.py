from sqlalchemy import Column, Integer
from database.base import Base
from sqlalchemy.orm import declarative_base


class Memory(Base):
    __tablename__ = "Memory"
    id = Column(Integer, primary_key=True)
    total = Column(Integer)
    free = Column(Integer)
    used = Column(Integer)
