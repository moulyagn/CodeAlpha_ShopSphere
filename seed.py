import json
import random
import re
from datetime import datetime, timedelta, timezone
import sys
from urllib.parse import quote_plus

from app import create_app
from extensions import db
from models import Brand, Category, Product


random.seed(20260904)

CATEGORY_DATA = {
    "Mobiles": ["Apple", "Samsung", "OnePlus", "Google", "Xiaomi"],
    "Laptops": ["Apple", "Dell", "Lenovo", "HP", "ASUS"],
    "Electronics": ["Sony", "Bose", "JBL", "Philips", "LG"],
    "Gaming": ["PlayStation", "Xbox", "Nintendo", "Razer", "Logitech"],
    "Fashion": ["Levi's", "H&M", "Manyavar", "FabIndia", "Mango"],
    "Shoes": ["Nike", "adidas", "Puma", "New Balance", "Clarks"],
    "Beauty": ["Forest Essentials", "MAC", "The Body Shop", "Nykaa", "Clinique"],
    "Furniture": ["IKEA", "Urban Ladder", "Wakefit", "Durian", "Pepperfry"],
    "Kitchen": ["Prestige", "KITCHENAID", "Borosil", "Wonderchef", "Havells"],
    "Books": ["Penguin", "HarperCollins", "Rupa", "Bloomsbury", "Aleph"],
    "Sports": ["Nike", "adidas", "Yonex", "Wilson", "Decathlon"],
    "Fitness": ["Fitbit", "Garmin", "Cultsport", "Boldfit", "Apple"],
    "Luxury Watches": ["Titan", "Fossil", "Seiko", "Casio", "Tissot"],
    "Jewellery": ["Tanishq", "Swarovski", "Senco", "CaratLane", "Mia"],
    "Travel": ["Samsonite", "American Tourister", "Wildcraft", "VIP", "Mokobara"],
    "Groceries": ["Tata", "Aashirvaad", "Organic Tattva", "Happilo", "Fortune"],
    "Office": ["HP", "Canon", "Pilot", "Kokuyo", "Fellowes"],
    "Automotive": ["Bosch", "Michelin", "Castrol", "3M", "Goodyear"],
    "Pet Supplies": ["Royal Canin", "Pedigree", "Whiskas", "Farmina", "Heads Up For Tails"],
    "Kids": ["LEGO", "Mattel", "Hamleys", "Funskool", "Babyhug"],
}

CATEGORY_BASE_PRICES = {
    "Mobiles": 18999, "Laptops": 42999, "Electronics": 1499, "Gaming": 2499,
    "Fashion": 899, "Shoes": 1499, "Beauty": 499, "Furniture": 4999,
    "Kitchen": 799, "Books": 299, "Sports": 999, "Fitness": 1299,
    "Luxury Watches": 6999, "Jewellery": 1999, "Travel": 1499, "Groceries": 199,
    "Office": 399, "Automotive": 699, "Pet Supplies": 299, "Kids": 599,
}

ADJECTIVES = ["Signature", "Heritage", "Essential", "Elevated", "Studio", "Classic", "Modern", "Select", "Pro", "Everyday", "Prime", "Luxe", "Air", "Ultra"]


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


