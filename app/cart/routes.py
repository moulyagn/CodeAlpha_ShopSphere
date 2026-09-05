from decimal import Decimal

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.cart import cart_bp
from extensions import db
from models import Cart, CartItem, Product


def _get_cart():
	if current_user.cart is None:
		current_user.cart = Cart(user_id=current_user.id)
		db.session.add(current_user.cart)
		db.session.flush()
	return current_user.cart


@cart_bp.get("/")
@login_required
def view():
	cart = _get_cart()
	subtotal = Decimal(str(cart.subtotal))
	shipping = Decimal("0") if subtotal >= Decimal("1999") or not cart.items else Decimal("99")
	gst = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
	coupon = request.args.get("coupon", "").strip().upper()
	discount = Decimal("0")
	if coupon == "WELCOME10":
		discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
	return render_template("cart/view.html", cart=cart, subtotal=subtotal, shipping=shipping, gst=gst, discount=discount, coupon=coupon, grand_total=subtotal + shipping + gst - discount)


@cart_bp.post("/add/<int:product_id>")
@login_required
def add(product_id):
	product = Product.query.get_or_404(product_id)
	cart = _get_cart()
	item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
	requested = max(1, request.form.get("quantity", 1, type=int))
	if item:
		item.quantity = min(item.quantity + requested, product.stock or item.quantity + requested)
	else:
		db.session.add(CartItem(cart=cart, product=product, quantity=min(requested, product.stock or requested)))
	db.session.commit()
	flash(f"{product.title or product.name} added to your bag.", "success")
	return redirect(request.form.get("next") or url_for("cart.view"))


@cart_bp.post("/update/<int:item_id>")
@login_required
def update(item_id):
	item = CartItem.query.filter_by(id=item_id, cart_id=_get_cart().id).first_or_404()
	quantity = request.form.get("quantity", 1, type=int)
	if quantity <= 0:
		db.session.delete(item)
	else:
		item.quantity = min(quantity, item.product.stock or quantity)
	db.session.commit()
	return redirect(url_for("cart.view"))


@cart_bp.post("/remove/<int:item_id>")
@login_required
def remove(item_id):
	item = CartItem.query.filter_by(id=item_id, cart_id=_get_cart().id).first_or_404()
	db.session.delete(item)
	db.session.commit()
	return redirect(url_for("cart.view"))


@cart_bp.post("/move-to-wishlist/<int:item_id>")
@login_required
def move_to_wishlist(item_id):
	from models import WishlistItem
	item = CartItem.query.filter_by(id=item_id, cart_id=_get_cart().id).first_or_404()
	if not WishlistItem.query.filter_by(user_id=current_user.id, product_id=item.product_id).first():
		db.session.add(WishlistItem(user=current_user, product=item.product))
	db.session.delete(item)
	db.session.commit()
	flash("Moved to your wishlist.", "success")
	return redirect(url_for("cart.view"))
