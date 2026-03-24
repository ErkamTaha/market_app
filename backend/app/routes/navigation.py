from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.location import MapZone, ProductLocation
from app.models.product import Product
from app.models.user import User
from app.schemas.location import (
    MapZoneCreate, MapZoneUpdate, MapZoneResponse,
    ProductLocationSet, ProductLocationResponse,
    NavigationPathResponse, ProductSearchResult
)
from app.services.auth import get_current_user
from app.services.pathfinding import find_path
from datetime import datetime, timezone

router = APIRouter(tags=["Navigation"])


# =====================
# PUBLIC ENDPOINTS
# =====================

@router.get("/navigation/map", response_model=list[MapZoneResponse])
def get_map_layout(db: Session = Depends(get_db)):
    """
    Get the full floor plan — all zones that make up the market map.
    Called by both the mobile app and admin dashboard to render the map.
    """
    return db.query(MapZone).filter(MapZone.is_active == True).all()


@router.get("/navigation/product/{product_id}/location", response_model=ProductLocationResponse | None)
def get_product_location(product_id: int, db: Session = Depends(get_db)):
    """Get where a specific product is located on the map."""
    loc = db.query(ProductLocation).filter(
        ProductLocation.product_id == product_id
    ).first()
    if not loc:
        raise HTTPException(404, "This product's location has not been set yet")
    return loc


@router.get("/navigation/all-locations")
def get_all_product_locations(db: Session = Depends(get_db)):
    """Get all product locations (for rendering pins on the map)."""
    locations = db.query(ProductLocation).options(
        joinedload(ProductLocation.product)
    ).all()

    return [{
        "id": loc.id,
        "product_id": loc.product_id,
        "product_name": loc.product.name,
        "product_brand": loc.product.brand,
        "product_price": loc.product.discount_price or loc.product.price,
        "category_id": loc.product.category_id,
        "x": loc.x,
        "y": loc.y,
        "z": loc.z,
        "zone_id": loc.zone_id,
        "shelf_label": loc.shelf_label
    } for loc in locations]


@router.get("/navigation/search")
def search_products_with_location(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Search products and include their location data.
    Used by the mobile app's "Find in Store" feature.
    """
    search_term = f"%{q}%"
    products = db.query(Product).filter(
        Product.is_active == True,
        (Product.name.ilike(search_term)) | (Product.brand.ilike(search_term))
    ).all()

    results = []
    for p in products:
        loc = db.query(ProductLocation).filter(
            ProductLocation.product_id == p.id
        ).first()

        results.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "price": p.price,
            "discount_price": p.discount_price,
            "image_url": p.image_url,
            "unit": p.unit,
            "location": {
                "id": loc.id,
                "product_id": loc.product_id,
                "zone_id": loc.zone_id,
                "x": loc.x,
                "y": loc.y,
                "z": loc.z,
                "shelf_label": loc.shelf_label,
                "updated_at": loc.updated_at.isoformat() if loc.updated_at else None
            } if loc else None
        })

    return results


@router.get("/navigation/path")
def get_navigation_path(
    from_x: float = Query(...),
    from_y: float = Query(...),
    to_x: float = Query(...),
    to_y: float = Query(...),
    db: Session = Depends(get_db)
):
    """
    Calculate the walking path from one point to another,
    avoiding shelves and walls.

    Returns a list of waypoints the user should follow,
    plus the total distance and estimated walking time.
    """
    zones = db.query(MapZone).filter(MapZone.is_active == True).all()
    result = find_path(zones, from_x, from_y, to_x, to_y)
    return result


@router.get("/navigation/route")
def get_multi_product_route(
    product_ids: str = Query(..., description="Comma-separated product IDs"),
    from_x: float = Query(50),
    from_y: float = Query(55),
    db: Session = Depends(get_db)
):
    """
    Calculate an optimized route to visit multiple products.

    Uses nearest-neighbor heuristic: from the starting point,
    always go to the closest unvisited product next.
    Not globally optimal, but good enough and fast.
    """
    ids = [int(x.strip()) for x in product_ids.split(",") if x.strip()]

    locations = db.query(ProductLocation).filter(
        ProductLocation.product_id.in_(ids)
    ).options(joinedload(ProductLocation.product)).all()

    if not locations:
        return {"stops": [], "total_distance": 0, "total_seconds": 0}

    zones = db.query(MapZone).filter(MapZone.is_active == True).all()

    # Nearest-neighbor ordering
    unvisited = list(locations)
    ordered = []
    current_x, current_y = from_x, from_y

    while unvisited:
        nearest = min(unvisited, key=lambda loc:
            ((loc.x - current_x) ** 2 + (loc.y - current_y) ** 2) ** 0.5
        )
        ordered.append(nearest)
        current_x, current_y = nearest.x, nearest.y
        unvisited.remove(nearest)

    # Build the full route
    stops = []
    total_distance = 0
    total_seconds = 0
    cx, cy = from_x, from_y

    for loc in ordered:
        path_result = find_path(zones, cx, cy, loc.x, loc.y)
        total_distance += path_result["distance"]
        total_seconds += path_result["estimated_seconds"]

        stops.append({
            "product_id": loc.product_id,
            "product_name": loc.product.name,
            "x": loc.x,
            "y": loc.y,
            "shelf_label": loc.shelf_label,
            "path": path_result["waypoints"],
            "segment_distance": path_result["distance"]
        })

        cx, cy = loc.x, loc.y

    return {
        "stops": stops,
        "total_distance": round(total_distance, 1),
        "total_seconds": total_seconds
    }


# =====================
# ADMIN ENDPOINTS
# =====================

@router.post("/admin/map/zones", response_model=MapZoneResponse, status_code=201)
def create_zone(
    data: MapZoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new map zone (shelf, aisle, wall, etc.)."""
    zone = MapZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.put("/admin/map/zones/{zone_id}", response_model=MapZoneResponse)
def update_zone(
    zone_id: int,
    data: MapZoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a map zone's properties."""
    zone = db.query(MapZone).filter(MapZone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(zone, key, value)

    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/admin/map/zones/{zone_id}")
def delete_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a map zone."""
    zone = db.query(MapZone).filter(MapZone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    db.delete(zone)
    db.commit()
    return {"message": f"'{zone.name}' deleted"}


@router.put("/admin/products/{product_id}/location", response_model=ProductLocationResponse)
def set_product_location(
    product_id: int,
    data: ProductLocationSet,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set or update a product's location on the map.
    Called by admin when a worker places a product on a shelf.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    existing = db.query(ProductLocation).filter(
        ProductLocation.product_id == product_id
    ).first()

    if existing:
        existing.x = data.x
        existing.y = data.y
        existing.z = data.z
        existing.zone_id = data.zone_id
        existing.shelf_label = data.shelf_label
        existing.updated_by = data.updated_by
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        loc = ProductLocation(
            product_id=product_id,
            zone_id=data.zone_id,
            x=data.x,
            y=data.y,
            z=data.z,
            shelf_label=data.shelf_label,
            updated_by=data.updated_by
        )
        db.add(loc)
        db.commit()
        db.refresh(loc)
        return loc


@router.delete("/admin/products/{product_id}/location")
def remove_product_location(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a product's location from the map."""
    loc = db.query(ProductLocation).filter(
        ProductLocation.product_id == product_id
    ).first()
    if not loc:
        raise HTTPException(404, "Product location not found")
    db.delete(loc)
    db.commit()
    return {"message": "Product location removed"}
