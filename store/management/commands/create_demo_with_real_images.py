# store/management/commands/create_demo_with_real_images.py
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.text import slugify

from store.models import Category, Product, ProductImages, VariationValue

import os, random, time, mimetypes
from io import BytesIO
import requests
from django.conf import settings

try:
    from PIL import Image, ImageDraw
except Exception:
    raise SystemExit("Pillow is required. Install with: pip install Pillow")

PEXELS_API_KEY = getattr(settings, "PEXELS_API_KEY", "")
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

# Demo product names you can tweak
CATEGORY_PRODUCTS = {
    "Smart Watches": ["ChronoX S1","ChronoX S2 LTE","FitPulse Pro","GearLite 3","NeoBand Active","TimeOne Sport","WaveFit 7","PulseTrack Mini","Orbit Watch OS","RunMate Steel"],
    "Audio": ["SonicBuds Pro","SonicBuds Lite","AirBeats ANC","BassBox Mini","StudioMic USB-C","SoundBar 2.1","PartyBoom 300","ClarityPod Open-Ear","NoiseCancel Max","DeskMic Go"],
    "Televisions": ["Aurora 43\" 4K LED","Aurora 55\" 4K LED","CineMax 50\" HDR","NovaScreen 65\" QLED","NovaScreen 75\" 8K","HomeView 32\" HD","ThePanel 55\" OLED","Stadium 85\" 4K"],
    "Smart Phones": ["NovaPhone A3","NovaPhone A3 Plus","Luma S10","Luma S10 Pro","Orbit One","Orbit One Pro","Vega X1","Vega X1 Max","Metro M5","Pixelate P2 Lite"],
    "Digital Cameras": ["Photon D500 DSLR","Photon M100 Mirrorless","SnapShot Go Compact","ActionCam 4K","Lumic X-T Mirrorless","ProStudio FX","StreetShot Rangefinder","WildTrack TrailCam"],
    "Computer & Laptop": ["QuantumBook 14","QuantumBook 15 Pro","WorkMate 13","GameForge 17","MiniPC Cube","UltraTower i5","CreatorBook 16","StudentBook 11","DeskBox Ryzen"],
}
PRICE_RANGES = {"Smart Watches":(59,349),"Audio":(19,399),"Televisions":(179,2999),"Smart Phones":(129,1299),"Digital Cameras":(89,1999),"Computer & Laptop":(199,2499)}
SIZE_OPTIONS = {"Smart Watches":["38mm","41mm","45mm"],"Televisions":["43\"","50\"","55\"","65\""],"Smart Phones":["64GB","128GB","256GB"],"Computer & Laptop":["13.3\"","14\"","15.6\"","17\""],"Audio":[],"Digital Cameras":["Body Only","18-55mm Kit","24-70mm Kit"]}
COLOR_OPTIONS = {"Smart Watches":["Black","Silver","Rose Gold"],"Televisions":["Black"],"Smart Phones":["Midnight","Starlight","Blue"],"Computer & Laptop":["Slate","Silver","Black"],"Audio":["Black","White","Blue"],"Digital Cameras":["Black","Graphite"]}

# Query templates to get realistic stock photos per category
CATEGORY_QUERIES = {
    "Smart Watches": ["smartwatch closeup", "fitness watch wrist", "wearable watch"],
    "Audio": ["headphones studio", "wireless earbuds closeup", "bluetooth speaker"],
    "Televisions": ["4k tv living room", "oled tv on stand", "qled tv wall mounted"],
    "Smart Phones": ["smartphone closeup", "mobile phone on desk", "hand holding smartphone"],
    "Digital Cameras": ["mirrorless camera closeup", "dslr camera lens", "camera on table"],
    "Computer & Laptop": ["laptop on desk", "gaming laptop", "desktop pc setup"],
}

CATEGORY_COLORS = {"Smart Watches":(66,133,244),"Audio":(52,168,83),"Televisions":(251,188,5),"Smart Phones":(234,67,53),"Digital Cameras":(156,39,176),"Computer & Laptop":(0,121,107)}

def media_dir(subfolder):
    root = getattr(settings, "MEDIA_ROOT", None)
    if not root:
        raise CommandError("MEDIA_ROOT is not set. Configure MEDIA_ROOT in settings.")
    path = os.path.join(root, subfolder)
    os.makedirs(path, exist_ok=True)
    return path

def unique_slug(model, base):
    base_slug = slugify(base) or "item"
    slug = base_slug
    i = 2
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{i}"
        i += 1
    return slug

def fetch_pexels_images(query, per_page=6, orientation="landscape"):
    if not PEXELS_API_KEY:
        raise CommandError("PEXELS_API_KEY not set. Get one at https://www.pexels.com/api/ and export it.")
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": orientation}
    r = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    results = data.get("photos", []) or []
    # return direct image URLs (prefer large/large2x; original can be huge)
    urls = []
    for p in results:
        src = p.get("src", {})
        for key in ("large2x", "large", "original", "medium"):
            if src.get(key):
                urls.append(src[key])
                break
    return urls

