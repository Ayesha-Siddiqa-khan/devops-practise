from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models.order import Order
from app.services.auth_service import authenticate_user, register_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("shop.products"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        if len(full_name.strip()) < 2 or len(password) < 8:
            flash("Use valid name and minimum 8-char password.", "danger")
            return render_template("auth/register.html")

        user, error = register_user(full_name, email, password)
        if error:
            flash(error, "danger")
            return render_template("auth/register.html")

        login_user(user)
        flash("Registration successful.", "success")
        return redirect(url_for("shop.products"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.products"))

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = authenticate_user(email, password)
        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        flash("Welcome back.", "success")
        return redirect(url_for("shop.products"))

    return render_template("auth/login.html")


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("shop.products"))


@auth_bp.get("/orders")
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template("shop/orders.html", orders=user_orders)
