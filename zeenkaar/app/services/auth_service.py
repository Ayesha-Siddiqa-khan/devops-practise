from app.extensions import db
from app.models.user import User


def register_user(full_name: str, email: str, password: str):
    normalized_email = email.strip().lower()
    if User.query.filter_by(email=normalized_email).first():
        return None, "Email already exists"

    user = User(full_name=full_name.strip(), email=normalized_email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None


def authenticate_user(email: str, password: str):
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not user.check_password(password):
        return None
    return user
