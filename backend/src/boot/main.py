from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.database import close_db, init_db
from src.domains.admin.routers import router as admin_router
from src.domains.games.routers import router as game_router
from src.domains.locations.routers import router as locations_router
from src.domains.users.routers import profile_router, router as users_router

app = FastAPI(title="GeoSerbia API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations_router)
app.include_router(users_router)
app.include_router(profile_router)
app.include_router(game_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def root():
    return {"message": "GeoSerbia backend is running!"}
