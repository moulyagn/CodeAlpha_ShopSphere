from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.wishlist import wishlist_bp
from extensions import db
from models import CartItem, Product, WishlistItem


@wishlist_bp.get("/")
@login_required
def view():
	items = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.created_at.desc()).all()
	return render_template("wishlist/view.html", items=items)


@wishlist_bp.post("/add/<int:product_id>")
@login_required
def add(product_id):
	product = Product.query.get_or_404(product_id)
	if not WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first():
		db.session.add(WishlistItem(user=current_user, product=product))
		db.session.commit()
		flash("Saved to your wishlist.", "success")
	return redirect(request.form.get("next") or url_for("wishlist.view"))


@wishlist_bp.post("/remove/<int:item_id>")
@login_required
def remove(item_id):
	item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
	db.session.delete(item)
	db.session.commit()
	return redirect(url_for("wishlist.view"))


@wishlist_bp.post("/move-to-cart/<int:item_id>")
@login_required
def move_to_cart(item_id):
	item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
	from app.cart.routes import _get_cart
	cart = _get_cart()
	cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=item.product_id).first()
	if cart_item:
		cart_item.quantity += 1
	else:
		db.session.add(CartItem(cart=cart, product=item.product, quantity=1))
	db.session.delete(item)
	db.session.commit()
	flash("Moved to your bag.", "success")
	return redirect(url_for("wishlist.view"))
