from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class MapZone(Base):
    """
    Represents a physical area in the market.

    The store floor plan is built from these zones — each one is a rectangle
    on the 2D map. Together, they form the complete layout showing shelves,
    aisles, walls, entrance, and checkout areas.

    In the future (Autodesk 3D Viewer), these same zones map to 3D regions
    using the z/height fields.

    zone_type options:
    - "shelf"     → product shelving area (obstacle, products placed here)
    - "aisle"     → walkable corridor between shelves
    - "entrance"  → store entrance (walkable, user starting point)
    - "checkout"  → cash register area
    - "wall"      → outer walls (obstacle)
    """
    __tablename__ = "map_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)           # "Reyon 1 — Meyve & Sebze"
    zone_type = Column(String, nullable=False)       # shelf, aisle, entrance, checkout, wall

    # Rectangle position on the 2D map (top-left corner + dimensions)
    # Map coordinate system: 0,0 is top-left, units are arbitrary (we use 100x60 grid)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)

    # Display properties
    color = Column(String, default="#e2e8f0")       # hex color for rendering
    label = Column(String)                           # short label shown on map

    # Future 3D support
    floor = Column(Integer, default=0)               # for multi-floor buildings
    z_height = Column(Float, default=3.0)            # shelf/wall height in meters

    is_active = Column(Boolean, default=True)

    # Relationship to products placed in this zone
    product_locations = relationship("ProductLocation", back_populates="zone")


class ProductLocation(Base):
    """
    Links a product to its physical location on the market map.

    Each product has exactly ONE location (unique constraint on product_id).
    Workers update these when restocking or reorganizing the market.

    The x,y coordinates are the exact pin position on the 2D map.
    The z coordinate stores shelf height (for future 3D viewer).
    """
    __tablename__ = "product_locations"

    id = Column(Integer, primary_key=True, index=True)

    # One location per product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True, index=True)

    # Which zone (shelf) this product is on
    zone_id = Column(Integer, ForeignKey("map_zones.id"), nullable=True)

    # Exact position on the 2D map
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)

    # Shelf height — 0=floor level, 1.5=eye level, etc. (for future 3D)
    z = Column(Float, default=1.0)

    # Human-readable description: "Reyon 3, Raf 2"
    shelf_label = Column(String)

    # When this location was last updated (tracks restocking)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_by = Column(String)  # name of worker who placed it

    # Relationships
    product = relationship("Product", backref="location", uselist=False)
    zone = relationship("MapZone", back_populates="product_locations")
