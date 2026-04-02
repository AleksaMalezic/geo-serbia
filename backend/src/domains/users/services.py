from src.domains.users.models import User
from src.core.security import (
    dummy_verify_password,
    hash_password,
    verify_password,
)
from src.domains.games.models import GameSession, Round
from tortoise.functions import Sum
from tortoise.expressions import Q

async def create_user(username: str, email: str, password: str):
    hashed = hash_password(password)
    user = await User.create(username=username, email=email, hashed_password=hashed)
    return user

async def authenticate_user(username: str, password: str):
    user = await User.filter(Q(username=username) | Q(email=username)).first()
    if not user:
        # Keep timing similar for missing users to reduce account enumeration risk.
        dummy_verify_password(password)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_user_stats(user_id: int):
    total_sessions = await GameSession.filter(user_id=user_id).count()
    total_rounds = await Round.filter(session__user_id=user_id).count()
    total_score = await GameSession.filter(user_id=user_id).annotate(s=Sum("total_score")).values_list("s", flat=True)
    total_score = total_score[0] if total_score and total_score[0] else 0
    
    avg_score = 0
    if total_rounds > 0:
        avg_score = round(total_score / total_rounds, 2)
        
    last_activity = (
        await Round.filter(session__user_id=user_id).order_by("-created_at").first()
    )
    last_played = last_activity.created_at if last_activity else None
    
    return {
        "total_sessions": total_sessions,
        "total_rounds": total_rounds,
        "total_score": int(total_score),
        "average_score": avg_score,
        "last_played": last_played,
    }
