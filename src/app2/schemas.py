# src/app2/schemas.py

from pydantic import BaseModel


class OrderSchema(BaseModel):
    product_name: str
    quantity: int
