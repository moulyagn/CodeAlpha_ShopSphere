from flask import Blueprint

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")

from app.wishlist import routes  # noqa: E402,F401
