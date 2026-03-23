"""
Seed data for the market app.
Creates categories and products on first run.
"""
from app.database import SessionLocal
from app.models.product import Category, Product


def seed_all():
    db = SessionLocal()

    # Only seed if no categories exist
    if db.query(Category).first():
        db.close()
        return

    print("Seed data yükleniyor...")

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
    db.close()
    print(f"✓ {len(categories_data)} kategori ve {len(products_data)} ürün oluşturuldu")
