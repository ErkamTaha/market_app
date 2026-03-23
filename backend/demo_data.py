"""
Market Demo Data Script
=======================
Creates realistic fake users, orders, and cart data.

Usage:
    cd backend
    source venv/bin/activate
    python demo_data.py
"""
import os
import sys
import random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.services.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("=== Market Demo Veri Oluşturucu ===\n")

# --- USERS ---
demo_users = [
    {"email": "erkam@market.com", "phone": "+905551111111", "full_name": "Erkam Taha", "password": "demo1234", "points": 85},
    {"email": "ayse@test.com", "phone": "+905552222222", "full_name": "Ayşe Yılmaz", "password": "demo1234", "points": 45},
    {"email": "mehmet@test.com", "phone": "+905553333333", "full_name": "Mehmet Kaya", "password": "demo1234", "points": 120},
    {"email": "fatma@test.com", "phone": "+905554444444", "full_name": "Fatma Demir", "password": "demo1234", "points": 30},
    {"email": "ali@test.com", "phone": "+905555555555", "full_name": "Ali Çelik", "password": "demo1234", "points": 60},
    {"email": "zeynep@test.com", "phone": "+905556666666", "full_name": "Zeynep Öztürk", "password": "demo1234", "points": 95},
]

created_users = []
for u in demo_users:
    existing = db.query(User).filter(User.email == u["email"]).first()
    if existing:
        print(f"  Kullanıcı zaten var: {u['full_name']}")
        created_users.append(existing)
        continue

    user = User(
        email=u["email"], phone=u["phone"], full_name=u["full_name"],
        hashed_password=hash_password(u["password"]),
        loyalty_points=u["points"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    created_users.append(user)
    print(f"  ✓ Kullanıcı oluşturuldu: {u['full_name']}")

print(f"\n  Toplam kullanıcı: {len(created_users)}\n")

# --- ORDERS ---
products = db.query(Product).all()
if not products:
    print("  ⚠ Ürün bulunamadı! Önce sunucuyu çalıştırın.")
    sys.exit(1)

now = datetime.now(timezone.utc)

# Order scenarios
order_scenarios = [
    # (user_idx, num_items, status, days_ago, note)
    (0, 4, "teslim_edildi", 5, None),
    (0, 2, "teslim_edildi", 3, "Kapıda bırakın"),
    (0, 6, "hazırlanıyor", 0, None),
    (1, 3, "teslim_edildi", 7, None),
    (1, 5, "hazır", 0, "Poşetsiz olsun"),
    (2, 8, "teslim_edildi", 4, None),
    (2, 3, "teslim_edildi", 2, None),
    (2, 4, "hazırlanıyor", 0, None),
    (2, 2, "iptal", 1, None),
    (3, 3, "teslim_edildi", 6, "Meyveleri sert seçin"),
    (3, 5, "hazır", 0, None),
    (4, 2, "teslim_edildi", 8, None),
    (4, 4, "teslim_edildi", 3, None),
    (4, 3, "hazırlanıyor", 0, "Acil lütfen"),
    (5, 6, "teslim_edildi", 5, None),
    (5, 4, "teslim_edildi", 2, None),
    (5, 7, "hazırlanıyor", 0, None),
    (5, 2, "iptal", 1, "Vazgeçtim"),
]

print("Siparişler oluşturuluyor...")
for user_idx, num_items, status, days_ago, note in order_scenarios:
    user = created_users[user_idx]
    order_date = now - timedelta(days=days_ago, hours=random.randint(1, 12))

    # Pick random products
    selected = random.sample(products, min(num_items, len(products)))
    total = 0
    item_count = 0
    order_items = []

    for prod in selected:
        qty = random.randint(1, 3)
        price = prod.discount_price if prod.discount_price else prod.price
        subtotal = round(price * qty, 2)
        total += subtotal
        item_count += qty
        order_items.append(OrderItem(
            product_id=prod.id,
            product_name=prod.name,
            product_price=price,
            quantity=qty,
            subtotal=subtotal
        ))

    order = Order(
        user_id=user.id,
        total_price=round(total, 2),
        item_count=item_count,
        status=status,
        note=note,
        created_at=order_date
    )
    db.add(order)
    db.flush()

    for item in order_items:
        item.order_id = order.id
        db.add(item)

db.commit()
print(f"  ✓ {len(order_scenarios)} sipariş oluşturuldu")

db.close()

print("\n" + "=" * 50)
print("Demo verileri başarıyla oluşturuldu!")
print("=" * 50)
print(f"\nGiriş bilgileri:")
print(f"  E-posta: erkam@market.com")
print(f"  Şifre:   demo1234")
print(f"\nTüm kullanıcılar için şifre: demo1234")
