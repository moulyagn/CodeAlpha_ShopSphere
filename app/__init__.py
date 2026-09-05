from flask import Flask, abort, flash, redirect, render_template, request, url_for
from config import Config
from extensions import csrf, db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth import auth_bp
    from app.catalog import catalog_bp
    from app.cart import cart_bp
    from app.wishlist import wishlist_bp
    from app.orders import orders_bp
    from app.profile import profile_bp
    from app.search import search_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def index():
        from models import Brand, Category, Product, Review
        return render_template("index.html", showcase=Product.query.filter_by(is_active=True).order_by(Product.rating.desc()).limit(6).all(), brands=Brand.query.order_by(Brand.name).limit(10).all(), categories=Category.query.order_by(Category.name).all(), deals=Product.query.filter(Product.is_active.is_(True), Product.discount >= 30).order_by(Product.discount.desc()).limit(6).all(), best_sellers=Product.query.filter_by(is_active=True).order_by(Product.views.desc()).limit(6).all(), reviews=Review.query.order_by(Review.likes.desc()).limit(3).all())

    @app.post("/newsletter")
    def newsletter():
        if request.form.get("email"):
            flash("You are on the ShopSphere list. Watch your inbox for the next considered edit.", "success")
        return redirect(url_for("index"))

    @app.get("/media/product/<int:product_id>/<int:view>")
    def product_image(product_id, view):
        from models import Product
        product = db.session.get(Product, product_id)
        if not product:
            abort(404)
        images = product.image_list
        if not images:
            abort(404)
        return redirect(images[view % len(images)])

    return app
