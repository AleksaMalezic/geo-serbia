from fastapi import APIRouter, Depends

from src.core.auth import get_current_user
from src.domains.games import services
from src.domains.users.models import User
from src.utils.response import success_response

router = APIRouter(prefix="/api/v1/game", tags=["Game"])


@router.post("/start")
async def start_challenge(
    mode: str = "adaptive",
    current_user: User = Depends(get_current_user),
):
    result = await services.start_challenge(current_user.id, mode=mode)
    return success_response(result, message="Challenge started.")


@router.post("/hint")
async def get_hint(
    location_id: int,
    hints_used_count: int = 0,
    current_user: User = Depends(get_current_user),
):
    result = await services.get_hint(current_user.id, location_id, hints_used_count)
    return success_response(result, message="Hint provided.")


@router.post("/play")
async def play_round(
    location_id: int,
    guessed_latitude: float,
    guessed_longitude: float,
    hints_used_count: int = 0,
    current_user: User = Depends(get_current_user),
):
    result = await services.play_round(
        current_user.id,
        location_id,
        guessed_latitude,
        guessed_longitude,
        hints_used_count=hints_used_count,
    )
    return success_response(result, message="Round played.")


@router.get("/leaderboard/daily")
async def daily_leaderboard():
    return success_response(await services.get_daily_leaderboard(), message="Daily leaderboard listed.")


@router.get("/leaderboard/monthly")
async def montly_leaderboard():
    return success_response(await services.get_monthly_leaderboard(), message="Monthly leaderboard listed.")
