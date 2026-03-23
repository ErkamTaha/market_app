from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderResponse, CheckoutRequest
from app.services.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Siparişler"])


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create an order from the user's cart.

    Flow:
    1. Get all cart items
    2. Verify each product is in stock
    3. Calculate total from DATABASE prices (not client)
    4. Create Order + OrderItems
    5. Reduce stock for each product
    6. Award loyalty points
    7. Clear the cart
    """
    cart_items = db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(CartItem.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Sepetiniz boş")

    # Build order items and calculate total
    total = 0.0
    order_items = []

    for cart_item in cart_items:
        product = cart_item.product

        if not product.is_in_stock or product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"'{product.name}' için yeterli stok yok (stok: {product.stock})"
            )

        # Use discount price if available, otherwise regular price
        price = product.discount_price if product.discount_price else product.price
        subtotal = price * cart_item.quantity
        total += subtotal

        order_items.append(OrderItem(
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

    # Create the order
    order = Order(
        user_id=current_user.id,
        total_price=round(total, 2),
        item_count=sum(item.quantity for item in order_items),
        status="hazırlanıyor",
        note=data.note
    )
    db.add(order)
    db.flush()  # Get the order.id without committing

    # Attach items to order
    for item in order_items:
        item.order_id = order.id
        db.add(item)

    # Award loyalty points: 1 point per 10 TL
    points = int(total // 10)
    current_user.loyalty_points += points

    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

    db.commit()
    db.refresh(order)

    # Load items for response
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()

    return order


@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user, newest first."""
    return db.query(Order).options(
        joinedload(Order.items)
    ).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order with its items."""
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu sipariş size ait değil")

    return order
