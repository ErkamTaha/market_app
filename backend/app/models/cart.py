from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class CartItem(Base):
    """
    Shopping cart items.

    Each row = one product in a user's cart with a quantity.
    The cart is server-side (stored in database), not just in the app's memory.

    Why server-side cart?
    1. Cart persists if user closes the app
    2. Cart syncs across devices (phone + tablet)
    3. We can track abandoned carts for analytics
    4. Stock validation happens on the server
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    product = relationship("Product")
