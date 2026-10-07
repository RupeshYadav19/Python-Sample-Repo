"""
schemas/user.py

Pydantic schemas define the shape of data coming into the API (requests)
and the shape of data going out (responses).

Key rule: password_hash is NEVER included in any response schema.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Request schemas (data coming IN from the client)
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    name: str = Field(..., min_length=1, max_length=100, description="Display name of the user")
    email: EmailStr = Field(..., description="Valid email address (must be unique)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserLogin(BaseModel):
    """Schema for logging in with email and password."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class UserUpdate(BaseModel):
    """
    Schema for updating the current user's profile.
    All fields are optional — only the provided fields will be updated.
    """

    name: str | None = Field(None, min_length=1, max_length=100, description="New display name")
    email: EmailStr | None = Field(None, description="New email address (must not be taken)")


# ---------------------------------------------------------------------------
# Response schemas (data going OUT to the client)
# ---------------------------------------------------------------------------


class UserResponse(BaseModel):
    """
    Safe user representation returned by all user-related endpoints.
    password_hash is intentionally excluded.
    """

    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    # Allow Pydantic to read attributes from SQLAlchemy ORM objects directly.
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for the JWT token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