CATEGORY_IMAGE_QUERIES = {
    "Mobiles": ["smartphone front screen", "android phone", "mobile phone camera", "smartphone hand", "phone charging", "phone on desk", "foldable smartphone", "phone close up", "smartphone retail", "phone back camera"],
    "Laptops": ["laptop computer open", "laptop keyboard", "ultrabook desk", "gaming laptop", "business laptop", "laptop workspace", "laptop screen", "laptop side view", "laptop office", "portable computer"],
    "Electronics": ["wireless headphones", "bluetooth speaker", "television screen", "digital camera", "smart home device", "earbuds case", "computer monitor", "tablet device", "audio amplifier", "electronic gadget"],
    "Gaming": ["game console controller", "gaming controller", "gaming keyboard", "gaming mouse", "arcade cabinet", "gaming headset", "video game console", "gaming desk setup", "handheld game console", "pc gaming setup"],
    "Fashion": ["indian fashion clothing", "silk saree", "mens fashion shirt", "womens fashion dress", "cotton kurta", "fashion jacket", "fashion accessories", "clothing rack", "fashion handbag", "traditional indian clothing"],
    "Shoes": ["running shoes pair", "sneakers shoes", "leather formal shoes", "hiking boots", "womens heels", "sports trainers", "casual shoes", "white sneakers", "shoe collection", "walking shoes"],
    "Beauty": ["skincare bottles", "makeup cosmetics", "perfume bottle", "lipstick beauty", "face serum", "beauty products flatlay", "natural skincare", "makeup brush", "beauty cream", "bath body products"],
    "Furniture": ["modern sofa living room", "wooden chair furniture", "dining table", "bedroom furniture", "bookshelf furniture", "wooden cabinet", "modern desk furniture", "armchair interior", "side table furniture", "home furniture"],
    "Kitchen": ["kitchen mixer appliance", "stainless cookware", "coffee machine kitchen", "kitchen blender", "dinner plates", "modern kitchen appliance", "cast iron pan", "electric kettle", "kitchen knives", "indian kitchen cooking"],
    "Books": ["books stack hardcover", "open book pages", "bookstore shelf", "novel book cover", "literature books", "business books", "books reading desk", "paperback books", "library books", "book collection"],
    "Sports": ["football soccer ball", "cricket bat ball", "basketball hoop", "tennis racket", "badminton racket", "sports equipment", "swimming goggles", "cycling helmet", "sports ball", "athlete equipment"],
    "Fitness": ["fitness dumbbells", "yoga mat", "treadmill gym", "fitness smartwatch", "resistance bands", "gym kettlebell", "exercise bicycle", "foam roller fitness", "weight lifting gym", "home workout equipment"],
    "Luxury Watches": ["mens wristwatch luxury", "luxury watch closeup", "mechanical wristwatch", "gold wristwatch", "watch leather strap", "classic wristwatch", "watch dial closeup", "diver watch", "chronograph watch", "watch on wrist"],
    "Jewellery": ["gold jewellery necklace", "diamond ring", "indian jewellery", "gold earrings", "bracelet jewellery", "pearl necklace", "jewellery box", "gemstone ring", "silver jewellery", "luxury jewellery"],
    "Travel": ["travel suitcase luggage", "carry on suitcase", "travel backpack", "leather passport holder", "travel bag airport", "luggage set", "travel accessories", "weekender bag", "travel organizer", "suitcase wheels"],
    "Groceries": ["fresh vegetables basket", "grocery shopping basket", "rice grains bag", "spices bowls", "organic food products", "fresh fruit market", "coffee beans package", "healthy grocery food", "cooking oil bottle", "pantry groceries"],
    "Office": ["office stationery desk", "printer office", "notebook pen desk", "office chair desk", "desk organizer", "computer keyboard office", "filing folders", "whiteboard office", "desk lamp office", "office supplies"],
    "Automotive": ["car dashboard", "car tire wheel", "automotive tools", "car interior", "motorcycle helmet", "car polish products", "electric car", "car engine", "auto accessories", "car detailing"],
    "Pet Supplies": ["dog food bowl", "cat toys", "pet bed dog", "pet collar leash", "aquarium supplies", "pet grooming", "cat scratching post", "dog treats", "pet carrier", "pet toys"],
    "Kids": ["lego building blocks", "wooden kids toy", "children books", "kids bicycle", "teddy bear toy", "kids educational toy", "baby clothing", "board game children", "toy train", "kids art supplies"],
}


