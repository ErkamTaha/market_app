"""
Market Demo Data Script — In-Store Flow
"""
import os, sys, random, uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.product import Product
from app.models.order import Purchase, PurchaseItem
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
    user = User(email=u["email"], phone=u["phone"], full_name=u["full_name"],
                hashed_password=hash_password(u["password"]), loyalty_points=u["points"])
    db.add(user)
    db.commit()
    db.refresh(user)
    created_users.append(user)
    print(f"  ✓ {u['full_name']}")

print(f"\n  Toplam: {len(created_users)} kullanıcı\n")

# --- PURCHASES ---
products = db.query(Product).all()
if not products:
    print("  ⚠ Ürün yok!"); sys.exit(1)

now = datetime.now(timezone.utc)
payment_methods = ["kart", "kart", "kart", "nakit", "nakit"]

scenarios = [
    (0, 4, "ödendi", 5), (0, 2, "ödendi", 3), (0, 6, "ödendi", 0),
    (1, 3, "ödendi", 7), (1, 5, "ödendi", 1),
    (2, 8, "ödendi", 4), (2, 3, "ödendi", 2), (2, 4, "ödendi", 0), (2, 2, "iptal", 1),
    (3, 3, "ödendi", 6), (3, 5, "ödendi", 0),
    (4, 2, "ödendi", 8), (4, 4, "ödendi", 3), (4, 3, "ödendi", 0),
    (5, 6, "ödendi", 5), (5, 4, "ödendi", 2), (5, 7, "ödendi", 0), (5, 2, "iptal", 1),
]

print("Satışlar oluşturuluyor...")
for user_idx, num_items, status, days_ago in scenarios:
    user = created_users[user_idx]
    purchase_date = now - timedelta(days=days_ago, hours=random.randint(1, 12))
    selected = random.sample(products, min(num_items, len(products)))

    total = 0; item_count = 0; items = []
    for prod in selected:
        qty = random.randint(1, 3)
        price = prod.discount_price if prod.discount_price else prod.price
        subtotal = round(price * qty, 2)
        total += subtotal; item_count += qty
        items.append(PurchaseItem(
            product_id=prod.id, product_name=prod.name,
            product_price=price, quantity=qty, subtotal=subtotal
        ))

    points = int(total // 10)
    purchase = Purchase(
        user_id=user.id, total_price=round(total, 2), item_count=item_count,
        receipt_code=f"MKT-{uuid.uuid4().hex[:8].upper()}",
        payment_method=random.choice(payment_methods),
        store_name="Market Çerkezköy", status=status,
        points_earned=points if status == "ödendi" else 0,
        created_at=purchase_date
    )
    db.add(purchase); db.flush()
    for item in items:
        item.purchase_id = purchase.id; db.add(item)

db.commit()
print(f"  ✓ {len(scenarios)} satış oluşturuldu")

db.close()
print(f"\n{'='*50}\nDemo verileri oluşturuldu!\n{'='*50}")
print(f"\nGiriş: erkam@market.com / demo1234")
