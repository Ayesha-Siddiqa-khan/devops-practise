from sqlalchemy import or_

from app.models.category import Category
from app.models.product import Product


def list_products(search: str = "", category_slug: str = ""):
    query = Product.query.join(Category)

    if search:
        like_term = f"%{search.strip()}%"
        query = query.filter(
            or_(Product.name.ilike(like_term), Product.description.ilike(like_term))
        )

    if category_slug:
        query = query.filter(Category.slug == category_slug)

    return query.order_by(Product.id.desc()).all()


def get_product(product_id: int):
    return Product.query.get_or_404(product_id)