UNSPLASH_PHOTO_IDS = {
    "Mobiles": ["1511707171634-5f897ff02aa9", "1510557880182-3d4d3cba35a5", "1511707171634-5f897ff02aa9", "1556656793-08538906a9f8", "1523206489230-c012c64b2b48", "1541807084-5c52b6b3adef", "1512428559087-560fa5ceab42", "1556656793-08538906a9f8", "1523206489230-c012c64b2b48", "1541807084-5c52b6b3adef"],
    "Laptops": ["1496181133206-80ce9b88a853", "1498050108023-c5249f4df085", "1496181133206-80ce9b88a853", "1525547719571-a2d4ac8945e2", "1531297484001-80022131f5a1", "1497366811353-6870744d04b2", "1504384308090-c894fdcc538d", "1516321318423-f06f85e504b3", "1593642532744-d377ab507dc8", "1541807084-5c52b6b3adef"],
    "Electronics": ["1505740420928-5e560c06d30e", "1546435770-a3e426bf472b", "1493225457124-a3eb161ffa5f", "1526170375885-4d8ecf77b99f", "1516321318423-f06f85e504b3", "1572569511254-d8f925fe2cbb", "1505740420928-5e560c06d30e", "1550745165-9bc0b252726f", "1593359677879-a4bb92f829d1", "1550751827-4bd374c3f58b"],
    "Gaming": ["1542751371-adc38448a05e", "1593305841991-05c297ba4575", "1605901309584-818e25960a8f", "1598550476439-6847785fcea6", "1603481546238-487240415921", "1612287230202-1ff1d85d1bdf", "1542751371-adc38448a05e", "1606144042614-b2417e99c4e3", "1547394765-185e1e68f34e", "1598550476439-6847785fcea6"],
    "Fashion": ["1529139574466-a303027c1d8b", "1490481651871-ab68de25d43d", "1483985988355-763728e1935b", "1515886657613-9f3515b0c78f", "1525507119028-ed4c629a60a3", "1539109136881-3be0616acf4b", "1529139574466-a303027c1d8b", "1551488831-00ddcb6c6bd3", "1485230895905-ec40ba36b9bc", "1496747611176-843222e1e57c"],
    "Shoes": ["1542291026-7eec264c27ff", "1549298916-b41d501d3772", "1460353581641-37baddab0fa2", "1495555961986-6d4c1ecb7be3", "1552346154-21d32810aba3", "1595950653106-6c9ebd614d3a", "1542291026-7eec264c27ff", "1460353581641-37baddab0fa2", "1543508282-6319a3e2621f", "1603808033192-082d6919d3e1"],
    "Beauty": ["1596462502278-27bfdc403348", "1556228578-0d85b1a4d571", "1522335789203-aabd1fc54bc9", "1571781926291-c477ebfd024b", "1586495777744-4413f21062fa", "1512496015851-a90fb38ba796", "1612817288484-6f916006741a", "1598440947619-2c35fc9aa908", "1515377905703-c4788e51af15", "1541643600914-78b084683601"],
    "Furniture": ["1555041469-a586c61ea9bc", "1556228453-efd6c1ff04f6", "1538688525198-9b88f6f53126", "1549497538-303791108f95", "1567016432779-094069958ea5", "1555041469-a586c61ea9bc", "1505693416388-ac5ce068fe85", "1524758631624-e2822e304c36", "1493663284031-b7e3aefcae8e", "1558211583-d26f610c1eb1"],
    "Kitchen": ["1556911220-bff31c812dba", "1556910103-1c02745aae4d", "1558317374-067fb5f30001", "1574781330855-d0db8cc6a79c", "1601050690597-df0568f70950", "1515003197210-e0cd71810b5f", "1528712306091-ed0763094c98", "1556911220-bff31c812dba", "1558317374-067fb5f30001", "1601050690597-df0568f70950"],
    "Books": ["1544947950-fa07a98d237f", "1495446815901-a7297e633e8d", "1512820790803-83ca734da794", "1521587760476-6c12a4b040da", "1526243741027-444d633d7365", "1544947950-fa07a98d237f", "1532012197267-da84d127e765", "1543002588-bfa74002ed7e", "1495446815901-a7297e633e8d", "1507842217343-583bb7270b66"],
    "Sports": ["1461896836934-ffe607ba8211", "1579952363873-27f3bade9f55", "1546519638-68e109498ffc", "1552674605-db6ffd4facb5", "1517649763962-0c623066013b", "1538805060514-97d9cc17730c", "1558618666-fcd25c85cd64", "1599058917212-d750089bc07e", "1517836357463-d25dfeac3438", "1534438327276-14e5300c3a48"],
    "Fitness": ["1571019613454-1cb2f99b2d8b", "1517836357463-d25dfeac3438", "1581009146145-b5ef050c2e1e", "1534438327276-14e5300c3a48", "1598289431512-b97b0917affc", "1583454110551-21f2fa2afe61", "1579758629938-03607ccdbaba", "1571019613454-1cb2f99b2d8b", "1517836357463-d25dfeac3438", "1581009146145-b5ef050c2e1e"],
    "Luxury Watches": ["1524805444758-089113d48a6d", "1523275335684-37898b6baf30", "1547996160-81dfa63595aa", "1523170335258-f5ed11844a49", "1533139502658-0198f920d8e8", "1509048191080-d2984bad6ae5", "1524805444758-089113d48a6d", "1522312346375-d1a52e2b99b3", "1524592094714-0f0654e20314", "1508685096489-7aacd43bd3b1"],
    "Jewellery": ["1515562141207-7a88fb7ce338", "1512418490979-92798cec1380", "1535632066927-ab7c9ab60908", "1506630448388-4e683c67ddb0", "1617038220319-276d3cfab638", "1515562141207-7a88fb7ce338", "1543294001-f7cd5d7fb516", "1602173574767-37ac01994b2a", "1599643478518-a784e5dc4c8f", "1573408301185-9146fe634ad0"],
    "Travel": ["1553062407-98eeb64c6a62", "1553062407-98eeb64c6a62", "1553062407-98eeb64c6a62", "1553062407-98eeb64c6a62", "1553531384-cc64ac80f931", "1523779917675-b6ed3a42a561", "1566576912321-d58ddd7a6088", "1556742049-0cfed4f6a45d", "1548777123-e216912df7d8", "1553062407-98eeb64c6a62"],
    "Groceries": ["1542838132-92c53300491e", "1540420773420-3366772f4999", "1542838132-92c53300491e", "1498837167922-ddd27525d352", "1547592180-85f173990554", "1512621776951-a57141f2eefd", "1447933601403-0c6688de566e", "1509440159596-0249088772ff", "1513104890138-7c749659a591", "1474979266404-7eaacbcd87c5"],
    "Office": ["1497366754035-f200968a6e72", "1497366811353-6870744d04b2", "1456324504439-367cee3b3c32", "1497215842964-222b430dc094", "1516321318423-f06f85e504b3", "1497366216548-37526070297c", "1524758631624-e2822e304c36", "1517048676732-d65bc937f952", "1517245386807-bb43f82c33c4", "1497366412874-3415097a27e7"],
    "Automotive": ["1503376780353-7e6692767b70", "1492144534655-ae79c964c9d7", "1542282088-72c9c27ed0cd", "1503736334956-4c8f8e92946d", "1493238792000-8113da705763", "1549317661-bd32c8ce0db2", "1552519507-da3b142c6e3d", "1583121274602-3e2820c69888", "1511919884226-fd3cad34687c", "1504215680853-026ed2a45def"],
    "Pet Supplies": ["1589924691995-400dc9ecc119", "1552053831-71594a27632d", "1450778869180-41d0601e046e", "1589924691995-400dc9ecc119", "1516734212186-a967f81ad0d7", "1601758228041-f3b2795255f1", "1548199973-03cce0bbc87b", "1589924691995-400dc9ecc119", "1589924691995-400dc9ecc119", "1592194996308-7b43878e84a6"],
    "Kids": ["1596461404969-9ae70f2830c1", "1560969184-10fe8719e047", "1594736797933-d0501ba2fe65", "1599623560574-39d485900c95", "1596461404969-9ae70f2830c1", "1566576912321-d58ddd7a6088", "1587654780291-39c9404d746b", "1596464716127-f2a82984de30", "1599623560574-39d485900c95", "1503454537195-1dcabb73ffb9"],
}


