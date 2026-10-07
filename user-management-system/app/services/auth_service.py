"""
services/auth_service.py

Authentication business logic:
  - Verifying a user's credentials (email + password).
  - Generating JWT access tokens.

Password hashing primitives live in utils/security.py;
this service composes them with database lookups.
"""

from sqlalchemy.orm import Session

from app.database.models import User
from app.services.user_service import get_user_by_email
from app.utils.security import create_access_token, verify_password


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Validate a user's email and password.

    Steps:
      1. Look up the user by email.
      2. Verify the submitted plaintext password against the stored hash.

    Does NOT check whether the account is active — the route handles that
    so it can return an appropriate HTTP status code.

    Args:
        db:       The active database session.
        email:    The email address submitted by the user.
        password: The plaintext password submitted by the user.

    Returns:
        The User ORM object if credentials are correct, or None otherwise.
    """
    user = get_user_by_email(db, email)
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def generate_token_for_user(user: User) -> str:
    """
    Generate a signed JWT access token for an authenticated user.

    Delegates to the low-level create_access_token utility.

    Args:
        user: The authenticated User ORM object.

    Returns:
        A JWT string to return to the client.
    """
    return create_access_token(user_id=user.id)
