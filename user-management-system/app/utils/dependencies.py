"""
utils/dependencies.py

FastAPI dependency functions that are injected into route handlers.

  - get_db()           : Yields a database session and closes it after the request.
  - get_current_user() : Extracts and validates the JWT, then loads the user from DB.
  - get_admin_user()   : Extends get_current_user() — also requires is_admin == True.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User
from app.utils.security import decode_access_token

# HTTPBearer extracts the token from the "Authorization: Bearer <token>" header.
bearer_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy database session for a single request.

    FastAPI will call this as a dependency.  The session is always closed
    after the request finishes (even if an exception is raised).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate the request by validating the Bearer JWT token.

    Steps:
      1. Extract the raw token string from the Authorization header.
      2. Decode and validate the JWT (signature + expiry).
      3. Load the user from the database using the ID in the token.
      4. Reject the request if the user no longer exists or is inactive.

    Returns:
        The authenticated User ORM object.

    Raises:
        401 if the token is missing, invalid, or expired.
        403 if the user account is inactive.
    """
    token = credentials.credentials

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User belonging to this token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Extend get_current_user() to also require admin privileges.

    Returns:
        The authenticated User ORM object (guaranteed to be an admin).

    Raises:
        403 if the authenticated user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action.",
        )
    return current_user
