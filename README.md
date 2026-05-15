# GeoSerbia

GeoSerbia is a full-stack geolocation guessing web application focused on Serbian locations. Users guess locations on an interactive map based on images, receive distance-based scores, and progress through an adaptive difficulty system based on their performance.

Live demo: https://www.geoserbia.xyz

## Features

- User registration, login and logout
- JWT authentication with HTTP-only cookies
- 5-round game sessions
- Haversine distance calculation and location-based scoring
- Hint system
- Daily and monthly leaderboards
- User profile statistics
- User-submitted locations
- Admin moderation for pending locations
- Image upload validation
- Adaptive difficulty based on user skill and location difficulty
- Endpoint-level automated tests
- Production deployment on VPS with Docker Compose and Nginx

## Tech Stack

**Backend:** FastAPI, PostgreSQL, Tortoise ORM, Aerich  
**Frontend:** Vue.js, Leaflet, Axios  
**Infrastructure:** Docker Compose, Nginx, VPS, Cloudflare DNS/SSL  

## Architecture

GeoSerbia follows a client-server architecture. The Vue frontend communicates with the FastAPI backend through REST API endpoints. The backend handles authentication, game sessions, scoring, adaptive difficulty, location moderation and database persistence.

## Main Modules

- `users` — authentication and user profiles
- `game` — game sessions, rounds, scoring and hints
- `locations` — approved and user-submitted locations
- `admin` — moderation and statistics
- `adaptive` — user skill and location difficulty logic

## Local Development

```bash
git clone https://github.com/AleksaMalezic/geo-serbia.git
cd geo-serbia
docker compose up --build
