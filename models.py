from datetime import datetime, timezone
import json

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    profile_picture = db.Column(db.String(255))
    addresses = db.relationship("Address", back_populates="user", cascade="all, delete-orphan")
    cart = db.relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wishlist_items = db.relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    saved_cards = db.relationship("SavedCard", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship("Product", back_populates="category")


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship("Product", back_populates="brand")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    mrp = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount = db.Column(db.Integer, nullable=False, default=0)
    specs = db.Column(db.Text, nullable=False, default="{}")
    stock = db.Column(db.Integer, nullable=False, default=0)
    delivery_estimate = db.Column(db.String(120), nullable=False, default="Delivery in 3-5 days")
    rating = db.Column(db.Numeric(2, 1), nullable=False, default=4.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)
    seller = db.Column(db.String(160), nullable=False, default="ShopSphere Select")
    features = db.Column(db.Text, nullable=False, default="[]")
    image_urls = db.Column(db.Text, nullable=False, default="[]")
    primary_image = db.Column(db.String(500), nullable=False, default="")
    images = db.Column(db.Text, nullable=False, default="[]")
    views = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"))
    category = db.relationship("Category", back_populates="products")
    brand = db.relationship("Brand", back_populates="products")
    cart_items = db.relationship("CartItem", back_populates="product")
    wishlist_items = db.relationship("WishlistItem", back_populates="product")
    order_items = db.relationship("OrderItem", back_populates="product")
    reviews = db.relationship("Review", back_populates="product", cascade="all, delete-orphan")

    @property
    def display_title(self):
        return self.title or self.name

    @property
    def spec_map(self):
        return json.loads(self.specs or "{}")

    @property
    def feature_list(self):
        return json.loads(self.features or "[]")

    @property
    def image_list(self):
        stored_images = json.loads(self.images or "[]")
        if stored_images:
            return stored_images
        return json.loads(self.image_urls or "[]")


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    label = db.Column(db.String(80), nullable=False, default="Home")
    line_one = db.Column(db.String(255), nullable=False)
    line_two = db.Column(db.String(255))
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(80), nullable=False, default="India")
    phone = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship("User", back_populates="addresses")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(24), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    shipping_method = db.Column(db.String(40), nullable=False, default="Standard")
    payment_method = db.Column(db.String(30), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    address_snapshot = db.Column(db.Text, nullable=False, default="{}")
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    shipping = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    gst = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = db.relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")

    @property
    def address(self):
        return json.loads(self.address_snapshot or "{}")


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="cart")
    items = db.relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items), 0)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cart = db.relationship("Cart", back_populates="items")
    product = db.relationship("Product", back_populates="cart_items")
    __table_args__ = (db.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)

    @property
    def line_total(self):
        return self.product.price * self.quantity


class Wishlist(db.Model):
    __abstract__ = True


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="wishlist_items")
    product = db.relationship("Product", back_populates="wishlist_items")
    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_wishlist_product"),)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    product_title = db.Column(db.String(200), nullable=False)
    product_slug = db.Column(db.String(220), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    gst_rate = db.Column(db.Numeric(4, 2), nullable=False, default=18)
    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
    review = db.relationship("Review", back_populates="order_item", uselist=False)

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), unique=True, nullable=False)
    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    transaction_reference = db.Column(db.String(80), unique=True, nullable=False)
    masked_details = db.Column(db.String(80))
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    is_mock = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    order = db.relationship("Order", back_populates="payment")


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    max_discount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    expires_at = db.Column(db.DateTime)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey("order_item.id"), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
    order_item = db.relationship("OrderItem", back_populates="review")


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(40), nullable=False, default="general")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user = db.relationship("User", back_populates="notifications")


class SavedCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    cardholder_name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(30), nullable=False, default="Card")
    last_four = db.Column(db.String(4), nullable=False)
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", back_populates="saved_cards")


