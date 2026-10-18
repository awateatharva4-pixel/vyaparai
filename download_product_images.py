import os
import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import requests
from PIL import Image

STATIC_PRODUCTS_DIR = os.path.abspath(r"e:\vyaparai\app\static\products")
os.makedirs(STATIC_PRODUCTS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 VyaparAI/1.0"
}

# Mapping of product identifiers to candidate image URLs (with reliable fallbacks)
PRODUCT_IMAGE_SOURCES = {
    "GROC-SUG-001": {
        "slug": "sugar",
        "name": "Madhur Sugar (1kg)",
        "urls": [
            "https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=500&auto=format&fit=crop&q=80",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Sucre_blanc_cassonade_complet_rapadura.jpg/640px-Sucre_blanc_cassonade_complet_rapadura.jpg"
        ]
    },
    "FMCG-PARLE-100G": {
        "slug": "parle_g",
        "name": "Parle-G Biscuit 100g",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/a/a1/Parle-G_Biscuit.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/7/7b/Parle-G.jpg"
        ]
    },
    "OIL-FORT-1L": {
        "slug": "fortune_oil",
        "name": "Fortune Sunflower Oil 1L",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/3/33/Bottle_1_liter_Sunflower_refined_oil.jpg",
            "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "BAK-PAV-LADI": {
        "slug": "ladi_pav",
        "name": "Fresh Bakery Pav (Ladi)",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/3/36/Vada_pav_01.jpg",
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "DAL-TUR-001": {
        "slug": "tur_dal",
        "name": "Tur Dal (Pigeon Pea Lentils)",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/0/02/Pigeon_Pea_%28Toor_Dal%29_%2849683602388%29.jpg",
            "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "GROC-SALT-1K": {
        "slug": "tata_salt",
        "name": "Tata Salt 1kg",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/d/d9/Tata_salt_packet_photo.webp",
            "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "GROC-ATTA-5K": {
        "slug": "aashirvaad_atta",
        "name": "Aashirvaad Atta 5kg",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/42/Atta-05.jpg",
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "FMCG-MAGGI-70G": {
        "slug": "maggi",
        "name": "Maggi 2-Minute Noodles 70g",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/9/9e/Maggi_noodles.jpg",
            "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "VEG-KANDA-001": {
        "slug": "red_onion",
        "name": "Fresh Red Onion",
        "urls": [
            "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&auto=format&fit=crop&q=80",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Mixed_onions.jpg/640px-Mixed_onions.jpg"
        ]
    },
    "VEG-BATATA-001": {
        "slug": "potato",
        "name": "Fresh Potato",
        "urls": [
            "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&auto=format&fit=crop&q=80",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Patates.jpg/640px-Patates.jpg"
        ]
    },
    "AUTO-VID-KINLEY": {
        "slug": "kinley_water",
        "name": "Kinley Water Bottle 1L",
        "urls": [
            "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?w=500&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1523362628745-0c100150b504?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "AUTO-VID-PEN": {
        "slug": "reynolds_pen",
        "name": "Reynolds Blue Pen",
        "urls": [
            "https://upload.wikimedia.org/wikipedia/commons/4/4d/Ballpoint_Pen.jpg",
            "https://images.unsplash.com/photo-1585336261026-6213038a8e10?w=500&auto=format&fit=crop&q=80"
        ]
    },
    "AUTO-VID-NOTEBOOK": {
        "slug": "classmate_notebook",
        "name": "Classmate Notebook",
        "urls": [
            "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
            "https://upload.wikimedia.org/wikipedia/commons/7/76/Spiral-bound_notebooks.JPG"
        ]
    },
    "DAIRY-AMUL-500M": {
        "slug": "amul_milk",
        "name": "Amul Taaza Milk 500ml",
        "urls": [
            "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=500&auto=format&fit=crop&q=80"
        ]
    }
}

def download_and_save_image(sku, meta):
    slug = meta["slug"]
    name = meta["name"]
    target_sku_path = os.path.join(STATIC_PRODUCTS_DIR, f"{sku}.jpg")
    target_slug_path = os.path.join(STATIC_PRODUCTS_DIR, f"{slug}.jpg")

    for url in meta["urls"]:
        try:
            print(f"[FETCH] Attempting {sku} ({name}) from: {url[:60]}...")
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200 and len(r.content) > 1000:
                # Open with Pillow to validate, format, and resize
                img = Image.open(io.BytesIO(r.content))
                img = img.convert("RGB")
                
                # Resize keeping aspect ratio (max 600x600 for fast loading)
                img.thumbnail((600, 600), Image.Resampling.LANCZOS)
                
                # Save as both SKU and slug
                img.save(target_sku_path, "JPEG", quality=88, optimize=True)
                img.save(target_slug_path, "JPEG", quality=88, optimize=True)
                
                size_kb = os.path.getsize(target_sku_path) / 1024
                print(f"✅ [SAVED] {sku} & {slug}.jpg ({size_kb:.1f} KB)")
                return True
            else:
                print(f"⚠️ [WARN] Non-200 ({r.status_code}) or small size ({len(r.content)} B)")
        except Exception as e:
            print(f"❌ [ERROR] Failed URL {url[:40]}: {e}")

    print(f"🚨 [FAILED] All URLs failed for {sku}")
    return False

if __name__ == "__main__":
    success_count = 0
    total = len(PRODUCT_IMAGE_SOURCES)
    print(f"--- Starting Download of {total} Product Images ---")
    for sku, meta in PRODUCT_IMAGE_SOURCES.items():
        if download_and_save_image(sku, meta):
            success_count += 1
    print(f"--- Finished: {success_count}/{total} Images Saved to {STATIC_PRODUCTS_DIR} ---")
