from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    icon: str | None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    price: float
    discount_price: float | None
    unit: str
    barcode: str | None
    stock: int
    is_in_stock: bool
    image_url: str | None
    brand: str | None

    model_config = {"from_attributes": True}


class ProductWithCategoryResponse(ProductResponse):
    category: CategoryResponse

    model_config = {"from_attributes": True}
