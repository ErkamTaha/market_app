"""
Admin routes for the market dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import Purchase
from app.services.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_categories = db.query(func.count(Category.id)).filter(Category.is_active == True).scalar()

    total_purchases = db.query(func.count(Purchase.id)).scalar()
    paid_purchases = db.query(func.count(Purchase.id)).filter(Purchase.status == "paid").scalar()
    cancelled_purchases = db.query(func.count(Purchase.id)).filter(Purchase.status == "cancelled").scalar()

    total_revenue = db.query(func.coalesce(func.sum(Purchase.total_price), 0)).filter(
        Purchase.status == "paid"
    ).scalar()

    total_items_sold = db.query(func.coalesce(func.sum(Purchase.item_count), 0)).filter(
        Purchase.status == "paid"
    ).scalar()

    low_stock = db.query(func.count(Product.id)).filter(
        Product.is_active == True, Product.stock <= 10
    ).scalar()

    return {
        "users": {"total": total_users},
        "products": {"total": total_products, "categories": total_categories, "low_stock": low_stock},
        "purchases": {
            "total": total_purchases,
            "paid": paid_purchases,
            "cancelled": cancelled_purchases,
            "total_items_sold": int(total_items_sold)
        },
        "revenue": {"total": float(total_revenue)}
    }


@router.get("/purchases")
def get_all_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    purchases = db.query(Purchase).options(
        joinedload(Purchase.user),
        joinedload(Purchase.items)
    ).order_by(Purchase.created_at.desc()).all()

    result = []
    for p in purchases:
        result.append({
            "id": p.id,
            "user_name": p.user.full_name,
            "user_email": p.user.email,
            "total_price": p.total_price,
            "item_count": p.item_count,
            "receipt_code": p.receipt_code,
            "payment_method": p.payment_method,
            "store_name": p.store_name,
            "status": p.status,
            "points_earned": p.points_earned,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "product_price": item.product_price,
                    "subtotal": item.subtotal
                }
                for item in p.items
            ]
        })
    return result


@router.get("/products")
def get_all_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    products = db.query(Product).options(
        joinedload(Product.category)
    ).order_by(Product.category_id, Product.name).all()

    return [{
        "id": p.id, "name": p.name, "brand": p.brand,
        "category": p.category.name if p.category else "-",
        "price": p.price, "discount_price": p.discount_price,
        "stock": p.stock, "is_in_stock": p.is_in_stock,
        "barcode": p.barcode, "unit": p.unit, "is_active": p.is_active
    } for p in products]


class StockUpdate(BaseModel):
    stock: int


@router.patch("/products/{product_id}/stock")
def update_stock(
    product_id: int, update: StockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    product.stock = update.stock
    product.is_in_stock = update.stock > 0
    db.commit()
    return {"message": f"'{product.name}' stok: {update.stock}"}