CATEGORY_IMAGE_POOLS = {
    category: [f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=900&h=900&q=88&variant={slot}" for slot, photo_id in enumerate(photo_ids, start=1)]
    for category, photo_ids in UNSPLASH_PHOTO_IDS.items()
}


def image_urls(category_name, brand_name, index):
    pool = CATEGORY_IMAGE_POOLS[category_name]
    primary_index = index % len(pool)
    return [pool[(primary_index + offset) % len(pool)] for offset in range(3)]


def build_product(category_name, brand_name, index):
    adjective = ADJECTIVES[index % len(ADJECTIVES)]
    category_word = category_name.rstrip("s")
    if category_name == "Mobiles":
        model = f"iPhone {13 + index % 4} {['Pro', 'Plus', 'Air'][index % 3]}"
    elif category_name == "Shoes":
        model = f"{['Air Max', 'Court Vision', 'Pegasus', 'Runner', 'Flex'][index % 5]} {100 + index % 80}"
    elif category_name == "Laptops":
        model = f"{['Book', 'Inspiron', 'ThinkPad', 'Pavilion', 'Zenbook'][index % 5]} {14 + index % 5}"
    else:
        model = f"{category_word} {index + 1:02d}"
    title = f"{brand_name} {adjective} {model}"
    base = CATEGORY_BASE_PRICES[category_name]
    price = round(base * (0.75 + (index % 9) * 0.12), -1)
    discount = 8 + (index * 7) % 43
    mrp = round(price / (1 - discount / 100), -1)
    features = [f"Curated {category_name.lower()} essential", "Quality checked by ShopSphere", "Designed for modern Indian living"]
    specs = {"Collection": category_name, "Brand": brand_name, "Warranty": "1 year manufacturer warranty", "Origin": "India / International select"}
    if category_name in {"Mobiles", "Laptops", "Electronics", "Gaming", "Office", "Fitness"}:
        specs.update({"Connectivity": "Bluetooth 5.3 / Wi-Fi", "Colour": ["Midnight Black", "Champagne Gold", "Ivory White"][index % 3]})
    product_images = image_urls(category_name, brand_name, index)
    return Product(
        title=title,
        name=title,
        slug=slugify(f"{title}-{index}"),
        description=f"A thoughtfully selected {category_name.lower()} piece from {brand_name}, balancing dependable performance with a refined everyday feel.",
        price=price,
        mrp=mrp,
        discount=discount,
        specs=json.dumps(specs),
        stock=(index * 13) % 48,
        delivery_estimate=f"Delivery in {2 + index % 5}-{4 + index % 5} days",
        rating=round(3.8 + (index % 13) / 10, 1),
        review_count=24 + (index * 37) % 1800,
        seller=f"{brand_name} Official Store",
        features=json.dumps(features),
        image_urls=json.dumps(product_images),
        primary_image=product_images[0],
        images=json.dumps(product_images),
        views=50 + (index * 113) % 9500,
        category_id=None,
        brand_id=None,
    )


def seed():
    app = create_app()
    with app.app_context():
        if Product.query.count() and "--reset-products" not in sys.argv:
            print("Products already exist. Use python seed.py --reset-products to rebuild the product catalog.")
            return
        if "--reset-products" in sys.argv:
            from models import CartItem, OrderItem, Review, WishlistItem
            Review.query.delete()
            OrderItem.query.delete()
            CartItem.query.delete()
            WishlistItem.query.delete()
            Product.query.delete()
            db.session.commit()
            print("Cleared existing products and product-linked records.")
        categories = {}
        brands = {}
        for category_name, brand_names in CATEGORY_DATA.items():
            category = Category.query.filter_by(slug=slugify(category_name)).first()
            if not category:
                category = Category(name=category_name, slug=slugify(category_name), description=f"The ShopSphere {category_name.lower()} edit.")
                db.session.add(category)
            categories[category_name] = category
            for brand_name in brand_names:
                if brand_name not in brands:
                    brand = Brand.query.filter_by(slug=slugify(brand_name)).first()
                    if not brand:
                        brand = Brand(name=brand_name, slug=slugify(brand_name), description=f"{brand_name} selected by ShopSphere.")
                        db.session.add(brand)
                    brands[brand_name] = brand
        db.session.flush()
        products = []
        for category_name, brand_names in CATEGORY_DATA.items():
            for index in range(26):
                brand_name = brand_names[index % len(brand_names)]
                product = build_product(category_name, brand_name, index + list(CATEGORY_DATA).index(category_name) * 26)
                product.category_id = categories[category_name].id
                product.brand_id = brands[brand_name].id
                product.created_at = datetime.now(timezone.utc) - timedelta(days=index)
                products.append(product)
        db.session.add_all(products)
        db.session.commit()
        print(f"Seeded {len(categories)} categories, {len(brands)} brands, and {len(products)} products.")


if __name__ == "__main__":
    seed()
