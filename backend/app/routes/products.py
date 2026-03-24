from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.product import Category, Product
from app.schemas.product import CategoryResponse, ProductResponse, ProductWithCategoryResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all active categories, sorted by sort_order."""
    return db.query(Category).filter(
        Category.is_active == True
    ).order_by(Category.sort_order).all()


@router.get("/", response_model=list[ProductResponse])
def get_products(
    category_id: int | None = None,
    search: str | None = None,
    on_sale: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get products with optional filters.

    - category_id: filter by category
    - search: search by name or brand
    - on_sale: only show discounted products
    """
    query = db.query(Product).filter(Product.is_active == True)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.brand.ilike(search_term))
        )

    if on_sale:
        query = query.filter(Product.discount_price.isnot(None))

    return query.order_by(Product.name).all()


@router.get("/{product_id}", response_model=ProductWithCategoryResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product with its category."""
    product = db.query(Product).options(
        joinedload(Product.category)
    ).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/barcode/{barcode}", response_model=ProductWithCategoryResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """
    Look up a product by its barcode.
    Called when the user scans a barcode at the market.
    """
    product = db.query(Product).options(
        joinedload(Product.category)
    ).filter(Product.barcode == barcode).first()

    if not product:
        raise HTTPException(status_code=404, detail="No product found for this barcode")
    return product
