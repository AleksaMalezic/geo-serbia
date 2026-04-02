from fastapi import Depends, HTTPException, Request, status
from jose import JWTError

from src.core.security import decode_access_token, is_jti_revoked
from src.core.settings import settings
from src.domains.users.models import User


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )


async def get_current_user(request: Request) -> User:
    # Protected endpoints authenticate using the access token stored in
    # an HTTP-only cookie instead of Authorization header bearer tokens.
    token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if not token:
        raise _credentials_exception()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        token_type = payload.get("type")
        sub = payload.get("sub")
        jti = payload.get("jti")
        if token_type != "access" or sub is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Token revocation is enforced by JTI blacklist lookup on every request.
    if await is_jti_revoked(jti):
        raise credentials_exception

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception

    user = await User.filter(id=user_id, is_active=True).first()
    if not user:
        raise credentials_exception
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
