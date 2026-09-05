import os
from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.profile import profile_bp
from extensions import db
from forms import AddressForm, ProfileForm
from models import Address, Notification, Order, Product, SavedCard


@profile_bp.get("/")
@login_required
def dashboard():
	recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(4).all()
	wishlist = current_user.wishlist_items[:4]
	recent_products = Product.query.filter_by(is_active=True).order_by(Product.views.desc()).limit(4).all()
	deals = Product.query.filter(Product.is_active.is_(True), Product.discount >= 30).order_by(Product.discount.desc()).limit(4).all()
	recommended = Product.query.filter_by(is_active=True).order_by(Product.rating.desc()).limit(4).all()
	unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
	return render_template("profile/dashboard.html", recent_orders=recent_orders, wishlist=wishlist, recent_products=recent_products, deals=deals, recommended=recommended, unread_count=unread_count)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
	form = ProfileForm(obj=current_user)
	if form.validate_on_submit():
		current_user.first_name = form.first_name.data.strip()
		current_user.last_name = form.last_name.data.strip()
		current_user.email = form.email.data.strip().lower()
		picture = request.files.get("profile_picture")
		if picture and picture.filename:
			filename = secure_filename(picture.filename)
			upload_dir = os.path.join(current_app.static_folder, "uploads")
			os.makedirs(upload_dir, exist_ok=True)
			picture.save(os.path.join(upload_dir, filename))
			current_user.profile_picture = f"uploads/{filename}"
		db.session.commit()
		flash("Your profile has been updated.", "success")
		return redirect(url_for("profile.dashboard"))
	return render_template("profile/edit.html", form=form)


@profile_bp.route("/addresses", methods=["GET", "POST"])
@login_required
def addresses():
	form = AddressForm()
	if form.validate_on_submit():
		if form.is_default.data:
			Address.query.filter_by(user_id=current_user.id).update({"is_default": False})
		address = Address(user_id=current_user.id, label=form.label.data.strip(), line_one=form.line_one.data.strip(), line_two=form.line_two.data.strip(), city=form.city.data.strip(), state=form.state.data.strip(), postal_code=form.postal_code.data.strip(), phone=form.phone.data.strip(), is_default=form.is_default.data or not Address.query.filter_by(user_id=current_user.id).first())
		db.session.add(address)
		db.session.commit()
		flash("Address saved.", "success")
		return redirect(url_for("profile.addresses"))
	return render_template("profile/addresses.html", form=form, addresses=Address.query.filter_by(user_id=current_user.id).order_by(Address.is_default.desc(), Address.id.desc()).all())


@profile_bp.post("/addresses/<int:address_id>/delete")
@login_required
def delete_address(address_id):
	address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
	db.session.delete(address)
	db.session.commit()
	return redirect(url_for("profile.addresses"))


@profile_bp.get("/notifications")
@login_required
def notifications():
	items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
	for item in items:
		item.is_read = True
	db.session.commit()
	return render_template("profile/notifications.html", notifications=items)


@profile_bp.route("/saved-cards", methods=["GET", "POST"])
@login_required
def saved_cards():
	if request.method == "POST":
		digits = "".join(character for character in request.form.get("card_number", "") if character.isdigit())
		if len(digits) >= 4:
			db.session.add(SavedCard(user_id=current_user.id, cardholder_name=request.form.get("cardholder_name", current_user.first_name), brand=request.form.get("brand", "Card"), last_four=digits[-4:], expiry_month=int(request.form.get("expiry_month", 1)), expiry_year=int(request.form.get("expiry_year", datetime.now().year + 1))))
			db.session.commit()
			flash("Mock card saved securely as a masked reference.", "success")
	return render_template("profile/saved_cards.html", cards=SavedCard.query.filter_by(user_id=current_user.id).all())


@profile_bp.post("/saved-cards/<int:card_id>/delete")
@login_required
def delete_card(card_id):
	card = SavedCard.query.filter_by(id=card_id, user_id=current_user.id).first_or_404()
	db.session.delete(card)
	db.session.commit()
	return redirect(url_for("profile.saved_cards"))


@profile_bp.get("/orders")
@login_required
def orders():
	return redirect(url_for("orders.history"))


@profile_bp.get("/wishlist")
@login_required
def wishlist():
	return redirect(url_for("wishlist.view"))
