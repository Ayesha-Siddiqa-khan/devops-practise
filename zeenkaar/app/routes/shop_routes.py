from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.cart_service import add_to_cart, clear_cart, get_cart_details, remove_from_cart
from app.services.order_service import create_order_from_cart
from app.services.payment_service import PaymentError, create_checkout_session, fetch_checkout_session
from app.services.product_service import get_product, list_products

shop_bp = Blueprint("shop", __name__)


@shop_bp.get("/")
def home():
    return redirect(url_for("shop.products"))


@shop_bp.get("/products")
def products():
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    items = list_products(search=q, category_slug=category)
    return render_template("shop/products.html", products=items, q=q, selected_category=category)


@shop_bp.get("/products/<int:product_id>")
def product_detail(product_id: int):
    product = get_product(product_id)
    return render_template("shop/product_detail.html", product=product)


@shop_bp.post("/cart/add/<int:product_id>")
@login_required
def cart_add(product_id: int):
    quantity = int(request.form.get("quantity", "1"))
    add_to_cart(current_user.id, product_id, quantity)
    flash("Item added to cart.", "success")
    return redirect(request.referrer or url_for("shop.products"))


@shop_bp.get("/cart")
@login_required
def cart_view():
    rows, total = get_cart_details(current_user.id)
    return render_template("shop/cart.html", cart_rows=rows, total=total)


@shop_bp.post("/cart/remove/<int:item_id>")
@login_required
def cart_remove(item_id: int):
    remove_from_cart(current_user.id, item_id)
    flash("Item removed from cart.", "info")
    return redirect(url_for("shop.cart_view"))


@shop_bp.post("/checkout")
@login_required
def checkout():
    rows, _total = get_cart_details(current_user.id)
    success_url = url_for("shop.checkout_success", _external=True)
    cancel_url = url_for("shop.checkout_cancel", _external=True)

    try:
        session = create_checkout_session(current_user.id, rows, success_url, cancel_url)
    except PaymentError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("shop.cart_view"))

    return redirect(session.url, code=303)


@shop_bp.get("/checkout/success")
@login_required
def checkout_success():
    session_id = request.args.get("session_id", "")
    if not session_id:
        flash("Missing checkout session id.", "danger")
        return redirect(url_for("shop.cart_view"))

    try:
        session = fetch_checkout_session(session_id)
    except PaymentError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("shop.cart_view"))

    if session.payment_status != "paid":
        flash("Payment not completed.", "danger")
        return redirect(url_for("shop.cart_view"))

    rows, total = get_cart_details(current_user.id)
    if not rows:
        flash("Cart already cleared.", "info")
        return redirect(url_for("auth.orders"))

    create_order_from_cart(current_user.id, rows, total, payment_ref=session.id)
    clear_cart(current_user.id)
    flash("Payment successful. Order placed.", "success")
    return redirect(url_for("auth.orders"))


@shop_bp.get("/checkout/cancel")
@login_required
def checkout_cancel():
    flash("Payment canceled.", "warning")
    return redirect(url_for("shop.cart_view"))
