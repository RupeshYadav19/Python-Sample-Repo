"""
database/models.py

SQLAlchemy ORM models that map Python classes to database tables.
The User model represents a row in the 'users' table.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class User(Base):
    """
    Represents a user in the system.

    Columns:
      - id            : Auto-incremented primary key.
      - name          : The user's display name.
      - email         : Unique email address used for login.
      - password_hash : Bcrypt hash of the user's password (never plaintext).
      - is_active     : Whether the account is active (default True).
      - is_admin      : Whether the user has admin privileges (default False).
      - created_at    : Timestamp when the user was created.
      - updated_at    : Timestamp of the last update.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
