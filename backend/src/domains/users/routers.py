from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError

from src.core.auth import get_current_user
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    extract_exp_as_datetime,
    is_jti_revoked,
    revoke_jti,
)
from src.core.settings import settings
from src.domains.users import schemas, services
from src.domains.users.models import User
from src.domains.games import services as game_services
from src.utils.response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
profile_router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


def _set_auth_cookies(response: Response, user_id: int) -> None:
    access_token = create_access_token(user_id=user_id)
    refresh_token = create_refresh_token(user_id=user_id)

    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


def _set_access_cookie(response: Response, user_id: int) -> None:
    access_token = create_access_token(user_id=user_id)
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")


@router.post("/register")
async def register_user(user: schemas.UserCreate):
    if await User.filter(username=user.username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
            )
        
    if await User.filter(email=user.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail already exists."
            ) 
    
    created = await services.create_user(
        username=user.username,
        email=user.email,
        password=user.password,
    )
    serialized = schemas.UserRead.model_validate(created).model_dump()
    return success_response(serialized, message="User registered.")


@router.post("/login")
async def login_user(credentials: schemas.UserLogin, response: Response):
    user = await services.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    _set_auth_cookies(response, user.id)
    return success_response({}, message="Login successful")


@router.post("/refresh")
async def refresh_access_token(request: Request, response: Response):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    jti = payload.get("jti")
    if not jti or await is_jti_revoked(jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await User.filter(id=user_id, is_active=True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Current design refreshes only access token and keeps existing refresh token.
    _set_access_cookie(response, user.id)
    return success_response({}, message="Access token refreshed")


@router.post("/logout")
async def logout(request: Request, response: Response):
    access_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)

    if access_token:
        try:
            payload = decode_access_token(access_token)
            jti = payload.get("jti")
            if jti:
                await revoke_jti(
                    jti=jti,
                    token_type="access",
                    expires_at=extract_exp_as_datetime(payload),
                )
        except JWTError:
            pass

    if refresh_token:
        try:
            payload = decode_refresh_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                await revoke_jti(
                    jti=jti,
                    token_type="refresh",
                    expires_at=extract_exp_as_datetime(payload),
                )
        except JWTError:
            pass

    _clear_auth_cookies(response)
    return success_response({}, message="Logged out")


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    stats = await services.get_user_stats(current_user.id)
    return success_response({
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "joined": current_user.created_at,
        "stats": stats,
    }, message="Profile loaded.")


@profile_router.get("/adaptive-stats")
async def get_adaptive_stats(current_user: User = Depends(get_current_user)):
    data = await game_services.get_user_adaptive_stats(current_user.id)
    return success_response(data, message="Adaptive stats loaded.")
