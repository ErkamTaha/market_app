from pydantic import BaseModel
from datetime import datetime


# --- MAP ZONES ---

class MapZoneCreate(BaseModel):
    name: str
    zone_type: str
    x: float
    y: float
    width: float
    height: float
    color: str = "#e2e8f0"
    label: str | None = None


class MapZoneUpdate(BaseModel):
    name: str | None = None
    zone_type: str | None = None
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    color: str | None = None
    label: str | None = None


class MapZoneResponse(BaseModel):
    id: int
    name: str
    zone_type: str
    x: float
    y: float
    width: float
    height: float
    color: str
    label: str | None
    floor: int
    is_active: bool

    model_config = {"from_attributes": True}


# --- PRODUCT LOCATIONS ---

class ProductLocationSet(BaseModel):
    """Used by admin to place a product on the map."""
    zone_id: int | None = None
    x: float
    y: float
    z: float = 1.0
    shelf_label: str | None = None
    updated_by: str | None = None


class ProductLocationResponse(BaseModel):
    id: int
    product_id: int
    zone_id: int | None
    x: float
    y: float
    z: float
    shelf_label: str | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


# --- NAVIGATION ---

class Waypoint(BaseModel):
    x: float
    y: float


class NavigationPathResponse(BaseModel):
    waypoints: list[Waypoint]
    distance: float       # total distance in map units
    estimated_seconds: int  # walking time estimate


class ProductSearchResult(BaseModel):
    id: int
    name: str
    brand: str | None
    price: float
    discount_price: float | None
    image_url: str | None
    unit: str
    location: ProductLocationResponse | None

    model_config = {"from_attributes": True}
