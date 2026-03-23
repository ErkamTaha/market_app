from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.cart import CartItem
from app.models.order import Purchase, PurchaseItem
from app.models.user import User
from app.schemas.order import PurchaseResponse, CheckoutRequest
from app.services.auth import get_current_user

router = APIRouter(prefix="/purchases", tags=["Alışverişler"])


@router.post("/checkout", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete an in-store purchase.

    Flow:
    1. Get all cart items
    2. Verify stock for each product
    3. Calculate total from DATABASE prices
    4. Create Purchase + PurchaseItems (digital receipt)
    5. Reduce stock
    6. Award loyalty points (1 per 10 TL)
    7. Clear the cart
    8. Return receipt with unique receipt_code for cashier verification
    """
    cart_items = db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(CartItem.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Sepetiniz boş")

    total = 0.0
    purchase_items = []

    for cart_item in cart_items:
        product = cart_item.product

        if not product.is_in_stock or product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"'{product.name}' için yeterli stok yok (stok: {product.stock})"
            )

        price = product.discount_price if product.discount_price else product.price
        subtotal = round(price * cart_item.quantity, 2)
        total += subtotal

        purchase_items.append(PurchaseItem(
            product_id=product.id,
            product_name=product.name,
            product_price=price,
            quantity=cart_item.quantity,
            subtotal=subtotal
        ))

        # Reduce stock
        product.stock -= cart_item.quantity
        if product.stock <= 0:
            product.is_in_stock = False

    # Award loyalty points
    points = int(total // 10)

    # Create purchase (receipt)
    purchase = Purchase(
        user_id=current_user.id,
        total_price=round(total, 2),
        item_count=sum(item.quantity for item in purchase_items),
        payment_method=data.payment_method,
        status="ödendi",
        points_earned=points
    )
    db.add(purchase)
    db.flush()

    for item in purchase_items:
        item.purchase_id = purchase.id
        db.add(item)

    # Update user points
    current_user.loyalty_points += points

    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

    db.commit()
    db.refresh(purchase)

    purchase = db.query(Purchase).options(
        joinedload(Purchase.items)
    ).filter(Purchase.id == purchase.id).first()

    return purchase


@router.get("/", response_model=list[PurchaseResponse])
def get_my_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all purchases (receipts) for the current user, newest first."""
    return db.query(Purchase).options(
        joinedload(Purchase.items)
    ).filter(
        Purchase.user_id == current_user.id
    ).order_by(Purchase.created_at.desc()).all()


@router.get("/{receipt_code}", response_model=PurchaseResponse)
def get_receipt(
    receipt_code: str,
    db: Session = Depends(get_db)
):
    """
    Get a purchase by receipt code.
    Used by the cashier to verify a customer's digital receipt.
    Public endpoint — no auth required (cashier scans the QR).
    """
    purchase = db.query(Purchase).options(
        joinedload(Purchase.items)
    ).filter(Purchase.receipt_code == receipt_code).first()

    if not purchase:
        raise HTTPException(status_code=404, detail="Fiş bulunamadı")
    return purchase
