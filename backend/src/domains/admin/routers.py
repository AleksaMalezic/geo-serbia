from fastapi import APIRouter, Depends
from src.core.auth import get_current_admin
from src.domains.games import services as game_services
from src.domains.users.models import User
from src.domains.locations.models import Location
from src.domains.games.models import GameSession, Round
from src.utils.response import success_response

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard"])


@router.get("/stats")
async def get_admin_stats(admin=Depends(get_current_admin)):
    total_users = await User.all().count()
    total_admins = await User.filter(is_admin=True).count()
    total_locations = await Location.all().count()
    approved_locations = await Location.filter(is_approved=True).count()
    pending_locations = await Location.filter(is_approved=False).count()
    total_sessions = await GameSession.all().count()
    total_rounds = await Round.all().count()

    return success_response({
        "users": {
            "total": total_users,
            "admins": total_admins,
        },
        "locations": {
            "total": total_locations,
            "approved": approved_locations,
            "pending": pending_locations,
        },
        "game": {
            "sessions": total_sessions,
            "rounds": total_rounds,
        },
    }, message="Admin stats loaded.")


@router.get("/adaptive/stats")
async def get_adaptive_stats(admin=Depends(get_current_admin)):
    stats = await game_services.get_admin_adaptive_stats()
    return success_response(stats, message="Adaptive stats loaded.")
