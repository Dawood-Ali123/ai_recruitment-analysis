#password ko hash krny ky liya hm Argon2 use krein gy
#Pyjwt ko hm JWT generate krny or verify krnuy ky liya use krein gy

from datetime import datetime,timedelta,timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings
import secrets
import hashlib

#cryptographically secure random token generate krta ha
#hashlib Refresh token SHA-256 hash calculate krta ha


#password hash
password_hash=PasswordHash.recommended()
#yahan hm pwdlib ka password hash object use kr rahy han 
# recommended  password hashing configuration min argon2id use hota ha
def hash_password(password:str)->str:
    """
    Convert the plian password into a secure hash
    """
    return password_hash.hash(password)

def verify_password(
        plain_password:str,
        hashed_password:str
)->bool:
    """
    Verify a plain password against its stored hash
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )

def create_access_token(
        user_id:int,
        role:str
)->str:
    now=datetime.now(timezone.utc)
    expire=now+timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload={
        "sub":str(user_id),
        "role":role,
        "type":"access",
        "iat":now,
        "exp":expire
    }
    token=jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token

def verify_access_token(token:str)->dict|None:
    try:
        payload=jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require":['exp','sub','iat']
            }
        )
        if payload.get("type")!="access":
            return None
        return payload
    except jwt.InvalidTokenError:
        return None

def create_refresh_token()->str:
    """
    Generate a cryptographically secure random refresh token.
    """
    return secrets.token_urlsafe(48)

    
def hash_refresh_token(token:str)->str:
    """Hash refresh token using the SHA-256"""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

"""
token.encode(utf-8) string ko bytes me convert krta ha 
phr hashlib.sha256() in bytes par kam krta ha or hash me convert krta ha
.hexdigest() hash ko readable hexadecimal string mein convert krta hao
"""