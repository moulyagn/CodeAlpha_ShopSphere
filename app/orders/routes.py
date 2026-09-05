import json
import secrets
from datetime import datetime, timezone
from decimal import Decimal

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.cart.routes import _get_cart
from app.orders import orders_bp
from extensions import db
from forms import CheckoutForm, ReviewForm
from models import Address, Coupon, Notification, Order, OrderItem, Payment, Review

GST_RATE = Decimal("0.18")
SHIPPING_COSTS = {"Standard": Decimal("99"), "Express": Decimal("199")}
ORDER_STATUSES = ["Pending", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled", "Returned"]


def _address_values(address):
	return {"label": address.label, "line_one": address.line_one, "line_two": address.line_two or "", "city": address.city, "state": address.state, "postal_code": address.postal_code, "country": address.country, "phone": address.phone or ""}


def _checkout_totals(cart, shipping_method="Standard", coupon_code=""):
	subtotal = Decimal(str(cart.subtotal))
	shipping = Decimal("0") if subtotal >= Decimal("1999") else SHIPPING_COSTS.get(shipping_method, SHIPPING_COSTS["Standard"])
	discount = Decimal("0")
	coupon = Coupon.query.filter_by(code=(coupon_code or "").strip().upper(), is_active=True).first() if coupon_code else None
	if not coupon and (coupon_code or "").strip().upper() == "WELCOME10":
		discount = min((subtotal * Decimal("0.10")).quantize(Decimal("0.01")), Decimal("500"))
	elif coupon:
		discount = min((subtotal * Decimal(coupon.discount_percent) / 100).quantize(Decimal("0.01")), Decimal(str(coupon.max_discount)))
	taxable = max(Decimal("0"), subtotal - discount)
	gst = (taxable * GST_RATE).quantize(Decimal("0.01"))
	return {"subtotal": subtotal, "shipping": shipping, "discount": discount, "gst": gst, "total": taxable + shipping + gst, "coupon": coupon}


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
	cart = _get_cart()
	if not cart.items:
		flash("Your bag is empty. Add something before checkout.", "info")
		return redirect(url_for("cart.view"))
	addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc(), Address.id.desc()).all()
	if not addresses:
		flash("Add a delivery address to continue.", "info")
		return redirect(url_for("profile.addresses", next="orders.checkout"))
	form = CheckoutForm()
	form.address_id.choices = [(address.id, f"{address.label} · {address.line_one}, {address.city} - {address.postal_code}") for address in addresses]
	totals = _checkout_totals(cart, form.shipping_method.data or "Standard", form.coupon_code.data or "")
	if form.validate_on_submit():
		address = Address.query.filter_by(id=form.address_id.data, user_id=current_user.id).first_or_404()
		for item in cart.items:
			if not item.product.is_active or item.product.stock < item.quantity:
				flash(f"{item.product.display_title} no longer has enough stock.", "danger")
				return redirect(url_for("cart.view"))
		totals = _checkout_totals(cart, form.shipping_method.data, form.coupon_code.data)
		order = Order(order_number=f"SS-{datetime.now(timezone.utc):%y%m%d}-{secrets.token_hex(3).upper()}", user=current_user, status="Confirmed", shipping_method=form.shipping_method.data, payment_method=form.payment_method.data, payment_status="Paid" if form.payment_method.data != "COD" else "Pending", address_snapshot=json.dumps(_address_values(address)), **{key: totals[key] for key in ("subtotal", "shipping", "discount", "gst", "total")})
		db.session.add(order)
		db.session.flush()
		masked = None
		if form.payment_method.data in {"Debit Card", "Credit Card"}:
			digits = "".join(character for character in (form.card_details.data or "") if character.isdigit())
			masked = f"•••• {digits[-4:]}" if len(digits) >= 4 else "•••• 0000"
		db.session.add(Payment(order=order, method=form.payment_method.data, status=order.payment_status, transaction_reference=f"MOCK-{secrets.token_hex(6).upper()}", masked_details=masked, amount=order.total, is_mock=True))
		for item in cart.items:
			item.product.stock -= item.quantity
			db.session.add(OrderItem(order=order, product=item.product, product_title=item.product.display_title, product_slug=item.product.slug, unit_price=item.product.price, quantity=item.quantity))
		db.session.add(Notification(user=current_user, title="Order confirmed", message=f"Your order {order.order_number} is confirmed.", kind="order"))
		cart.items.clear()
		db.session.commit()
		return redirect(url_for("orders.confirmation", order_number=order.order_number))
	return render_template("orders/checkout.html", form=form, addresses=addresses, cart=cart, totals=totals)


@orders_bp.get("/confirmation/<order_number>")
@login_required
def confirmation(order_number):
	order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
	return render_template("orders/confirmation.html", order=order)


@orders_bp.get("/invoice/<order_number>")
@login_required
def invoice(order_number):
	order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
	return render_template("orders/invoice.html", order=order)


@orders_bp.get("/")
@login_required
def history():
	orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
	return render_template("orders/history.html", orders=orders)


@orders_bp.get("/<order_number>")
@login_required
def detail(order_number):
	order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
	return render_template("orders/detail.html", order=order, statuses=ORDER_STATUSES, review_form=ReviewForm())


@orders_bp.post("/<order_number>/cancel")
@login_required
def cancel(order_number):
	order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
	if order.status in {"Pending", "Confirmed"}:
		order.status = "Cancelled"
		for item in order.items:
			item.product.stock += item.quantity
		order.payment_status = "Refund Pending" if order.payment_status == "Paid" else order.payment_status
		db.session.add(Notification(user=current_user, title="Order cancelled", message=f"Order {order.order_number} has been cancelled.", kind="order"))
		db.session.commit()
	return redirect(url_for("orders.detail", order_number=order.order_number))


@orders_bp.post("/<order_number>/advance")
@login_required
def advance(order_number):
	order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
	if order.status in ORDER_STATUSES[:4]:
		order.status = ORDER_STATUSES[ORDER_STATUSES.index(order.status) + 1]
		if order.status == "Delivered":
			db.session.add(Notification(user=current_user, title="Order delivered", message=f"Order {order.order_number} has arrived.", kind="order"))
		db.session.commit()
	return redirect(url_for("orders.detail", order_number=order.order_number))


@orders_bp.post("/review/<int:order_item_id>")
@login_required
def review(order_item_id):
	item = OrderItem.query.join(Order).filter(OrderItem.id == order_item_id, Order.user_id == current_user.id, Order.status == "Delivered").first_or_404()
	form = ReviewForm()
	if form.validate_on_submit() and not item.review:
		review_record = Review(user=current_user, product=item.product, order_item=item, rating=form.rating.data, comment=form.comment.data.strip())
		db.session.add(review_record)
		existing = Review.query.filter_by(product_id=item.product_id).all()
		item.product.rating = round((sum(review_item.rating for review_item in existing) + form.rating.data) / (len(existing) + 1), 1)
		item.product.review_count += 1
		db.session.commit()
	return redirect(url_for("orders.detail", order_number=item.order.order_number))


@orders_bp.post("/review/<int:review_id>/like")
@login_required
def like_review(review_id):
	review_record = Review.query.get_or_404(review_id)
	review_record.likes += 1
	db.session.commit()
	return redirect(request.referrer or url_for("catalog.detail", slug=review_record.product.slug))
