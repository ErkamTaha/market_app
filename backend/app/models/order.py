from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Order(Base):
    """
    A completed purchase.

    When the user checks out, all cart items become an Order
    with OrderItems. The cart is then cleared.

    Status flow:
      "hazırlanıyor" (preparing) → "hazır" (ready for pickup) → "teslim_edildi" (delivered)
                                 → "iptal" (cancelled)
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Total price at the time of order
    total_price = Column(Float, nullable=False)
    item_count = Column(Integer, nullable=False)

    status = Column(String, default="hazırlanıyor")
    # hazırlanıyor, hazır, teslim_edildi, iptal

    # Optional note from customer
    note = Column(Text)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    Individual items within an order.

    We store the price and name at the time of purchase because:
    - Product price might change after the order
    - Product might be deleted
    The customer's receipt should always show what they actually paid.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    # Snapshot at time of purchase
    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)  # price * quantity

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
