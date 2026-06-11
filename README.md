# Canaan CMS — Backend API

FastAPI backend for the Canaan Global International Content Management System. Designed to be lightweight, production-secure, and compatible with shared hosting environments running Phusion Passenger (cPanel).

---

## Technical Architecture

| Layer | Technology |
|---|---|
| Framework | FastAPI (ASGI) |
| Server | Uvicorn |
| Database | SQLite via SQLAlchemy ORM |
| Auth | JWT (PyJWT) + bcrypt (passlib) |
| Rate Limiting | slowapi (5 login attempts / minute / IP) |
| File Storage | BLOB columns directly in SQLite |
| Config | python-dotenv (.env file) |

### Why SQLite + BLOBs

Images and PDFs are stored as binary columns (`LargeBinary`) directly inside the database. This eliminates the need for filesystem permission management, external cloud storage buckets, or separate static file servers — critical for shared hosting environments where writable directories are restricted.

### Phusion Passenger Compatibility

Phusion Passenger (used by cPanel) may bypass the ASGI `lifespan` startup event. The admin seeding logic is therefore duplicated as a fallback inside the login route. Both paths are idempotent and safe.

---

## Project Structure

```
backend/
├── main.py          App entrypoint, middleware, auth route, lifespan
├── auth.py          JWT creation/verification, bcrypt password hashing
├── database.py      SQLAlchemy engine + session factory (SQLite)
├── models.py        ORM table definitions
├── schemas.py       Pydantic request/response models with computed URL fields
├── requirements.txt Python dependencies
├── cms.db           SQLite database file (auto-created on first run)
└── routers/
    ├── achievements.py
    ├── branches.py
    ├── cargos.py
    ├── circulars.py
    ├── licenses.py
    ├── services.py
    └── teams.py
```

---

## Data Models

### AdminUser
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| username | String | Unique, indexed |
| hashed_password | String | bcrypt hash |

### Achievement
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String | Indexed |
| description | Text | |
| images | Relationship | → AchievementImage (cascade delete) |

### AchievementImage
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| achievement_id | Integer | FK → achievements.id |
| image_blob | LargeBinary | Raw image bytes |

### Circular
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String | Indexed |
| description | Text | |
| circular_name | String | Nullable — reference/number e.g. CIR/2025/001 |
| date | Date | Nullable — official issue date |
| pdf_blob | LargeBinary | Raw PDF bytes |

### TeamMember
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String | Indexed |
| designation | String | |
| email | String | Indexed |
| image_blob | LargeBinary | Portrait image bytes |

### CargoCategory
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String | Unique, indexed |
| images | Relationship | → CargoImage (cascade delete) |

### CargoImage
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| category_id | Integer | FK → cargo_categories.id |
| image_blob | LargeBinary | Raw image bytes |

### Service
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String | Indexed |
| description | Text | |
| image_blob | LargeBinary | |

### License
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String | Indexed |
| description | Text | |
| image_blob | LargeBinary | |

### Branch
| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String | Indexed |
| address | Text | |
| iframe_input | Text | Raw Google Maps embed HTML (src extracted client-side) |
| image_blob | LargeBinary | |

---

## Authentication Flow

1. Client POSTs credentials as `application/x-www-form-urlencoded` to `POST /api/auth/login`.
2. Rate limiter enforces a maximum of **5 attempts per minute per IP**.
3. Backend looks up the `AdminUser` by username, then runs `passlib.verify` against the bcrypt-hashed password.
4. On success, a **7-day JWT** is issued, signed with `JWT_SECRET_KEY` using HS256.
5. All mutating endpoints (`POST`, `PUT`, `DELETE`) require an `Authorization: Bearer <token>` header, validated via the `get_current_user` FastAPI dependency.
6. GET endpoints are publicly accessible (the portfolio frontend reads them without auth).

### Password Hashing

`passlib.CryptContext` is configured with `schemes=["bcrypt", "pbkdf2_sha256"]` and `deprecated="auto"`. The default scheme is **bcrypt**. The `pbkdf2_sha256` scheme is kept in the list for backward-compatible verification of any legacy hashes, but all new passwords are hashed with bcrypt.

A compatibility shim is applied at import time to patch `bcrypt.__about__` — required for passlib to work correctly with bcrypt ≥ 4.0.

---

## Security Measures

### Rate Limiting
`slowapi` wraps the login endpoint:
```
POST /api/auth/login → 5 requests / minute / IP
```
Exceeding the limit returns HTTP 429 with a `Retry-After` header.

### Security Headers Middleware
A custom `SecurityHeadersMiddleware` (Starlette `BaseHTTPMiddleware`) appends the following to every response:

| Header | Value |
|---|---|
| X-Content-Type-Options | nosniff |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | camera=(), microphone=(), geolocation=() |
| Strict-Transport-Security | max-age=31536000; includeSubDomains *(production only)* |

### CORS
Origins are read from `ALLOWED_ORIGINS` (comma-separated env var). Default allows only `localhost:3000` and the two known production domains. Credentials are allowed so the `Authorization` header can be sent.

### API Documentation Lockdown
When `ENVIRONMENT=production`, the `/docs`, `/redoc`, and `/openapi.json` endpoints are disabled, preventing public exposure of the API schema.

### File Upload Validation
Every upload endpoint enforces:
- **Maximum size**: 5 MB per file
- **MIME type**: `image/*` for images, `application/pdf` for circulars

---

## Automatic Schema Migrations

The `lifespan` function runs a set of idempotent `ALTER TABLE … ADD COLUMN` statements at startup. This handles in-place schema upgrades without requiring Alembic or a separate migration step. SQLite silently raises an error if a column already exists — these errors are caught and ignored.

