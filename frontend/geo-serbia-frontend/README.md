# GeoSerbia Frontend

GeoSerbia frontend is a Vue 3 game UI for a Serbia-focused GeoGuessr-style experience.
Players guess map locations from photos, see score/distance feedback, and track performance through profile and leaderboards.

## Stack

- Vue 3 (Composition API)
- Vue Router
- Axios
- Leaflet
- Vite

## Project Structure

```text
geo-serbia-frontend/
  src/
    api/
    assets/
    components/
    composables/
    router/
    stores/
    views/
  public/
  package.json
  vite.config.js
  README.md
```

## Setup

1. Go to frontend folder:

```powershell
cd C:\Users\amalezic\Desktop\mst\frontend\geo-serbia-frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Configure `.env` (optional but recommended):

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

Note:
- If `VITE_API_URL` is not set, the app auto-builds a base URL and appends `/api/v1`.
- Keep frontend/backend host consistent (`localhost` with `localhost`, or `127.0.0.1` with `127.0.0.1`) to avoid cookie auth issues.

## Run

Development:

```powershell
npm run dev
```

Production build:

```powershell
npm run build
```

Preview build:

```powershell
npm run preview
```

## Run With Containers (Frontend + Backend + DB)

From this frontend folder:

```powershell
docker compose -f docker-compose.fullstack.yml up --build
```

App URLs:
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`

## Backend Requirements

Frontend expects backend running with:

- Base URL: `http://127.0.0.1:8000` (or `localhost:8000`)
- API prefix: `/api/v1`
- Cookie auth enabled (HTTP-only cookies)
- CORS allowing frontend origin (`http://localhost:5173` and/or `http://127.0.0.1:5173`)

## Main Features

- Auth page with login/register toggle
- Session restore via `GET /api/v1/auth/me`
- Home hero page with game CTA
- Game split layout (photo + map)
- Round progress (`Round X / 5`)
- Animated score and distance feedback
- Round hints (`up to 3`) with server-side score penalty
- Adaptive/fixed challenge mode toggle
- Difficulty badge and skill indicator
- Leaderboards (daily/monthly) with top medal icons and current-user highlight
- Profile stats + adaptive stats panel
- Add Location with map-click coordinate autofill
- Admin pending location moderation page
- Admin adaptive analytics page

## Important Routes

- `/auth`
- `/`
- `/game`
- `/summary`
- `/leaderboard`
- `/profile`
- `/add-location`
- `/admin/pending-locations` (admin)
- `/admin/adaptive-stats` (admin)

## API Integration (used by frontend)

### Auth/Profile
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/profile/adaptive-stats`

### Game
- `POST /api/v1/game/start?mode=adaptive|fixed`
- `POST /api/v1/game/hint`
- `POST /api/v1/game/play`
- `GET /api/v1/game/leaderboard/daily`
- `GET /api/v1/game/leaderboard/monthly`

### Locations/Admin
- `GET /api/v1/locations/`
- `POST /api/v1/locations/`
- `GET /api/v1/locations/pending`
- `POST /api/v1/locations/{id}/approve`
- `POST /api/v1/locations/{id}/reject`
- `GET /api/v1/admin/adaptive/stats`

## Testing and Validation

Recommended checks before demo:

1. Backend tests pass.
2. Frontend build passes:

```powershell
npm run build
```

3. Manual flow:
- login as `tojaga`, `somi`, `maleza` and compare adaptive difficulty
- submit guesses and verify summary
- login as admin and check pending moderation + adaptive analytics

## Notes

- Frontend keeps a local adaptive fallback model to preserve UX if adaptive backend endpoints are temporarily unavailable.
- Backend remains source of truth for scoring and auth.
