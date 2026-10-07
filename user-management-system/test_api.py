"""
test_api.py  —  End-to-end smoke tests for the User Management API.

Run with:  python test_api.py

Tests:
  1.  GET  /                            Health check
  2.  POST /auth/register               Register a new user
  3.  POST /auth/register               Duplicate email -> 409
  4.  POST /auth/login                  Valid login -> token
  5.  POST /auth/login                  Wrong password -> 401
  6.  GET  /users/me                    Without token -> 403
  7.  GET  /users/me                    With valid token -> 200
  8.  PUT  /users/me                    Update name
  9.  GET  /users                       Normal user -> 403
  10. GET  /users (as admin)            Admin -> 200
  11. GET  /users/{id} (as admin)       Admin -> 200
  12. GET  /users/999 (as admin)        Non-existent -> 404
  13. DELETE /users/{id} (as admin)     Admin deletes another user
  14. DELETE /users/me                  Delete own account
"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

failures = 0


def request(method, path, body=None, token=None, expected_status=200):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            body_out = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        status = e.code
        body_out = json.loads(e.read())

    return status, body_out


def check(test_name, condition, info=""):
    global failures
    if condition:
        print(f"  [{PASS}] {test_name}")
    else:
        print(f"  [{FAIL}] {test_name}  ← {info}")
        failures += 1


print("\n=== User Management API — End-to-End Tests ===\n")

# ── Test 1: Health check ──────────────────────────────────────────────────────
status, body = request("GET", "/")
check("1. GET /  -> 200 + message", status == 200 and "message" in body)

# ── Test 2: Register new user ─────────────────────────────────────────────────
status, body = request("POST", "/auth/register", {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "securepass123",
})
check("2. POST /auth/register -> 201", status == 201, body)
check("2b. No password_hash in response", "password_hash" not in body and "password" not in body)
user_id = body.get("id")

# ── Test 3: Duplicate email -> 409 ─────────────────────────────────────────────
status, body = request("POST", "/auth/register", {
    "name": "Duplicate",
    "email": "testuser@example.com",
    "password": "anotherpass123",
})
check("3. Duplicate email -> 409", status == 409, body)

# ── Test 4: Valid login ───────────────────────────────────────────────────────
status, body = request("POST", "/auth/login", {
    "email": "testuser@example.com",
    "password": "securepass123",
})
check("4. POST /auth/login -> 200 + token", status == 200 and "access_token" in body, body)
valid_token = body.get("access_token", "")

# ── Test 5: Wrong password -> 401 ─────────────────────────────────────────────
status, body = request("POST", "/auth/login", {
    "email": "testuser@example.com",
    "password": "WRONGPASSWORD",
})
check("5. Wrong password -> 401", status == 401, body)

# ── Test 6: /users/me without token ──────────────────────────────────────────
status, body = request("GET", "/users/me")
check("6. GET /users/me (no token) -> 403", status == 403, body)

# ── Test 7: /users/me with valid token ───────────────────────────────────────
status, body = request("GET", "/users/me", token=valid_token)
check("7. GET /users/me (valid token) -> 200", status == 200, body)
check("7b. No password_hash in /me response", "password_hash" not in body)

# ── Test 8: PUT /users/me ─────────────────────────────────────────────────────
status, body = request("PUT", "/users/me", {"name": "Updated Name"}, token=valid_token)
check("8. PUT /users/me -> 200 + updated name", status == 200 and body.get("name") == "Updated Name", body)

# ── Test 9: Normal user hitting admin endpoint ────────────────────────────────
status, body = request("GET", "/users", token=valid_token)
check("9. GET /users (normal user) -> 403", status == 403, body)

# ── Register an admin user for admin tests ────────────────────────────────────
status, body = request("POST", "/auth/register", {
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "adminpass123",
})
admin_id = body.get("id")

# Promote the admin user directly via SQLite
import subprocess
result = subprocess.run(
    ["python", "-c",
     "from app.database.database import SessionLocal; "
     "from app.database.models import User; "
     "db = SessionLocal(); "
     f"u = db.query(User).filter(User.id == {admin_id}).first(); "
     "u.is_admin = True; "
     "db.commit(); "
     "print('Admin promoted OK')"],
    capture_output=True, text=True, cwd="."
)
print(f"\n  [INFO] Admin promotion: {result.stdout.strip() or result.stderr.strip()}")

# Login as admin
status, body = request("POST", "/auth/login", {
    "email": "admin@example.com",
    "password": "adminpass123",
})
admin_token = body.get("access_token", "")
check("9b. Admin login OK", status == 200 and admin_token, body)

# ── Test 10: Admin list users ─────────────────────────────────────────────────
status, body = request("GET", "/users", token=admin_token)
check("10. GET /users (admin) -> 200 + list", status == 200 and isinstance(body, list), body)

# ── Test 11: Admin get user by ID ─────────────────────────────────────────────
status, body = request("GET", f"/users/{user_id}", token=admin_token)
check("11. GET /users/{id} (admin) -> 200", status == 200 and body.get("id") == user_id, body)

# ── Test 12: Non-existent user -> 404 ─────────────────────────────────────────
status, body = request("GET", "/users/999999", token=admin_token)
check("12. GET /users/999999 -> 404", status == 404, body)

# ── Test 13: Admin deletes a user ─────────────────────────────────────────────
status, body = request("DELETE", f"/users/{user_id}", token=admin_token)
check("13. DELETE /users/{id} (admin) -> 200", status == 200, body)

# Verify user is gone
status, body = request("GET", f"/users/{user_id}", token=admin_token)
check("13b. Deleted user -> 404", status == 404, body)

# ── Test 14: DELETE /users/me ─────────────────────────────────────────────────
# Register a fresh user to delete via /me
status, body = request("POST", "/auth/register", {
    "name": "To Delete",
    "email": "todelete@example.com",
    "password": "deletepass123",
})
status, body = request("POST", "/auth/login", {
    "email": "todelete@example.com",
    "password": "deletepass123",
})
delete_token = body.get("access_token", "")
status, body = request("DELETE", "/users/me", token=delete_token)
check("14. DELETE /users/me -> 200", status == 200, body)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*48}")
if failures == 0:
    print("  ALL TESTS PASSED (OK)")
else:
    print(f"\033[91m  {failures} TEST(S) FAILED\033[0m")
print(f"{'='*48}\n")

sys.exit(0 if failures == 0 else 1)