Current migration statements:
```sql
ALTER TABLE circulars ADD COLUMN circular_name TEXT
ALTER TABLE circulars ADD COLUMN date TEXT
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory. All variables are required for production.

| Variable | Description | Example |
|---|---|---|
| `ENVIRONMENT` | Set to `production` to harden the API | `production` |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens — must be a long random string | `openssl rand -hex 32` |
| `ADMIN_USERNAME` | Master admin login username | `canaan_admin` |
| `ADMIN_PASSWORD` | Master admin login password | `a-very-strong-password` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `https://canaan-cms.vercel.app` |
| `API_BASE_URL` | Public base URL of this API — used to build image/PDF URLs in responses | `https://api.popememorialhss.org` |

---

## API Reference

All `POST`, `PUT`, `DELETE` endpoints require:
```
Authorization: Bearer <token>
```

`GET` endpoints are public.

### Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | — | Returns a 7-day JWT. Rate limited: 5/min/IP. Body: `application/x-www-form-urlencoded` with `username` and `password`. |

### Achievements

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/achievements/` | — | List all achievements (with nested image URLs) |
| POST | `/api/achievements/` | Yes | Create achievement (`title`, `description`) |
| PUT | `/api/achievements/{id}` | Yes | Update achievement text fields |
| DELETE | `/api/achievements/{id}` | Yes | Delete achievement and all its images |
| POST | `/api/achievements/{id}/images` | Yes | Upload one or more images (`multipart/form-data`, field: `files`) |
| GET | `/api/achievements/images/{id}/content` | — | Serve raw image bytes |
| DELETE | `/api/achievements/images/{id}` | Yes | Delete a single image |

### Circulars

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/circulars/` | — | List all circulars (with computed `pdf_url`) |
| POST | `/api/circulars/` | Yes | Create circular (`title`, `description`, `circular_name`?, `date`?) |
| PUT | `/api/circulars/{id}` | Yes | Update circular fields |
| DELETE | `/api/circulars/{id}` | Yes | Delete circular |
| POST | `/api/circulars/{id}/pdf` | Yes | Upload PDF (`multipart/form-data`, field: `file`) |
| GET | `/api/circulars/{id}/pdf` | — | Serve raw PDF bytes (`application/pdf`) |

### Teams

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/teams/` | — | List all team members |
| POST | `/api/teams/` | Yes | Create member (`name`, `designation`, `email`) |
| PUT | `/api/teams/{id}` | Yes | Update member |
| DELETE | `/api/teams/{id}` | Yes | Delete member |
| POST | `/api/teams/{id}/image` | Yes | Upload portrait image |
| GET | `/api/teams/{id}/image` | — | Serve portrait image bytes |

### Cargo Categories

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/cargos/` | — | List all categories (with nested image URLs) |
| POST | `/api/cargos/` | Yes | Create category (`name`) |
| PUT | `/api/cargos/{id}` | Yes | Update category name |
| DELETE | `/api/cargos/{id}` | Yes | Delete category and all its images |
| POST | `/api/cargos/{id}/images` | Yes | Upload one or more images (`multipart/form-data`, field: `files`) |
| GET | `/api/cargos/images/{id}/content` | — | Serve raw image bytes |
| DELETE | `/api/cargos/images/{id}` | Yes | Delete a single image |

### Services

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/services/` | — | List all services |
| POST | `/api/services/` | Yes | Create service (`title`, `description`) |
| PUT | `/api/services/{id}` | Yes | Update service |
| DELETE | `/api/services/{id}` | Yes | Delete service |
| POST | `/api/services/{id}/image` | Yes | Upload service image |
| GET | `/api/services/{id}/image` | — | Serve image bytes |

### Licenses

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/licenses/` | — | List all licenses |
| POST | `/api/licenses/` | Yes | Create license (`title`, `description`) |
| PUT | `/api/licenses/{id}` | Yes | Update license |
| DELETE | `/api/licenses/{id}` | Yes | Delete license |
| POST | `/api/licenses/{id}/image` | Yes | Upload license image |
| GET | `/api/licenses/{id}/image` | — | Serve image bytes |

### Branches

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/branches/` | — | List all branches |
| POST | `/api/branches/` | Yes | Create branch (`title`, `address`, `iframe_input`) |
| PUT | `/api/branches/{id}` | Yes | Update branch |
| DELETE | `/api/branches/{id}` | Yes | Delete branch |
| POST | `/api/branches/{id}/image` | Yes | Upload branch image |
| GET | `/api/branches/{id}/image` | — | Serve image bytes |

---

## Local Development Setup

The recommended Python environment for this project is the `deeplearning` conda environment.

```bash
conda activate deeplearning
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```env
ENVIRONMENT=development
JWT_SECRET_KEY=any-long-random-string-for-local-dev
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_BASE_URL=http://localhost:8000
```

Start the server:
```bash
uvicorn main:app --reload
```

The database file `cms.db` is created automatically on first run. The admin user is seeded from the env variables.

Interactive API docs (development only): `http://localhost:8000/docs`

---

## Production Deployment (cPanel / Phusion Passenger)

1. Upload the `backend/` directory to your hosting environment.
2. Configure a Python app in cPanel pointing at `main:app`.
3. Set all required environment variables in the cPanel Python app configuration or in `backend/.env`.
4. Ensure `ENVIRONMENT=production` is set to disable API docs and enable HSTS.
5. The `lifespan` startup will run migrations and seed the admin on the first request cycle.
