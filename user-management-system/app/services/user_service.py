"""
services/user_service.py

All business logic related to User objects lives here.
Route handlers call these functions — they don't touch the database directly.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieve a single user by their primary key.

    Args:
        db:      The active database session.
        user_id: The integer primary key of the user.

    Returns:
        The User ORM object, or None if no user with that ID exists.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a single user by their email address.

    Used during registration (duplicate check) and login.

    Args:
        db:    The active database session.
        email: The email address to look up.

    Returns:
        The User ORM object, or None if no user with that email exists.
    """
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session) -> list[User]:
    """
    Retrieve every user in the database.

    This is an admin-only operation; the route enforces that.

    Args:
        db: The active database session.

    Returns:
        A list of all User ORM objects (may be empty).
    """
    return db.query(User).all()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user record in the database.

    The plaintext password is hashed before storage.
    The caller is responsible for checking that the email is not already taken.

    Args:
        db:        The active database session.
        user_data: Validated UserCreate schema with name, email, and password.

    Returns:
        The newly created and persisted User ORM object.
    """
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh so `id`, `created_at`, etc. are populated.
    return new_user


def update_user(db: Session, user: User, update_data: UserUpdate) -> User:
    """
    Apply partial updates to an existing user.

    Only fields explicitly provided (non-None) in update_data are changed.
    Protected fields (id, password_hash, is_admin, created_at) are never modified here.
    The caller is responsible for checking that a new email is not already taken.

    Args:
        db:          The active database session.
        user:        The User ORM object to update.
        update_data: Validated UserUpdate schema with optional name and email.

    Returns:
        The updated User ORM object.
    """
    if update_data.name is not None:
        user.name = update_data.name

    if update_data.email is not None:
        user.email = update_data.email

    # Manually set updated_at because SQLAlchemy's onupdate lambda fires
    # only on UPDATE statements triggered through the ORM flush, which is reliable,
    # but we set it explicitly here for clarity.
    user.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    """
    Permanently delete a user from the database.

    Args:
        db:   The active database session.
        user: The User ORM object to delete.
    """
    db.delete(user)
    db.commit()
