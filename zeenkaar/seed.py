from app import create_app
from app.extensions import db
from app.models.category import Category
from app.models.product import Product

app = create_app()

SEED_DATA = {
    "Skincare": [
        {
            "name": "Hydra Glow Serum",
            "description": "Hydrating serum for bright and soft skin.",
            "price": 29.99,
            "image_url": "https://images.pexels.com/photos/4465831/pexels-photo-4465831.jpeg",
            "stock": 50,
        },
        {
            "name": "Aloe Calm Gel",
            "description": "Cooling gel moisturizer with aloe extract.",
            "price": 19.99,
            "image_url": "https://images.pexels.com/photos/3735657/pexels-photo-3735657.jpeg",
            "stock": 40,
        },
    ],
    "Makeup": [
        {
            "name": "Velvet Matte Lipstick",
            "description": "Rich matte finish lipstick with long wear.",
            "price": 14.99,
            "image_url": "https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg",
            "stock": 60,
        },
        {
            "name": "Silk Touch Foundation",
            "description": "Lightweight foundation with natural coverage.",
            "price": 24.99,
            "image_url": "https://images.pexels.com/photos/3762874/pexels-photo-3762874.jpeg",
            "stock": 35,
        },
    ],
    "Fragrance": [
        {
            "name": "Floral Mist Perfume",
            "description": "Elegant floral notes for daily wear.",
            "price": 39.99,
            "image_url": "https://images.pexels.com/photos/965989/pexels-photo-965989.jpeg",
            "stock": 25,
        }
    ],
}


def slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "-")


def seed():
    with app.app_context():
        for category_name, products in SEED_DATA.items():
            slug = slugify(category_name)
            category = Category.query.filter_by(slug=slug).first()
            if not category:
                category = Category(name=category_name, slug=slug)
                db.session.add(category)
                db.session.flush()

            for item in products:
                existing = Product.query.filter_by(name=item["name"]).first()
                if not existing:
                    db.session.add(Product(category_id=category.id, **item))

        db.session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
