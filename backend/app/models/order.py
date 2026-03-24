import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Purchase(Base):
    """
    A completed in-store purchase (receipt).

    Flow: Customer scans products → adds to cart → pays at checkout →
    gets a digital receipt with a verification code.

    No delivery tracking needed — the customer is physically in the store.
    The receipt_code is a unique code the cashier can verify.
    """
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    total_price = Column(Float, nullable=False)
    item_count = Column(Integer, nullable=False)

    # Unique receipt code — shown as QR to cashier for verification
    receipt_code = Column(String, unique=True, index=True, nullable=False,
                          default=lambda: f"MKT-{uuid.uuid4().hex[:8].upper()}")

    # Payment method: "card" (card in-app), "cash" (cash at register), "wallet" (wallet)
    payment_method = Column(String, default="card")

    # Which market location
    store_name = Column(String, default="Market Çerkezköy")

    # Status: "paid" or "cancelled" (refunded)
    status = Column(String, default="paid")

    # Loyalty points earned from this purchase
    points_earned = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    items = relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(Base):
    """
    Individual items in a purchase receipt.
    Snapshot of product info at time of purchase.
    """
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    product_name = Column(String, nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")
