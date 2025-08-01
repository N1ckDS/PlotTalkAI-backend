from fastapi import APIRouter, HTTPException, Depends, Request, Header

from db.users_db import Users
from lib.models.schemas import *
from lib.auth.utils import decode_token, get_users_service
import psycopg2
from db.database import DatabasePool

router = APIRouter()

def get_current_user_id(authorization: str = Header(...)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/users/me", tags=["Users"])
def get_user_by_id(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    DatabasePool.put_connection(users_service.db_conn)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/me/data", tags=["Users"])
def get_user_data(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        DatabasePool.put_connection(users_service.db_conn)
        raise HTTPException(status_code=404, detail="User not found")
    data = users_service.get_user_data(user_id)
    DatabasePool.put_connection(users_service.db_conn)
    if data:
        return {"data": data}
    raise HTTPException(status_code=404, detail="User data not found")

@router.post("/users/me/upd/data", tags=["Users"])
def update_user_data(new_data: UserUpdateData, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    print(f"Updating data for user: {user_id}", new_data, sep = "...\n", end="\n\n======\n\n")
    user_data = users_service.get_user_data(user_id)
    if not user_data:
        DatabasePool.put_connection(users_service.db_conn)
        raise HTTPException(status_code=404, detail="User data not found")
    for game_index in range(len(new_data.data.get("games", []))):
        game = new_data.data["games"][game_index]
        for scene_index in range(len(game.get("scenes", []))):
            scene = game["scenes"][scene_index]
            for script_index in range(len(scene.get("scripts", []))):
                try:
                    new_data.data["games"][game_index]["scenes"][scene_index]["scripts"][script_index]["result"] = user_data["games"][game_index]["scenes"][scene_index]["scripts"][script_index]["result"]
                except Exception:
                    pass

    success = users_service.update_user_data(user_id, new_data.data)
    DatabasePool.put_connection(users_service.db_conn)
    if success:
        return {"message": "User data updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update data")

@router.put("/users/me/name", tags=["Users"])
def update_user_name(new_name: UserUpdateName, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        DatabasePool.put_connection(users_service.db_conn)
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.update_user_name(user_id, new_name.name, new_name.surname)
    DatabasePool.put_connection(users_service.db_conn)
    if success:
        return {"message": "User name updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update name")

@router.put("/users/me/password", tags=["Users"])
def update_user_password(new_pass: UserUpdatePassword, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        DatabasePool.put_connection(users_service.db_conn)
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.update_user_password(user_id, new_pass.password_hash)
    DatabasePool.put_connection(users_service.db_conn)
    if success:
        return {"message": "Password updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update password")

@router.delete("/users/me", tags=["Users"])
def delete_user(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        DatabasePool.put_connection(users_service.db_conn)
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.delete_user(user_id)
    DatabasePool.put_connection(users_service.db_conn)
    if success:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete user")
