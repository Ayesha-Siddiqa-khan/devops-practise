from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem


def create_order_from_cart(user_id: int, cart_rows: list, total_amount, payment_ref: str):
    existing = Order.query.filter_by(payment_ref=payment_ref).first()
    if existing:
        return existing

    order = Order(user_id=user_id, total_amount=total_amount, payment_ref=payment_ref)
    db.session.add(order)
    db.session.flush()

    for row in cart_rows:
        product = row["product"]
        quantity = row["quantity"]
        line_total = row["line_total"]

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
            line_total=line_total,
        )
        db.session.add(order_item)

    db.session.commit()
    return order
