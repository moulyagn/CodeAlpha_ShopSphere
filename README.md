# ShopSphere

ShopSphere is a luxury Indian e-commerce platform built with Flask, SQLAlchemy, Flask-Migrate, Flask-WTF, Flask-Login, Jinja2, Bootstrap 5, vanilla JavaScript, and SQLite. The completed Phase 1-4 implementation includes the public storefront, seeded catalog, checkout, mock payments, orders, reviews, customer dashboard, and protected admin console.

## Run locally

```powershell
pip install -r requirements.txt
flask db upgrade
python run.py
```

After applying migrations, run `python seed.py` once to load the 520-product catalog when starting with an empty database. Existing seeded databases are detected and left unchanged.

Open `http://127.0.0.1:5000` in a browser. Set `SECRET_KEY` and `DATABASE_URL` environment variables for non-development deployments.

## Database migrations

The project uses Flask-Migrate and SQLAlchemy. For a schema change:

```powershell
flask db migrate -m "describe the change"
flask db upgrade
```

A new environment can initialize migration metadata with `flask db init` before its first migration. The checked-in migration chain applies Phases 1-4 with `flask db upgrade`.

## Admin access

Open `/admin/login`. Development defaults are `admin@shopsphere.local` and `ShopSphereAdmin!2026`. Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables before running in any shared or deployed environment. The first successful configured login creates the administrator account with a hashed password and `is_admin` role. Admin sessions are separate from storefront access and all mutation routes require authentication, role checks, and CSRF protection.

## Structure

- `app/`: Flask Blueprints for auth, catalog, cart, wishlist, orders, admin, profile, and search
- `models.py`: catalog, customer, cart, order, payment, coupon, review, notification, and saved-card models
- `templates/`: storefront, checkout, invoices, account, dashboard, and admin views
- `static/`: reusable luxury theme CSS, JavaScript, logo, uploads, and admin analytics chart code
- `config.py`, `extensions.py`, `run.py`: application configuration, extensions, and entry point

## Implemented features

- Black/gold luxury responsive storefront with animated globe-to-cart intro, product showcases, categories, brands, flash sale, best sellers, reviews, statistics, newsletter, social/legal footer, and ₹ currency throughout
- 520 seeded products across 20 categories with search, filters, sorting, pagination, galleries, zoom, related products, wishlist, and cart
- Registration, login, Remember Me, hashed passwords, profile dashboard, profile pictures, address book, notifications, mock saved cards, and order history
- Checkout with Indian addresses/PIN codes, Standard or Express shipping, GST, coupons, UPI, COD, debit card, credit card, and net banking mock payments
- Immutable order snapshots, invoice pages, order tracking statuses, cancellation, stock updates, verified-purchase reviews, and review likes
- Admin login and role check, dashboard metrics, revenue chart, traffic/order/product stats, product CRUD, category/brand management, user management, order status updates, and coupon management

Real payment gateways, shipment integrations, and production email delivery are intentionally outside this phase. Payment records are explicitly mock-only.
