"""
routes/auth.py

Authentication endpoints:
  POST /auth/register  — Create a new user account.
  POST /auth/login     — Authenticate and receive a JWT token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, generate_token_for_user
from app.services.user_service import create_user, get_user_by_email
from app.utils.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new user account with a name, email, and password. "
        "The email must be unique. The password is hashed before storage — "
        "it is never stored or returned in plaintext."
    ),
)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Register a new user.

    - Validates input via Pydantic (UserCreate schema).
    - Checks for duplicate email → 409 Conflict.
    - Hashes the password.
    - Returns the new user's safe information (no password hash).
    """
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with the email '{user_data.email}' already exists.",
        )

    new_user = create_user(db, user_data)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT token",
    description=(
        "Authenticate with email and password. "
        "Returns a JWT Bearer token to use in the Authorization header for protected endpoints."
    ),
)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Authenticate a user and issue a JWT.

    - Looks up user by email.
    - Verifies the password hash.
    - Checks the account is active.
    - Returns the JWT access token.
    """
    user = authenticate_user(db, credentials.email, credentials.password)

    # Use the same error for wrong email and wrong password to avoid leaking
    # information about which accounts exist.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support.",
        )

    token = generate_token_for_user(user)
    return TokenResponse(access_token=token)
