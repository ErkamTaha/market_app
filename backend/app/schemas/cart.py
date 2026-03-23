from pydantic import BaseModel
from app.schemas.product import ProductResponse


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    model_config = {"from_attributes": True}
