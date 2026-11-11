
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.db.database import get_db
from app.models.user import User

from typing import Callable
from app.models.user import User
from fastapi import Depends,HTTPException,status

# Bearer Token Authentication
bearer_scheme = HTTPBearer(auto_error=False)
# is ka kam request ke authorization header sae Bearer token extract krna
# auto errro is liya use kiya ha agr token na mila tu hm handle ko khud handkle krein gy


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    # Check whether token is provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify JWT Access Token
    payload = verify_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract user ID from JWT payload
    try:
        user_id = int(payload["sub"])

    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Fetch current user from database
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    # Check whether user exists and is active
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is inactive"
        )

    return user

def require_role(*allowed_roles:str)->callable:
    #yahan allowed roles ka matlab hai function multiple roles accept krta ha
    def role_checker(
            current_user:User=Depends(get_current_user)
    )->User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to acess this resources"
            )
        return current_user
    return role_checker


