"""
Seed data for the market app.
Creates categories and products on first run.
"""
from app.database import SessionLocal
from app.models.product import Category, Product
from app.models.location import MapZone, ProductLocation


def seed_all():
    db = SessionLocal()

    # Only seed if no categories exist
    if db.query(Category).first():
        db.close()
        return

    print("Loading seed data...")

    # --- CATEGORIES ---
    categories_data = [
        {"name": "Meyve & Sebze", "description": "Taze meyve ve sebzeler", "icon": "leaf-outline", "sort_order": 1},
        {"name": "Süt Ürünleri", "description": "Süt, peynir, yoğurt", "icon": "water-outline", "sort_order": 2},
        {"name": "Et & Tavuk", "description": "Taze et, tavuk, balık", "icon": "restaurant-outline", "sort_order": 3},
        {"name": "Ekmek & Fırın", "description": "Ekmek, poğaça, börek", "icon": "pizza-outline", "sort_order": 4},
        {"name": "İçecekler", "description": "Su, meyve suyu, gazlı içecek", "icon": "beer-outline", "sort_order": 5},
        {"name": "Atıştırmalık", "description": "Cips, çikolata, kuruyemiş", "icon": "fast-food-outline", "sort_order": 6},
        {"name": "Temizlik", "description": "Deterjan, sabun, kağıt ürünleri", "icon": "sparkles-outline", "sort_order": 7},
        {"name": "Kişisel Bakım", "description": "Şampuan, diş macunu, kozmetik", "icon": "body-outline", "sort_order": 8},
    ]

    categories = []
    for cat_data in categories_data:
        cat = Category(**cat_data)
        db.add(cat)
        db.flush()
        categories.append(cat)

    # --- PRODUCTS ---
    products_data = [
        # Meyve & Sebze
        {"category_idx": 0, "name": "Domates", "price": 29.90, "discount_price": 24.90, "unit": "kg", "barcode": "8690000000101", "stock": 150, "brand": "Çiftçi", "image_url": "https://placehold.co/400x400/e74c3c/fff?text=Domates"},
        {"category_idx": 0, "name": "Salatalık", "price": 19.90, "unit": "kg", "barcode": "8690000000102", "stock": 120, "brand": "Çiftçi", "image_url": "https://placehold.co/400x400/27ae60/fff?text=Salatalık"},
        {"category_idx": 0, "name": "Elma (Golden)", "price": 34.90, "unit": "kg", "barcode": "8690000000103", "stock": 80, "brand": "Anadolu Bahçe", "image_url": "https://placehold.co/400x400/f1c40f/fff?text=Elma"},
        {"category_idx": 0, "name": "Muz", "price": 49.90, "discount_price": 39.90, "unit": "kg", "barcode": "8690000000104", "stock": 60, "brand": "Dole", "image_url": "https://placehold.co/400x400/f39c12/fff?text=Muz"},
        {"category_idx": 0, "name": "Patates", "price": 14.90, "unit": "kg", "barcode": "8690000000105", "stock": 200, "brand": "Çiftçi", "image_url": "https://placehold.co/400x400/d35400/fff?text=Patates"},
        {"category_idx": 0, "name": "Soğan", "price": 12.90, "unit": "kg", "barcode": "8690000000106", "stock": 180, "brand": "Çiftçi", "image_url": "https://placehold.co/400x400/e67e22/fff?text=Soğan"},

        # Süt Ürünleri
        {"category_idx": 1, "name": "Günlük Süt 1L", "price": 32.90, "unit": "adet", "barcode": "8690000000201", "stock": 100, "brand": "Sütaş", "image_url": "https://placehold.co/400x400/ecf0f1/333?text=Süt"},
        {"category_idx": 1, "name": "Beyaz Peynir 500g", "price": 89.90, "discount_price": 74.90, "unit": "adet", "barcode": "8690000000202", "stock": 50, "brand": "Pınar", "image_url": "https://placehold.co/400x400/f5f5dc/333?text=Peynir"},
        {"category_idx": 1, "name": "Yoğurt 1kg", "price": 44.90, "unit": "adet", "barcode": "8690000000203", "stock": 80, "brand": "Sütaş", "image_url": "https://placehold.co/400x400/fff8dc/333?text=Yoğurt"},
        {"category_idx": 1, "name": "Kaşar Peynir 300g", "price": 69.90, "unit": "adet", "barcode": "8690000000204", "stock": 40, "brand": "Pınar", "image_url": "https://placehold.co/400x400/ffd700/333?text=Kaşar"},
        {"category_idx": 1, "name": "Tereyağ 250g", "price": 59.90, "unit": "adet", "barcode": "8690000000205", "stock": 35, "brand": "Sütaş", "image_url": "https://placehold.co/400x400/fff8dc/333?text=Tereyağ"},

        # Et & Tavuk
        {"category_idx": 2, "name": "Dana Kıyma", "price": 249.90, "unit": "kg", "barcode": "8690000000301", "stock": 30, "brand": "Namet", "image_url": "https://placehold.co/400x400/c0392b/fff?text=Kıyma"},
        {"category_idx": 2, "name": "Tavuk Bütün", "price": 129.90, "discount_price": 109.90, "unit": "kg", "barcode": "8690000000302", "stock": 25, "brand": "Banvit", "image_url": "https://placehold.co/400x400/f0e68c/333?text=Tavuk"},
        {"category_idx": 2, "name": "Tavuk Göğüs", "price": 159.90, "unit": "kg", "barcode": "8690000000303", "stock": 20, "brand": "Banvit", "image_url": "https://placehold.co/400x400/f0e68c/333?text=Göğüs"},
        {"category_idx": 2, "name": "Sucuk 250g", "price": 79.90, "unit": "adet", "barcode": "8690000000304", "stock": 45, "brand": "Yayla", "image_url": "https://placehold.co/400x400/8b0000/fff?text=Sucuk"},

        # Ekmek & Fırın
        {"category_idx": 3, "name": "Tam Buğday Ekmek", "price": 12.50, "unit": "adet", "barcode": "8690000000401", "stock": 50, "brand": "Uno", "image_url": "https://placehold.co/400x400/d2691e/fff?text=Ekmek"},
        {"category_idx": 3, "name": "Tost Ekmeği", "price": 22.90, "unit": "adet", "barcode": "8690000000402", "stock": 40, "brand": "Uno", "image_url": "https://placehold.co/400x400/deb887/333?text=Tost"},
        {"category_idx": 3, "name": "Poğaça 5'li", "price": 34.90, "unit": "paket", "barcode": "8690000000403", "stock": 30, "brand": "Fırın", "image_url": "https://placehold.co/400x400/f4a460/333?text=Poğaça"},

        # İçecekler
        {"category_idx": 4, "name": "Su 1.5L", "price": 7.90, "unit": "adet", "barcode": "8690000000501", "stock": 300, "brand": "Erikli", "image_url": "https://placehold.co/400x400/87ceeb/333?text=Su"},
        {"category_idx": 4, "name": "Ayran 1L", "price": 19.90, "unit": "adet", "barcode": "8690000000502", "stock": 80, "brand": "Sütaş", "image_url": "https://placehold.co/400x400/f0f0f0/333?text=Ayran"},
        {"category_idx": 4, "name": "Portakal Suyu 1L", "price": 39.90, "discount_price": 32.90, "unit": "adet", "barcode": "8690000000503", "stock": 60, "brand": "Cappy", "image_url": "https://placehold.co/400x400/ff8c00/fff?text=Portakal"},
        {"category_idx": 4, "name": "Cola 1L", "price": 29.90, "unit": "adet", "barcode": "8690000000504", "stock": 100, "brand": "Coca-Cola", "image_url": "https://placehold.co/400x400/c0392b/fff?text=Cola"},
        {"category_idx": 4, "name": "Çay 1kg", "price": 89.90, "unit": "adet", "barcode": "8690000000505", "stock": 70, "brand": "Çaykur", "image_url": "https://placehold.co/400x400/228b22/fff?text=Çay"},

        # Atıştırmalık
        {"category_idx": 5, "name": "Cips Klasik 150g", "price": 24.90, "unit": "adet", "barcode": "8690000000601", "stock": 90, "brand": "Lay's", "image_url": "https://placehold.co/400x400/ffd700/333?text=Cips"},
        {"category_idx": 5, "name": "Çikolata 80g", "price": 19.90, "discount_price": 14.90, "unit": "adet", "barcode": "8690000000602", "stock": 120, "brand": "Ülker", "image_url": "https://placehold.co/400x400/4a2c2a/fff?text=Çikolata"},
        {"category_idx": 5, "name": "Fıstık 200g", "price": 49.90, "unit": "adet", "barcode": "8690000000603", "stock": 55, "brand": "Tadım", "image_url": "https://placehold.co/400x400/deb887/333?text=Fıstık"},
        {"category_idx": 5, "name": "Bisküvi 200g", "price": 14.90, "unit": "adet", "barcode": "8690000000604", "stock": 100, "brand": "Eti", "image_url": "https://placehold.co/400x400/d2b48c/333?text=Bisküvi"},

        # Temizlik
        {"category_idx": 6, "name": "Bulaşık Deterjanı 1L", "price": 44.90, "unit": "adet", "barcode": "8690000000701", "stock": 60, "brand": "Fairy", "image_url": "https://placehold.co/400x400/00ced1/fff?text=Deterjan"},
        {"category_idx": 6, "name": "Çamaşır Suyu 2.5L", "price": 34.90, "unit": "adet", "barcode": "8690000000702", "stock": 40, "brand": "Domestos", "image_url": "https://placehold.co/400x400/4169e1/fff?text=Çamaşır"},
        {"category_idx": 6, "name": "Tuvalet Kağıdı 16'lı", "price": 119.90, "discount_price": 99.90, "unit": "paket", "barcode": "8690000000703", "stock": 45, "brand": "Solo", "image_url": "https://placehold.co/400x400/f0f0f0/333?text=TK"},

        # Kişisel Bakım
        {"category_idx": 7, "name": "Şampuan 500ml", "price": 69.90, "unit": "adet", "barcode": "8690000000801", "stock": 50, "brand": "Head&Shoulders", "image_url": "https://placehold.co/400x400/4682b4/fff?text=Şampuan"},
        {"category_idx": 7, "name": "Diş Macunu 100ml", "price": 39.90, "unit": "adet", "barcode": "8690000000802", "stock": 70, "brand": "Colgate", "image_url": "https://placehold.co/400x400/dc143c/fff?text=Diş+Mac."},
        {"category_idx": 7, "name": "Sabun 4'lü", "price": 29.90, "discount_price": 24.90, "unit": "paket", "barcode": "8690000000803", "stock": 80, "brand": "Dalan", "image_url": "https://placehold.co/400x400/90ee90/333?text=Sabun"},
    ]

    for p_data in products_data:
        cat_idx = p_data.pop("category_idx")
        p_data["category_id"] = categories[cat_idx].id
        p_data["is_in_stock"] = p_data["stock"] > 0
        product = Product(**p_data)
        db.add(product)

    db.commit()
    print(f"✓ {len(categories_data)} categories and {len(products_data)} products created")

    # --- MAP LAYOUT ---
    # Only seed map if no zones exist
    if not db.query(MapZone).first():
        seed_map(db)

    db.close()


