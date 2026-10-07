# User Management System

A clean, beginner-friendly **User Management REST API** built with **FastAPI**, **SQLAlchemy**, **SQLite**, and **JWT authentication**. This project is designed as a properly structured, production-style learning project.

---

## Features

- **User Registration** — Create accounts with name, email, and a hashed password
- **JWT Login** — Authenticate and receive a Bearer token
- **Profile Management** — View, update, or delete your own account
- **Admin Role** — Admins can list, view, and delete any user
- **Swagger UI** — Interactive API docs available out of the box
- **Secure by design** — Passwords hashed with bcrypt, JWT expiry enforced, no raw SQL

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Language |
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| SQLAlchemy | ORM (database layer) |
| SQLite | Database (file-based, zero setup) |
| Pydantic v2 | Data validation and serialization |
| pydantic-settings | Environment variable loading |
| python-jose | JWT token creation and validation |
| pwdlib + bcrypt | Password hashing |

---

## Project Structure

```
user-management-system/
│
├── app/
│   ├── main.py               ← FastAPI app, startup, router registration
│   ├── config.py             ← Settings loaded from .env
│   │
│   ├── database/
│   │   ├── database.py       ← SQLAlchemy engine, session, Base
│   │   └── models.py         ← User ORM model
│   │
│   ├── schemas/
│   │   └── user.py           ← Pydantic schemas (request/response shapes)
│   │
│   ├── services/
│   │   ├── user_service.py   ← User CRUD business logic
│   │   └── auth_service.py   ← Authentication logic
│   │
│   ├── routes/
│   │   ├── auth.py           ← POST /auth/register, POST /auth/login
│   │   └── users.py          ← GET/PUT/DELETE /users/me, Admin /users endpoints
│   │
│   └── utils/
│       ├── security.py       ← Password hashing, JWT encode/decode
│       └── dependencies.py   ← FastAPI dependency injection (auth guards)
│
├── .env                      ← Your local secrets (not committed to git)
├── .env.example              ← Template for .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and edit it:

```bash
copy .env.example .env
```

Open `.env` and set your values:

```env
JWT_SECRET=your-very-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./users.db
```

> **Important:** Change `JWT_SECRET` to a long, random string. Never commit `.env` to version control.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The `users.db` SQLite file is created automatically on first startup.

### 6. Open Swagger UI

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to see all endpoints.

---

## API Endpoints

### Public Endpoints (no token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a JWT |

### Authenticated Endpoints (Bearer token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me` | Get your own profile |
| `PUT` | `/users/me` | Update your name or email |
| `DELETE` | `/users/me` | Delete your own account |

### Admin-Only Endpoints (admin token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users |
| `GET` | `/users/{user_id}` | Get any user by ID |
| `DELETE` | `/users/{user_id}` | Delete any user by ID |

---

## Usage Examples

### Register

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Rupesh", "email": "rupesh@gmail.com", "password": "password123"}'
```

**Response:**
```json
{
  "id": 1,
  "name": "Rupesh",
  "email": "rupesh@gmail.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "rupesh@gmail.com", "password": "password123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use the Token

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Using the JWT Token in Swagger

1. Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Call `POST /auth/login` to get your token.
3. Copy the `access_token` value from the response.
4. Click the **Authorize 🔒** button at the top right of the Swagger page.
5. In the `HTTPBearer` field, paste just the token (without the word "Bearer").
6. Click **Authorize**, then **Close**.
7. All subsequent requests in Swagger will now include your token.

---

## Making a User an Admin

SQLite doesn't have a built-in admin UI, but you can promote a user using the SQLite CLI or any SQLite browser:

```sql
UPDATE users SET is_admin = 1 WHERE email = 'rupesh@gmail.com';
```

Or use the [DB Browser for SQLite](https://sqlitebrowser.org/) (free GUI tool).

---

## Security Notes

- Passwords are **never** stored in plaintext — only bcrypt hashes.
- The `password_hash` field is **never** included in API responses.
- JWTs are signed with your `JWT_SECRET` and expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.
- All database queries use SQLAlchemy ORM (parameterized) — no raw SQL string concatenation.
- Inactive users are rejected at the authentication layer.
