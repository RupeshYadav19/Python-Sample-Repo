"""
routes/users.py

User management endpoints:

  Authenticated user (self):
    GET    /users/me         — View own profile.
    PUT    /users/me         — Update own profile.
    DELETE /users/me         — Delete own account.

  Admin only:
    GET    /users            — List all users.
    GET    /users/{user_id}  — View any user by ID.
    DELETE /users/{user_id}  — Delete any user by ID.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import (
    delete_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from app.utils.dependencies import get_admin_user, get_current_user, get_db

router = APIRouter(prefix="/users", tags=["Users"])


# ---------------------------------------------------------------------------
# Authenticated user (self) endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user's profile",
    description="Returns the profile of the currently authenticated user.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's own profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user's profile",
    description=(
        "Update the authenticated user's name and/or email. "
        "The new email must not already be in use by another account. "
        "Password, admin status, and timestamps cannot be changed through this endpoint."
    ),
)
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Allow a logged-in user to update their own name and/or email."""
    # If the user wants to change their email, make sure no one else has it.
    if update_data.email is not None and update_data.email != current_user.email:
        existing = get_user_by_email(db, update_data.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The email '{update_data.email}' is already in use by another account.",
            )

    updated = update_user(db, current_user, update_data)
    return updated


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Delete current user's account",
    description="Permanently delete the authenticated user's own account.",
)
def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Allow a logged-in user to permanently delete their own account."""
    delete_user(db, current_user)
    return {"message": "Your account has been deleted successfully."}


# ---------------------------------------------------------------------------
# Admin-only endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=list[UserResponse],
    summary="[Admin] List all users",
    description=(
        "Returns a paginated list of registered users. Requires admin privileges. "
        "Use `skip` and `limit` query parameters to page through results."
    ),
)
def list_all_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    _admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    """Return a paginated list of users. Admin only."""
    return get_all_users(db, skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="[Admin] Get a user by ID",
    description="Returns a specific user's profile by their ID. Requires admin privileges.",
)
def get_user(
    user_id: int,
    _admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Return a single user by ID. Admin only."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with ID {user_id}.",
        )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="[Admin] Delete a user by ID",
    description="Permanently delete a user by their ID. Requires admin privileges.",
)
def delete_user_by_id(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a specific user by ID. Admin only."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with ID {user_id}.",
        )

    # Prevent an admin from accidentally deleting themselves through this endpoint.
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete their own account through the admin endpoint. "
                   "Use DELETE /users/me instead.",
        )

    delete_user(db, user)
    return {"message": f"User with ID {user_id} has been deleted successfully."}
