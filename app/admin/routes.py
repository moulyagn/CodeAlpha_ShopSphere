from functools import wraps

from flask import abort, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app.admin import admin_bp
from extensions import db
from models import Brand, Category, Coupon, Order, Product, Review, User


def admin_required(view):
	@wraps(view)
	def wrapped(*args, **kwargs):
		if not session.get("admin_authenticated") or not current_user.is_authenticated or not current_user.is_admin:
			return redirect(url_for("admin.login", next=request.path))
		return view(*args, **kwargs)
	return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		if email == current_app.config["ADMIN_EMAIL"] and password == current_app.config["ADMIN_PASSWORD"]:
			user = User.query.filter_by(email=email).first()
			if not user:
				user = User(first_name="ShopSphere", last_name="Admin", email=email, password_hash=generate_password_hash(password), is_admin=True)
				db.session.add(user)
			user.is_admin = True
			db.session.commit()
			login_user(user)
			session["admin_authenticated"] = True
			return redirect(request.args.get("next") or url_for("admin.dashboard"))
		flash("Admin credentials were not accepted.", "danger")
	return render_template("admin/login.html")


@admin_bp.get("/logout")
def logout():
	session.pop("admin_authenticated", None)
	logout_user()
	return redirect(url_for("admin.login"))


@admin_bp.get("/")
@admin_required
def dashboard():
	revenue = db.session.scalar(db.select(func.coalesce(func.sum(Order.total), 0)).where(Order.payment_status.in_(["Paid", "Pending"]), Order.status != "Cancelled")) or 0
	monthly = db.session.execute(db.select(func.strftime("%Y-%m", Order.created_at), func.count(Order.id), func.coalesce(func.sum(Order.total), 0)).group_by(func.strftime("%Y-%m", Order.created_at)).order_by(func.strftime("%Y-%m", Order.created_at))).all()
	return render_template("admin/dashboard.html", users=User.query.count(), products=Product.query.count(), orders=Order.query.count(), reviews=Review.query.count(), revenue=revenue, low_stock=Product.query.filter(Product.stock < 10, Product.is_active.is_(True)).order_by(Product.stock).limit(8).all(), recent_orders=Order.query.order_by(Order.created_at.desc()).limit(8).all(), chart_labels=[row[0] for row in monthly], chart_orders=[row[1] for row in monthly], chart_revenue=[float(row[2]) for row in monthly])


@admin_bp.route("/products", methods=["GET", "POST"])
@admin_required
def products():
	if request.method == "POST":
		category = db.session.get(Category, request.form.get("category_id", type=int))
		brand = db.session.get(Brand, request.form.get("brand_id", type=int))
		title = request.form.get("title", "").strip()
		if title and category and brand:
			product = Product(title=title, name=title, slug=f"{title.lower().replace(' ', '-')}-{Product.query.count()+1}", description=request.form.get("description", ""), price=request.form.get("price", 0, type=float), mrp=request.form.get("mrp", 0, type=float), discount=request.form.get("discount", 0, type=int), stock=request.form.get("stock", 0, type=int), category=category, brand=brand, image_urls='["https://placehold.co/900x900/0f0f0f/d4af37?text=ShopSphere"]', specs="{}", features="[]")
			db.session.add(product)
			db.session.commit()
			flash("Product created.", "success")
	return render_template("admin/products.html", products=Product.query.order_by(Product.created_at.desc()).all(), categories=Category.query.order_by(Category.name).all(), brands=Brand.query.order_by(Brand.name).all())


@admin_bp.post("/products/<int:product_id>/delete")
@admin_required
def delete_product(product_id):
	product = db.session.get(Product, product_id) or abort(404)
	product.is_active = False
	db.session.commit()
	return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
	product = db.session.get(Product, product_id) or abort(404)
	if request.method == "POST":
		product.title = request.form.get("title", product.title).strip()
		product.name = product.title
		product.price = request.form.get("price", product.price, type=float)
		product.mrp = request.form.get("mrp", product.mrp, type=float)
		product.discount = request.form.get("discount", product.discount, type=int)
		product.stock = request.form.get("stock", product.stock, type=int)
		product.description = request.form.get("description", product.description)
		db.session.commit()
		flash("Product updated.", "success")
		return redirect(url_for("admin.products"))
	return render_template("admin/product_edit.html", product=product)


@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
	name = request.form.get("name", "").strip() if request.method == "POST" else ""
	if name:
		db.session.add(Category(name=name, slug=name.lower().replace(" ", "-"), description=request.form.get("description", "")))
		db.session.commit()
		return redirect(url_for("admin.categories"))
	return render_template("admin/taxonomy.html", title="categories", records=Category.query.order_by(Category.name).all(), endpoint="admin.categories")


@admin_bp.route("/brands", methods=["GET", "POST"])
@admin_required
def brands():
	name = request.form.get("name", "").strip() if request.method == "POST" else ""
	if name:
		db.session.add(Brand(name=name, slug=name.lower().replace(" ", "-"), description=request.form.get("description", "")))
		db.session.commit()
		return redirect(url_for("admin.brands"))
	return render_template("admin/taxonomy.html", title="brands", records=Brand.query.order_by(Brand.name).all(), endpoint="admin.brands")


@admin_bp.get("/users")
@admin_required
def users():
	return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@admin_bp.post("/users/<int:user_id>/toggle")
@admin_required
def toggle_user(user_id):
	user = db.session.get(User, user_id) or abort(404)
	user.is_active = not user.is_active
	db.session.commit()
	return redirect(url_for("admin.users"))


@admin_bp.get("/orders")
@admin_required
def orders():
	return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())


@admin_bp.post("/orders/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
	order = db.session.get(Order, order_id) or abort(404)
	order.status = request.form.get("status", order.status)
	db.session.commit()
	return redirect(url_for("admin.orders"))


@admin_bp.route("/coupons", methods=["GET", "POST"])
@admin_required
def coupons():
	if request.method == "POST":
		code = request.form.get("code", "").strip().upper()
		if code:
			db.session.add(Coupon(code=code, discount_percent=request.form.get("discount_percent", 10, type=int), max_discount=request.form.get("max_discount", 500, type=float)))
			db.session.commit()
	return render_template("admin/coupons.html", coupons=Coupon.query.order_by(Coupon.id.desc()).all())
