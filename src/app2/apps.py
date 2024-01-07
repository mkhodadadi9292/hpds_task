# src/app2/app.py

from fastapi import FastAPI, Depends, APIRouter
from src.app2.models import Order, Base2
from src.app2.schemas import OrderSchema
from sqlalchemy.orm import Session

router = APIRouter(tags=["Orders"])


def get_db():
    db = Session(Base2)
    try:
        yield db
    finally:
        db.close()


@router.get("/orders", description="Returns a list of orders", )
async def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders


@router.post("/orders")
async def create_order(order: OrderSchema, db: Session = Depends(get_db)):
    new_order = Order(user_id=1, product_name=order.product_name, quantity=order.quantity)
    db.add(new_order)
    db.commit()
    return order
