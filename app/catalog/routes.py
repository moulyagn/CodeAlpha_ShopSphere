from flask import abort, render_template, request
from sqlalchemy import or_

from app.catalog import catalog_bp
from extensions import db
from models import Brand, Category, Product


def _listing_query(args=None):
	args = args or request.args
	query = Product.query.filter_by(is_active=True)
	category = args.get("category", "").strip().lower()
	brand = args.get("brand", "").strip().lower()
	if category:
		query = query.join(Product.category).filter(or_(Category.slug == category, Category.name.ilike(category)))
	if brand:
		query = query.join(Product.brand).filter(or_(Brand.slug == brand, Brand.name.ilike(brand)))
	if args.get("min_price"):
		query = query.filter(Product.price >= float(args["min_price"]))
	if args.get("max_price"):
		query = query.filter(Product.price <= float(args["max_price"]))
	if args.get("rating"):
		query = query.filter(Product.rating >= float(args["rating"]))
	if args.get("discount"):
		query = query.filter(Product.discount >= int(args["discount"]))
	if args.get("availability") == "in-stock":
		query = query.filter(Product.stock > 0)
	sort = args.get("sort", "newest")
	sort_map = {"price-low": Product.price.asc(), "price-high": Product.price.desc(), "rating": Product.rating.desc(), "popularity": Product.views.desc(), "discount": Product.discount.desc(), "newest": Product.created_at.desc()}
	return query.order_by(sort_map.get(sort, Product.created_at.desc())), sort


@catalog_bp.get("/")
def listing():
	query, sort = _listing_query()
	pagination = db.paginate(query, page=request.args.get("page", 1, type=int), per_page=24, error_out=False)
	return render_template("catalog/listing.html", products=pagination.items, pagination=pagination, categories=Category.query.order_by(Category.name).all(), brands=Brand.query.order_by(Brand.name).all(), sort=sort, filters=request.args)


@catalog_bp.get("/category/<slug>")
def category_listing(slug):
	category = Category.query.filter_by(slug=slug).first_or_404()
	return listing_with_filter(category=category.slug)


@catalog_bp.get("/brand/<slug>")
def brand_listing(slug):
	brand = Brand.query.filter_by(slug=slug).first_or_404()
	return listing_with_filter(brand=brand.slug)


def listing_with_filter(**values):
	args = request.args.to_dict()
	args.update(values)
	query, sort = _listing_query(args)
	pagination = db.paginate(query, page=int(args.get("page", 1)), per_page=24, error_out=False)
	return render_template("catalog/listing.html", products=pagination.items, pagination=pagination, categories=Category.query.order_by(Category.name).all(), brands=Brand.query.order_by(Brand.name).all(), sort=sort, filters=args)


@catalog_bp.get("/product/<slug>")
def detail(slug):
	product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
	product.views += 1
	db.session.commit()
	related = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.is_active.is_(True)).order_by(Product.rating.desc()).limit(4).all()
	bundle = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.is_active.is_(True)).order_by(Product.views.desc()).limit(2).all()
	return render_template("catalog/detail.html", product=product, related=related, bundle=bundle)
