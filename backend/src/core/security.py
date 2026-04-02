from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.settings import settings
from src.domains.users.models import TokenBlacklist

# Argon2 is the default production-grade password hasher in this project.
# Parameters are configurable from settings for environment-specific tuning.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=settings.ARGON2_TIME_COST,
    argon2__memory_cost=settings.ARGON2_MEMORY_COST,
    argon2__parallelism=settings.ARGON2_PARALLELISM,
)

# Dummy hash used to normalize timing for non-existing users during login.
# This avoids leaking account existence through response time differences.
DUMMY_PASSWORD_HASH = pwd_context.hash("dummy-password-for-timing-normalization")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def dummy_verify_password(plain_password: str) -> None:
    # Intentionally ignore result: this is only for timing normalization.
    pwd_context.verify(plain_password, DUMMY_PASSWORD_HASH)


def _build_payload(
    user_id: int,
    token_type: str,
    expires_delta: timedelta,
) -> dict:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    return {
        "sub": str(user_id),
        "jti": str(uuid4()),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }


def create_access_token(user_id: int) -> str:
    payload = _build_payload(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(payload, settings.ACCESS_TOKEN_SECRET, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = _build_payload(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return jwt.encode(payload, settings.REFRESH_TOKEN_SECRET, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.ACCESS_TOKEN_SECRET, algorithms=[settings.ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.REFRESH_TOKEN_SECRET, algorithms=[settings.ALGORITHM])


async def is_jti_revoked(jti: str) -> bool:
    return await TokenBlacklist.filter(jti=jti).exists()


async def revoke_jti(jti: str, token_type: str, expires_at: datetime) -> None:
    await TokenBlacklist.get_or_create(
        jti=jti,
        defaults={
            "token_type": token_type,
            "expires_at": expires_at,
        },
    )


def extract_exp_as_datetime(payload: dict) -> datetime:
    exp = payload.get("exp")
    if isinstance(exp, (int, float)):
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    raise JWTError("Token missing exp")
