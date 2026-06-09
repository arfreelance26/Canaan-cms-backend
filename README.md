# Canaan CMS Backend API

This directory contains the FastAPI backend for the Canaan Content Management System. It is designed to be lightweight, secure, and compatible with shared hosting environments like Phusion Passenger.

## Technical Architecture

- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: PBKDF2 (SHA256) via passlib (pure Python implementation to ensure compatibility across restrictive environments where C-extensions like bcrypt may fail).
- **File Storage**: Binary Large Objects (BLOBs) stored directly within the SQLite database. This eliminates the need for separate file system permission management and external cloud buckets.

## Security Configurations

The application relies strictly on environment variables to prevent hardcoded secrets. In production, you must define these variables in a `.env` file located in the root of the backend directory.

Required Environment Variables:
- `ENVIRONMENT`: Set to `production` to disable the auto-generated public API documentation.
- `JWT_SECRET_KEY`: A cryptographically secure random string used to sign JWT tokens.
- `ADMIN_USERNAME`: The master administrator username.
- `ADMIN_PASSWORD`: The master administrator password.
- `ALLOWED_ORIGINS`: A comma-separated list of domains permitted to access the API via CORS.

Note: The system will refuse to seed or authenticate users if `ADMIN_USERNAME` and `ADMIN_PASSWORD` are missing in production.

## API Endpoints

All data modification endpoints (POST, PUT, DELETE) require a valid JWT token passed in the `Authorization: Bearer <token>` header. GET requests are publicly accessible.

### Authentication
- `POST /api/auth/login`: Authenticates the user and returns a JWT access token.

### Achievements
- `GET /api/achievements/`: Retrieves all achievements.
- `POST /api/achievements/`: Creates a new achievement.
- `PUT /api/achievements/{id}`: Updates an existing achievement.
- `DELETE /api/achievements/{id}`: Deletes an achievement and its associated images.
- `POST /api/achievements/{id}/images`: Accepts a batch list of image files to associate with the achievement.
- `DELETE /api/achievements/images/{id}`: Deletes a specific image from an achievement.
- `GET /api/achievements/images/{id}/content`: Serves the raw image blob data.

### Cargo Categories
- `GET /api/cargos/`: Retrieves all cargo categories.
- `POST /api/cargos/`: Creates a new cargo category.
- `PUT /api/cargos/{id}`: Updates an existing cargo category.
- `DELETE /api/cargos/{id}`: Deletes a cargo category and its associated images.
- `POST /api/cargos/{id}/images`: Accepts a batch list of image files to associate with the category.
- `DELETE /api/cargos/images/{id}`: Deletes a specific image.
- `GET /api/cargos/images/{id}/content`: Serves the raw image blob data.

### Services
- `GET /api/services/`: Retrieves all services.
- `POST /api/services/`: Creates a new service.
- `PUT /api/services/{id}`: Updates a service.
- `DELETE /api/services/{id}`: Deletes a service.
- `POST /api/services/{id}/image`: Uploads the primary image for the service.
- `GET /api/services/{id}/image`: Serves the primary image blob.

### Branches
- `GET /api/branches/`: Retrieves all branch locations.
- `POST /api/branches/`: Creates a new branch.
- `PUT /api/branches/{id}`: Updates a branch.
- `DELETE /api/branches/{id}`: Deletes a branch.
- `POST /api/branches/{id}/image`: Uploads the primary image for the branch.
- `GET /api/branches/{id}/image`: Serves the primary image blob.

### Teams
- `GET /api/teams/`: Retrieves all team members.
- `POST /api/teams/`: Adds a new team member.
- `PUT /api/teams/{id}`: Updates a team member.
- `DELETE /api/teams/{id}`: Removes a team member.
- `POST /api/teams/{id}/image`: Uploads the team member's portrait image.
- `GET /api/teams/{id}/image`: Serves the portrait image blob.

### Licenses
- `GET /api/licenses/`: Retrieves all licenses and certifications.
- `POST /api/licenses/`: Adds a new license.
- `PUT /api/licenses/{id}`: Updates a license.
- `DELETE /api/licenses/{id}`: Removes a license.
- `POST /api/licenses/{id}/image`: Uploads the license image.
- `GET /api/licenses/{id}/image`: Serves the license image blob.

### Circulars
- `GET /api/circulars/`: Retrieves all circulars.
- `POST /api/circulars/`: Creates a new circular entry.
- `PUT /api/circulars/{id}`: Updates a circular.
- `DELETE /api/circulars/{id}`: Deletes a circular.
- `POST /api/circulars/{id}/pdf`: Uploads a PDF document for the circular.
- `GET /api/circulars/{id}/pdf`: Serves the raw PDF blob data with the appropriate application/pdf headers.

## Local Development Setup

To run the backend locally:

1. Create a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a local `.env` file containing the required variables (e.g., `ADMIN_USERNAME`, `ADMIN_PASSWORD`).
4. Start the server: `uvicorn main:app --reload`
