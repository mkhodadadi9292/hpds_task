# src/app1/app.py

from fastapi import FastAPI, Depends, APIRouter
from src.app1.models import User, Base1
from src.app1.schemas import UserSchema
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])


def get_db():
    db = Session(Base1)
    try:
        yield db
    finally:
        db.close()


@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.post("/users")
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    return user
