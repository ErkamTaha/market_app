from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Category(Base):
    """
    Product categories — e.g., Meyve & Sebze, Süt Ürünleri, İçecekler.

    Categories organize the product catalog. A supermarket might have
    10-20 top-level categories. For the prototype, we keep it flat
    (no subcategories), but the structure supports adding them later
    by adding a parent_id foreign key.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    icon = Column(String)  # Ionicon name for display in the app
    sort_order = Column(Integer, default=0)  # Controls display order
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    Individual products in the market.

    Key difference from car wash packages:
    - Products have stock (how many are available)
    - Products have barcodes (for scanning)
    - Products have weights/units (kg, adet, litre)
    - Products belong to categories
    - Products have images
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)

    # Discounted price — if set, shown as the sale price with original crossed out
    discount_price = Column(Float, nullable=True)

    # Unit of measurement: "kg", "adet" (piece), "litre", "paket" (pack)
    unit = Column(String, default="adet")

    # Barcode — for scanning at the market. EAN-13 format (13 digits).
    barcode = Column(String, unique=True, index=True)

    # Stock management
    stock = Column(Integer, default=0)
    is_in_stock = Column(Boolean, default=True)

    # Image URL (for prototype, we'll use placeholder URLs)
    image_url = Column(String)

    # Brand name
    brand = Column(String)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="products")
