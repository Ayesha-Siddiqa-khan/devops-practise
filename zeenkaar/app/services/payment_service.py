import stripe
from flask import current_app


class PaymentError(Exception):
    pass


def _configure_stripe():
    secret_key = current_app.config.get("STRIPE_SECRET_KEY", "")
    if not secret_key:
        raise PaymentError("Stripe secret key is missing")
    stripe.api_key = secret_key


def create_checkout_session(user_id: int, cart_rows: list, success_url: str, cancel_url: str):
    _configure_stripe()

    if not cart_rows:
        raise PaymentError("Cart is empty")

    line_items = []
    for row in cart_rows:
        product = row["product"]
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product.name,
                        "description": product.description[:200],
                    },
                    "unit_amount": int(float(product.price) * 100),
                },
                "quantity": row["quantity"],
            }
        )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        client_reference_id=str(user_id),
    )
    return session


def fetch_checkout_session(session_id: str):
    _configure_stripe()
    return stripe.checkout.Session.retrieve(session_id)
