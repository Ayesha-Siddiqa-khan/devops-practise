from flask import Flask

from app.config import Config
from app.extensions import bcrypt, db, login_manager, migrate
from app.models import category, cart_item, order, order_item, product, user  # noqa: F401
from app.models.category import Category
from app.models.cart_item import CartItem
from app.routes.auth_routes import auth_bp
from app.routes.shop_routes import shop_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)

    @app.context_processor
    def inject_common_data():
        categories = Category.query.order_by(Category.name.asc()).all()
        cart_count = 0
        from flask_login import current_user

        if current_user.is_authenticated:
            cart_count = (
                db.session.query(db.func.coalesce(db.func.sum(CartItem.quantity), 0))
                .filter(CartItem.user_id == current_user.id)
                .scalar()
            )

        return {
            "menu_categories": categories,
            "menu_cart_count": int(cart_count or 0),
            "stripe_publishable_key": app.config["STRIPE_PUBLISHABLE_KEY"],
        }

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "zeenkaar-web"}, 200

    return app
