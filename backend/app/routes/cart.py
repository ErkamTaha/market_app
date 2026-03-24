from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=list[CartItemResponse])
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items in the user's cart."""
    return db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(CartItem.user_id == current_user.id).all()


@router.post("/", response_model=CartItemResponse, status_code=201)
def add_to_cart(
    data: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a product to the cart.
    If the product is already in the cart, increase the quantity.
    """
    product = db.query(Product).filter(
        Product.id == data.product_id,
        Product.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.is_in_stock or product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == data.product_id
    ).first()

    if existing:
        existing.quantity += data.quantity
        db.commit()
        db.refresh(existing)
        # Reload product relationship
        db.refresh(existing, ["product"])
        return existing

    cart_item = CartItem(
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    db.refresh(cart_item, ["product"])
    return cart_item


@router.patch("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the quantity of a cart item."""
    item = db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if data.quantity <= 0:
        db.delete(item)
        db.commit()
        raise HTTPException(status_code=200, detail="Item removed from cart")

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from the cart."""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from the cart."""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
