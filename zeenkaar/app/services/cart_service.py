from decimal import Decimal

from app.extensions import db
from app.models.cart_item import CartItem
from app.models.product import Product


def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    product = Product.query.get_or_404(product_id)
    quantity = max(1, quantity)

    item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product.id, quantity=quantity)
        db.session.add(item)

    db.session.commit()


def remove_from_cart(user_id: int, cart_item_id: int):
    item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()


def get_cart_details(user_id: int):
    items = CartItem.query.filter_by(user_id=user_id).all()
    total = Decimal("0.00")

    detail_rows = []
    for item in items:
        if not item.product:
            continue
        line_total = item.product.price * item.quantity
        total += line_total
        detail_rows.append(
            {
                "id": item.id,
                "product": item.product,
                "quantity": item.quantity,
                "line_total": line_total,
            }
        )

    return detail_rows, total


def clear_cart(user_id: int):
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
