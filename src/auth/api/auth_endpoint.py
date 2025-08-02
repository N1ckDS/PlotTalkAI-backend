from fastapi import APIRouter, HTTPException, Depends, Header
from lib.auth.auth import Auth
from lib.models.schemas import UserRegisterRequest, UserLoginRequest, UserResponse
from typing import Optional
from lib.auth.utils import decode_token
import psycopg2
from lib.db.utils import get_auth_service

router = APIRouter()


@router.post("/register", tags=["Auth"])
def register(user: UserRegisterRequest, auth_service: Auth = Depends(get_auth_service)):
    user_id, error = auth_service.register(user.mail, user.name, user.surname, user.password)
    if error == "User already exists":
        raise HTTPException(status_code=400, detail=error)
    if error == "Failed to create user":
        raise HTTPException(status_code=500, detail=error)
    if error:
        raise HTTPException(status_code=422, detail=error)
    return UserResponse(id=user_id, mail=user.mail, name=user.name, surname=user.surname)
    

@router.post("/login", tags=["Auth"])
def login(user: UserLoginRequest, auth_service: Auth = Depends(get_auth_service)):
    login_res = auth_service.login(user.mail, user.password)
    return login_res

@router.get("/protected", tags=["Auth"])
def protected(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, detail="Missing token")
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(401, detail="Invalid token")
    return {"message": f"Hello, {payload.get('mail')}"}

