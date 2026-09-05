from flask import jsonify, render_template, request, session
from sqlalchemy import or_

from app.search import search_bp
from extensions import db
from models import Brand, Category, Product


@search_bp.get("/")
def search():
	term = request.args.get("q", "").strip()
	query = Product.query.filter_by(is_active=True)
	if term:
		pattern = f"%{term}%"
		query = query.join(Product.brand, isouter=True).join(Product.category, isouter=True).filter(or_(Product.title.ilike(pattern), Product.name.ilike(pattern), Product.description.ilike(pattern), Brand.name.ilike(pattern), Category.name.ilike(pattern)))
		recent = session.get("recent_searches", [])
		session["recent_searches"] = [term] + [item for item in recent if item.lower() != term.lower()]
		session["recent_searches"] = session["recent_searches"][:6]
	pagination = db.paginate(query.order_by(Product.views.desc(), Product.rating.desc()), page=request.args.get("page", 1, type=int), per_page=24, error_out=False)
	popular = ["iphone", "Nike", "laptop", "gold", "wireless"]
	return render_template("search/results.html", products=pagination.items, pagination=pagination, term=term, recent=session.get("recent_searches", []), popular=popular)


@search_bp.get("/suggest")
def suggest():
	term = request.args.get("q", "").strip()
	if len(term) < 2:
		return jsonify([])
	pattern = f"%{term}%"
	products = Product.query.filter(or_(Product.title.ilike(pattern), Product.name.ilike(pattern))).limit(6).all()
	brands = Brand.query.filter(Brand.name.ilike(pattern)).limit(4).all()
	categories = Category.query.filter(Category.name.ilike(pattern)).limit(4).all()
	return jsonify([{"label": product.title or product.name, "url": f"/catalog/product/{product.slug}", "type": "product"} for product in products] + [{"label": brand.name, "url": f"/catalog/brand/{brand.slug}", "type": "brand"} for brand in brands] + [{"label": category.name, "url": f"/catalog/category/{category.slug}", "type": "category"} for category in categories])
