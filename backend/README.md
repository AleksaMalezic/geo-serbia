# GeoSerbia Backend

GeoSerbia is a geography game backend inspired by GeoGuessr and focused on Serbia.
Players guess map locations from images, get distance-based points, and compete on leaderboards.

This backend is implemented with FastAPI, PostgreSQL, and Tortoise ORM.

## Stack

- FastAPI
- Tortoise ORM
- PostgreSQL (Docker)
- Aerich (migrations)
- JWT auth with HTTP-only cookies
- Pytest

## Project Structure

```text
backend/
  migrations/
  src/
    boot/
      main.py
    core/
      auth.py
      database.py
      security.py
      settings.py
    domains/
      users/
      locations/
      games/
      admin/
    scripts/
      commands/
      seeders/
      tests/
    static/uploads/locations/
    utils/
  docker-compose.yml
  requirements.txt
  pytest.ini
  README.md
```

## Setup

1. Go to backend folder:

```powershell
cd C:\Users\amalezic\Desktop\mst\backend
```

2. Create and activate venv:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Start PostgreSQL:

```powershell
docker compose up -d
```

5. Configure `.env` (example):

```env
DATABASE_USER=postgres
DATABASE_PASS=root
DATABASE_ADDRESS=localhost
DATABASE_PORT=5435
DATABASE_NAME=geo_serbia
SECRET_KEY=supersecretkey
JWT_ALGORITHM=HS256
```

## Migrations

Run after pulling model changes:

```powershell
aerich migrate --name some_name
aerich upgrade
```

If you want a clean local reset:

```powershell
python -m src.scripts.commands.reset_database
```

## Seed Data

Run all seeders:

```powershell
python -m src.scripts.seeders.seed
```

Seeded users include:

- `geo_admin` (admin)
- `geo_user`
- `tojaga` (low-skill persona)
- `somi` (medium-skill persona)
- `maleza` (high-skill persona)

Adaptive profiles are seeded for personas, and location difficulty profiles are initialized.

## Run Server

```powershell
uvicorn src.boot.main:app --reload
```

API docs:

- `http://127.0.0.1:8000/docs`

## Authentication Model

- Login sets access/refresh JWT in HTTP-only cookies.
- Protected endpoints use cookie auth (`get_current_user`).
- Admin endpoints require `is_admin=True`.

## Key Endpoints

### Auth / Profile

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/profile/adaptive-stats`

### Game

- `POST /api/v1/game/start?mode=adaptive|fixed`
- `POST /api/v1/game/play`
- `GET /api/v1/game/leaderboard/daily`
- `GET /api/v1/game/leaderboard/monthly`

### Locations

- `GET /api/v1/locations/`
- `GET /api/v1/locations/pending` (admin)
- `POST /api/v1/locations/`
- `POST /api/v1/locations/{location_id}/approve` (admin)
- `POST /api/v1/locations/{location_id}/reject` (admin)
- `DELETE /api/v1/locations/{location_id}`

### Admin

- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/adaptive/stats`

## Game and Adaptive Behavior

- Daily play is limited to 5 rounds per user.
- Round score is derived from Haversine distance.
- Adaptive system tracks:
  - `user_skill_profile`
  - `location_difficulty_profile`
  - `adaptive_decision_log`
- `/game/start` in adaptive mode picks rounds closest to user skill profile.

## Moderation Logic

- Regular users create pending locations (`is_approved=False`).
- Admin-created locations are auto-approved in service layer.
- Admin can approve/reject pending user submissions.

## Testing

Run all tests:

```powershell
venv\Scripts\python -m pytest -q
```

Current expected status in this project version:

- all tests passing (including adaptive and seeded persona tests).

## Presentation Quick Checklist

1. `docker compose up -d`
2. `aerich upgrade`
3. `python -m src.scripts.seeders.seed`
4. `uvicorn src.boot.main:app --reload`
5. Demo with users:
   - `tojaga`
   - `somi`
   - `maleza`
6. Show admin pages:
   - pending locations
   - adaptive analytics
