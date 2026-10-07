-- =============================================================
-- User Management System — Database Schema
-- File: schema.sql
-- Database: SQLite
--
-- This file defines the full database schema.
-- It is NOT connected to the application yet.
-- To apply manually:
--   sqlite3 users.db < schema.sql
-- =============================================================


-- Drop the table if it already exists (useful for fresh resets)
DROP TABLE IF EXISTS users;


-- -------------------------------------------------------------
-- Table: users
-- -------------------------------------------------------------
CREATE TABLE users (
    -- Primary key, auto-incremented
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,

    -- User's display name, required
    name            TEXT        NOT NULL,

    -- Unique email address used for login
    email           TEXT        NOT NULL UNIQUE,

    -- Bcrypt hash of the password — plaintext is NEVER stored
    password_hash   TEXT        NOT NULL,

    -- Whether the account is active (1 = active, 0 = deactivated)
    is_active       INTEGER     NOT NULL DEFAULT 1,

    -- Whether the user has admin privileges (1 = admin, 0 = regular)
    is_admin        INTEGER     NOT NULL DEFAULT 0,

    -- Timestamps stored in UTC ISO-8601 format
    created_at      TEXT        NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT        NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);


-- -------------------------------------------------------------
-- Index: speed up lookups by email (used on every login)
-- -------------------------------------------------------------
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- Index on id is automatic (PRIMARY KEY), but listed here for clarity:
-- CREATE UNIQUE INDEX IF NOT EXISTS ix_users_id ON users (id);


-- -------------------------------------------------------------
-- Trigger: keep updated_at current whenever a row is modified
-- -------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_users_updated_at
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    WHERE id = OLD.id;
END;


-- =============================================================
-- Sample seed data (optional — comment out for production)
-- =============================================================

-- Regular user (password: "password123" — replace hash before use)
-- INSERT INTO users (name, email, password_hash, is_active, is_admin)
-- VALUES (
--     'Rupesh',
--     'rupesh@gmail.com',
--     '$2b$12$examplehashgoesherereplaceme',
--     1,
--     0
-- );

-- Admin user (password: "adminpass123" — replace hash before use)
-- INSERT INTO users (name, email, password_hash, is_active, is_admin)
-- VALUES (
--     'Admin',
--     'admin@example.com',
--     '$2b$12$examplehashgoesherereplaceme',
--     1,
--     1
-- );