def seed_map(db):
    """
    Create the default market floor plan.

    Map coordinate system: 100 wide × 60 tall
    0,0 is top-left

    Layout:
    ┌─────────────────────────────────────────────────────────────┐
    │  wall                                                       │  y=0
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
    │  │ Shelf 1  │  │ Shelf 2  │  │ Shelf 3  │  │ Shelf 4  │      │  y=5-20
    │  │ Meyve    │  │ Süt      │  │ Et       │  │ Ekmek    │      │
    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
    │     aisle        aisle        aisle        aisle            │  y=20-25
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
    │  │ Shelf 5  │  │ Shelf 6  │  │ Shelf 7  │  │ Shelf 8  │      │  y=25-40
    │  │ İçecek   │  │ Atıştır  │  │ Temizlik │  │ Kişisel  │      │
    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
    │     aisle        aisle        aisle        aisle            │  y=40-45
    │                                          ┌──────────┐      │
    │  [Giriş]                                │  Kasa     │      │  y=45-55
    │                                          └──────────┘      │
    └─────────────────────────────────────────────────────────────┘  y=60
    """
    print("Loading map seed data...")

    zones_data = [
        # Outer walls
        {"name": "Top Wall", "zone_type": "wall", "x": 0, "y": 0, "width": 100, "height": 2, "color": "#374151"},
        {"name": "Left Wall", "zone_type": "wall", "x": 0, "y": 0, "width": 2, "height": 60, "color": "#374151"},
        {"name": "Right Wall", "zone_type": "wall", "x": 98, "y": 0, "width": 2, "height": 60, "color": "#374151"},
        {"name": "Bottom Wall Left", "zone_type": "wall", "x": 0, "y": 58, "width": 30, "height": 2, "color": "#374151"},
        {"name": "Bottom Wall Right", "zone_type": "wall", "x": 45, "y": 58, "width": 55, "height": 2, "color": "#374151"},

        # Row 1 shelves (y: 5-18)
        {"name": "Shelf 1 — Meyve & Sebze", "zone_type": "shelf", "x": 5, "y": 5, "width": 18, "height": 13, "color": "#86efac", "label": "Meyve\nSebze"},
        {"name": "Shelf 2 — Süt Ürünleri", "zone_type": "shelf", "x": 28, "y": 5, "width": 18, "height": 13, "color": "#bfdbfe", "label": "Süt\nÜrünleri"},
        {"name": "Shelf 3 — Et & Tavuk", "zone_type": "shelf", "x": 51, "y": 5, "width": 18, "height": 13, "color": "#fca5a5", "label": "Et\nTavuk"},
        {"name": "Shelf 4 — Ekmek & Fırın", "zone_type": "shelf", "x": 74, "y": 5, "width": 18, "height": 13, "color": "#fde68a", "label": "Ekmek\nFırın"},

        # Aisle between row 1 and row 2 (y: 18-25)
        {"name": "Aisle 1", "zone_type": "aisle", "x": 2, "y": 18, "width": 96, "height": 7, "color": "#f8fafc"},

        # Row 2 shelves (y: 25-38)
        {"name": "Shelf 5 — İçecekler", "zone_type": "shelf", "x": 5, "y": 25, "width": 18, "height": 13, "color": "#93c5fd", "label": "İçecekler"},
        {"name": "Shelf 6 — Atıştırmalık", "zone_type": "shelf", "x": 28, "y": 25, "width": 18, "height": 13, "color": "#fdba74", "label": "Atıştır-\nmalık"},
        {"name": "Shelf 7 — Temizlik", "zone_type": "shelf", "x": 51, "y": 25, "width": 18, "height": 13, "color": "#67e8f9", "label": "Temizlik"},
        {"name": "Shelf 8 — Kişisel Bakım", "zone_type": "shelf", "x": 74, "y": 25, "width": 18, "height": 13, "color": "#c4b5fd", "label": "Kişisel\nBakım"},

        # Aisle between row 2 and bottom (y: 38-45)
        {"name": "Aisle 2", "zone_type": "aisle", "x": 2, "y": 38, "width": 96, "height": 7, "color": "#f8fafc"},

        # Side aisles
        {"name": "Left Aisle", "zone_type": "aisle", "x": 2, "y": 2, "width": 3, "height": 56, "color": "#f8fafc"},
        {"name": "Right Aisle", "zone_type": "aisle", "x": 92, "y": 2, "width": 6, "height": 56, "color": "#f8fafc"},
        {"name": "Cross Aisle 1", "zone_type": "aisle", "x": 23, "y": 5, "width": 5, "height": 33, "color": "#f8fafc"},
        {"name": "Cross Aisle 2", "zone_type": "aisle", "x": 46, "y": 5, "width": 5, "height": 33, "color": "#f8fafc"},
        {"name": "Cross Aisle 3", "zone_type": "aisle", "x": 69, "y": 5, "width": 5, "height": 33, "color": "#f8fafc"},

        # Entrance
        {"name": "Entrance", "zone_type": "entrance", "x": 30, "y": 52, "width": 15, "height": 6, "color": "#bbf7d0", "label": "ENTRANCE"},

        # Checkout
        {"name": "Checkout 1", "zone_type": "checkout", "x": 60, "y": 45, "width": 14, "height": 8, "color": "#fef08a", "label": "CHECKOUT"},
        {"name": "Checkout 2", "zone_type": "checkout", "x": 76, "y": 45, "width": 14, "height": 8, "color": "#fef08a", "label": "CHECKOUT"},

        # Open floor
        {"name": "Main Floor", "zone_type": "aisle", "x": 2, "y": 45, "width": 58, "height": 13, "color": "#f8fafc"},
    ]

    zones = []
    for z_data in zones_data:
        zone = MapZone(**z_data)
        db.add(zone)
        db.flush()
        zones.append(zone)

    # --- PRODUCT LOCATIONS ---
    # Assign each product to a position on the correct shelf
    # Products are ordered by category in the seed data

    products = db.query(Product).order_by(Product.category_id, Product.id).all()

    # Map category_id to shelf zone index (0-based in zones list, shelves start at index 5)
    # Category 1 (Meyve) → Zone index 5 (Shelf 1)
    # Category 2 (Süt)   → Zone index 6 (Shelf 2)
    # etc.
    category_to_zone = {}
    categories = db.query(Category).order_by(Category.sort_order).all()
    for i, cat in enumerate(categories):
        zone_idx = 5 + i  # shelves start at index 5 in zones_data
        if zone_idx < len(zones):
            category_to_zone[cat.id] = zones[zone_idx]

    product_count = 0
    for product in products:
        zone = category_to_zone.get(product.category_id)
        if not zone:
            continue

        # Distribute products evenly within the shelf zone
        products_in_cat = [p for p in products if p.category_id == product.category_id]
        idx_in_cat = products_in_cat.index(product)
        total_in_cat = len(products_in_cat)

        # Calculate position within the shelf
        col = idx_in_cat % 3  # up to 3 columns
        row = idx_in_cat // 3  # rows

        px = zone.x + 3 + col * 5  # spread across the shelf width
        py = zone.y + 3 + row * 4  # spread across the shelf height

        loc = ProductLocation(
            product_id=product.id,
            zone_id=zone.id,
            x=px,
            y=py,
            z=1.0 + (idx_in_cat % 3) * 0.5,  # vary shelf height
            shelf_label=f"{zone.label or zone.name}, Row {row + 1}"
        )
        db.add(loc)
        product_count += 1

    db.commit()
    print(f"✓ {len(zones_data)} zones and {product_count} product locations created")
