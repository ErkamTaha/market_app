from pydantic import BaseModel
from datetime import datetime


class PurchaseItemResponse(BaseModel):
    id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}


class PurchaseResponse(BaseModel):
    id: int
    total_price: float
    item_count: int
    receipt_code: str
    payment_method: str
    store_name: str
    status: str
    points_earned: int
    created_at: datetime
    items: list[PurchaseItemResponse]

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    payment_method: str = "card"  # card, cash, wallet
