"""
utils/security.py

Low-level security utilities:
  - Password hashing and verification using pwdlib + bcrypt.
  - JWT creation and decoding using python-jose.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import settings

# Create a single shared PasswordHash instance explicitly configured to use bcrypt.
# We use BcryptHasher directly to avoid the default Argon2 dependency.
password_hash_ctx = PasswordHash((BcryptHasher(),))


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password: The raw password string from the user.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    return password_hash_ctx.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plaintext password matches a stored bcrypt hash.

    Args:
        plain_password:  The raw password the user just submitted.
        hashed_password: The hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return password_hash_ctx.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    Generate a signed JWT access token embedding the user's ID.

    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES minutes.

    Args:
        user_id: The primary key of the user to embed in the token.

    Returns:
        A JWT string the client can use as a Bearer token.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),   # "sub" (subject) is the standard JWT claim for user identity
        "exp": expire,         # "exp" (expiration) claim — jose validates this automatically
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """
    Decode and validate a JWT access token.

    Validates the signature and expiration automatically.

    Args:
        token: The raw JWT string from the Authorization header.

    Returns:
        The user ID (int) embedded in the token, or None if the token is
        invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)
    except JWTError:
        return None
