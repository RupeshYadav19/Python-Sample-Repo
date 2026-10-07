"""
main.py

The FastAPI application entry point.

Responsibilities:
  - Create the FastAPI application instance.
  - Create database tables on startup.
  - Register route handlers (auth + users).
  - Provide a health-check root endpoint.
"""

from fastapi import FastAPI

from app.database.database import create_tables
from app.routes import auth, users

# ---------------------------------------------------------------------------
# Create the FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="User Management API",
    description=(
        "A clean, beginner-friendly User Management System built with FastAPI, "
        "SQLAlchemy, and JWT authentication.\n\n"
        "**How to authenticate in Swagger:**\n"
        "1. Register via `POST /auth/register`.\n"
        "2. Login via `POST /auth/login` to get your token.\n"
        "3. Click the **Authorize 🔒** button above and paste: `Bearer <your_token>`."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Startup: create database tables
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    """
    Create all database tables when the application starts.
    If the tables already exist, this is a no-op (safe to call repeatedly).
    """
    create_tables()


# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(users.router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"], summary="Health check")
def root() -> dict:
    """Confirm the API is running."""
    return {"message": "User Management API is running"}
