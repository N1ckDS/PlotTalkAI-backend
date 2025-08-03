from fastapi import APIRouter, HTTPException, Depends, Request, Header

from db.users_db import Users
from lib.models.schemas import *
from lib.auth.utils import get_current_user_id
import psycopg2
from lib.db.utils import get_users_service, db_retry_decorator


router = APIRouter()

@router.get("/users/me", tags=["Users"])    
@db_retry_decorator
def get_user_by_id(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/me/data", tags=["Users"])
@db_retry_decorator
def get_user_data(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = users_service.get_user_data(user_id)
    if data:
        return {"data": data}
    raise HTTPException(status_code=404, detail="User data not found")

@router.put("/users/me/upd/data", tags=["Users"])
@db_retry_decorator
def update_user_data(new_data: dict, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    print(f"Updating data for user: {user_id}", new_data, sep = "...\n", end="\n\n======\n\n")
    user_data = users_service.get_user_data(user_id)
    if not user_data:
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
    if success:
        return {"message": "User data updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update data")

@router.put("/users/me/name", tags=["Users"])
@db_retry_decorator
def update_user_name(new_name: UserUpdateName, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.update_user_name(user_id, new_name.name, new_name.surname)
    if success:
        return {"message": "User name updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update name")

@router.put("/users/me/password", tags=["Users"])
@db_retry_decorator
def update_user_password(new_pass: UserUpdatePassword, user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.update_user_password(user_id, new_pass.password_hash)
    if success:
        return {"message": "Password updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update password")

@router.delete("/users/me", tags=["Users"])
@db_retry_decorator
def delete_user(user_id: int = Depends(get_current_user_id), users_service: Users = Depends(get_users_service)):
    user = users_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = users_service.delete_user(user_id)
    if success:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete user")
