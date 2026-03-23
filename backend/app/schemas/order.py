from pydantic import BaseModel
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    total_price: float
    item_count: int
    status: str
    note: str | None
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    note: str | None = None