def download_to_content_file(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    content = resp.content
    content_type = resp.headers.get("Content-Type", "")
    ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or os.path.splitext(url)[1] or ".jpg"
    # Normalize weird extensions
    if ext.lower() in (".jpe", ".jpeg"): ext = ".jpg"
    if ext.lower() not in (".jpg", ".png", ".webp"): ext = ".jpg"
    return ContentFile(content), ext

def ensure_main_image(product, urls, force=False):
    if product.image and not force:
        return False
    if not urls:
        # last resort: quick placeholder (rarely needed if API works)
        img = Image.new("RGB", (900, 600), CATEGORY_COLORS.get(product.category.name, (90, 90, 90)))
        d = ImageDraw.Draw(img)
        txt = f"{product.category.name}\n{product.name}"
        lines = [line for line in txt.split("\n") if line]
        w, h = img.size; y = h // 2 - (len(lines) * 18)
        for line in lines:
            tw = d.textlength(line); d.text(((w - tw) / 2, y), line, fill=(255, 255, 255)); y += 28
        buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        product.image.save(f"{product.slug}.png", ContentFile(buf.read()), save=False)
        return True
    cf, ext = download_to_content_file(urls[0])
    product.image.save(f"{product.slug}{ext}", cf, save=False)
    return True

def add_gallery(product, urls, count=3, force=False):
    existing = ProductImages.objects.filter(product=product).count()
    if existing >= count and not force:
        return 0
    added = 0
    # skip first url (used by main). take next ones
    for i, u in enumerate(urls[1: count + 1], start=1):
        cf, ext = download_to_content_file(u)
        rec = ProductImages(product=product)
        rec.image.save(f"{product.slug}-{i}{ext}", cf, save=False)
        rec.save()
        added += 1
    return added

def create_variations(product, base_price):
    cat = product.category.name
    for s in SIZE_OPTIONS.get(cat, []):
        VariationValue.objects.get_or_create(variation="size", name=s, product=product, defaults={"price": max(1, int(round(base_price + random.randint(-20, 120))))})
    for c in COLOR_OPTIONS.get(cat, []):
        VariationValue.objects.get_or_create(variation="color", name=c, product=product, defaults={"price": max(1, int(round(base_price + random.randint(-10, 80))))})

class Command(BaseCommand):
    help = "Create demo products and fetch REAL stock photos from Pexels for main and gallery images, plus variations."

    def add_arguments(self, parser):
        parser.add_argument("--per-category", type=int, default=0, help="Limit number of products to create per category (0 = use all defaults)")
        parser.add_argument("--force-images", action="store_true", help="Overwrite existing main/gallery images")

    def handle(self, *args, **opts):
        media_dir("products"); media_dir("product_gallery")
        limit = opts["per_category"]; force_images = opts["force_images"]

        total_created = 0
        total_imaged = 0
        categories = Category.objects.all()
        if not categories.exists():
            # ensure the known demo categories exist
            for cname in CATEGORY_PRODUCTS.keys():
                Category.objects.get_or_create(name=cname)
            categories = Category.objects.all()

        for category in categories:
            names = CATEGORY_PRODUCTS.get(category.name)
            if not names:
                continue
            if limit > 0:
                names = names[:limit]

            # prefetch a set of real image URLs for this category
            queries = CATEGORY_QUERIES.get(category.name, [category.name])
            query = random.choice(queries)
            try:
                urls = fetch_pexels_images(query=query, per_page=max(6, len(names) // 2 + 2))
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Pexels fetch failed for {category.name}: {e}"))
                urls = []

            for name in names:
                prod, created = Product.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={
                        "preview_desc": f"{name} — demo listing for {category.name}"[:255],
                        "description": f"Demo data for {name} in {category.name}. Replace text/specs as needed."[:1000],
                        "price": round(random.uniform(*PRICE_RANGES.get(category.name, (10, 999))), 2),
                        "old_price": 0.0,
                        "is_stock": (random.random() > 0.1),
                        "slug": unique_slug(Product, name),
                    },
                )
                if created:
                    total_created += 1

                # Main image (real photo if available)
                if ensure_main_image(prod, urls, force=force_images):
                    prod.save()
                    total_imaged += 1

                # Gallery slides (3)
                added = add_gallery(prod, urls, count=3, force=force_images)
                total_imaged += added

                # Variations
                create_variations(prod, prod.price)

                # be polite to API
                time.sleep(0.2)

        self.stdout.write(self.style.SUCCESS(f"Done. Products created: {total_created}. Images added/updated: {total_imaged}."))
