from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.auth import auth_bp
from extensions import db
from forms import ForgotPasswordForm, LoginForm, RegistrationForm
from models import User


def _safe_next_url(target):
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.netloc or parsed.scheme:
        return None
    return target


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Your ShopSphere account is ready. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.first_name}.", "success")
            return redirect(_safe_next_url(request.args.get("next")) or url_for("profile.dashboard"))
        flash("We could not match those credentials.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash("If that email is registered, a reset link has been sent. (Mock email for Phase 1.)", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)
