"""
Admin routes for the market dashboard.
In production, these would require admin role verification.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import Order, OrderItem
from app.services.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard overview statistics."""
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_categories = db.query(func.count(Category.id)).filter(Category.is_active == True).scalar()

    total_orders = db.query(func.count(Order.id)).scalar()
    preparing_orders = db.query(func.count(Order.id)).filter(Order.status == "hazırlanıyor").scalar()
    ready_orders = db.query(func.count(Order.id)).filter(Order.status == "hazır").scalar()
    delivered_orders = db.query(func.count(Order.id)).filter(Order.status == "teslim_edildi").scalar()
    cancelled_orders = db.query(func.count(Order.id)).filter(Order.status == "iptal").scalar()

    total_revenue = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
        Order.status != "iptal"
    ).scalar()

    low_stock = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.stock <= 10
    ).scalar()

    return {
        "users": {"total": total_users},
        "products": {"total": total_products, "categories": total_categories, "low_stock": low_stock},
        "orders": {
            "total": total_orders,
            "preparing": preparing_orders,
            "ready": ready_orders,
            "delivered": delivered_orders,
            "cancelled": cancelled_orders
        },
        "revenue": {"total": float(total_revenue)}
    }


@router.get("/orders")
def get_all_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders with user info."""
    orders = db.query(Order).options(
        joinedload(Order.user),
        joinedload(Order.items)
    ).order_by(Order.created_at.desc()).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "user_name": o.user.full_name,
            "user_email": o.user.email,
            "total_price": o.total_price,
            "item_count": o.item_count,
            "status": o.status,
            "note": o.note,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "items": [
                {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "product_price": item.product_price,
                    "subtotal": item.subtotal
                }
                for item in o.items
            ]
        })
    return result


class OrderStatusUpdate(BaseModel):
    status: str


@router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an order's status (hazırlanıyor → hazır → teslim_edildi)."""
    valid = ["hazırlanıyor", "hazır", "teslim_edildi", "iptal"]
    if update.status not in valid:
        raise HTTPException(400, f"Geçersiz durum. Geçerli: {', '.join(valid)}")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Sipariş bulunamadı")

    order.status = update.status
    db.commit()
    return {"message": f"Sipariş #{order_id} durumu '{update.status}' olarak güncellendi"}


@router.get("/products")
def get_all_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products with category info for admin management."""
    products = db.query(Product).options(
        joinedload(Product.category)
    ).order_by(Product.category_id, Product.name).all()

    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category.name if p.category else "-",
            "price": p.price,
            "discount_price": p.discount_price,
            "stock": p.stock,
            "is_in_stock": p.is_in_stock,
            "barcode": p.barcode,
            "unit": p.unit,
            "is_active": p.is_active
        })
    return result


class StockUpdate(BaseModel):
    stock: int


@router.patch("/products/{product_id}/stock")
def update_stock(
    product_id: int,
    update: StockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product's stock count."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Ürün bulunamadı")

    product.stock = update.stock
    product.is_in_stock = update.stock > 0
    db.commit()
    return {"message": f"'{product.name}' stok: {update.stock}"}
