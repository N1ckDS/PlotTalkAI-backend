from fastapi import APIRouter, Depends, HTTPException, Header, HTTPException
from lib.models.schemas import Params
from lib.llm.generator import Orchestrator
from db.database import DatabasePool
from db.users_db import Users
from src.db.api.db_endpoint import get_current_user_id
from psycopg2.extensions import connection as Connection
import json 
router = APIRouter()

def get_users_service(db_conn: Connection = Depends(DatabasePool.get_connection)):
    return Users(db_conn) 

class DialogueController:
    def __init__(self):
        self.generator_class = Orchestrator

    def generate(self, params: Params):
        generator = self.generator_class(params.dict())
        return generator.create_dialog()

dialogue_controller = DialogueController()

@router.post("/generate", tags=["Dialogue"])
def generate(params: Params, user_id: int = Depends(get_current_user_id)):
    # берём соединение из пула
    db_conn = DatabasePool.get_connection()
    users_service = Users(db_conn)
    a = dialogue_controller.generate(params)
    # a = {"x": 1}
    # time.sleep(5)
    # try:
    #     a_dict = json.loads(a)
    # except Exception:
    #     raise HTTPException(status_code=500, detail="Failed to parse generated dialogue")
    print(f"Generated  script for user: {user_id}", a, sep = "\n", end="\n\n======\n\n")
    user_data = users_service.get_user_data(user_id)
    if not user_data:
        DatabasePool.put_connection(db_conn)
        raise HTTPException(status_code=404, detail="User data not found")

    if isinstance(user_data, str):
        user_data = json.loads(user_data)

    game_id = params.game_id
    scene_id = params.scene_id
    script_id = params.script_id
    if script_id is None:
        print("script_id должен быть передан в params или я в чем-то ошибся, анлак", end="\n\n======\n\n")
        raise HTTPException(status_code=400, detail="script_id должен быть передан в params или я в чем-то ошибся, анлак")
    if game_id is None:
        print("game_id должен быть передан в params или я в чем-то ошибся, анлак", end="\n\n======\n\n")
        raise HTTPException(status_code=400, detail="game_id должен быть передан в params или я в чем-то ошибся, анлак")
    if scene_id is None:
        print("scene_id должен быть передан в params или я в чем-то ошибся, анлак", end="\n\n======\n\n")
        raise HTTPException(status_code=400, detail="scene_id должен быть передан в params или я в чем-то ошибся, анлак")
    # Поиск по структуре
    # for game in user_data.get("games", []):
    #     if str(game.get("id")) == str(game_id):
    #         for scene in game.get("scenes", []):
    #             if str(scene.get("id")) == str(scene_id):
    #                 # if "scripts" not in scene:
    #                 #     scene["scripts"] = []

    #                 found_script = False
    #                 for script in scene.get("scripts", []):
    #                     if str(script.get("id")) == str(script_id):
    #                         script["result"] = a
    #                         found_script = True
    #                         break
    #                 if not found_script:
    #                     raise HTTPException(status_code=400, detail="script_id не валидный")
    #                 break
    #         break
    found_game = 0
    for game_index in range(len(user_data.get("games", []))):
        game = user_data["games"][game_index]
        if str(game.get("id")) == str(game_id):
            found_game = 1
            found_scene = 0
            for scene_index in range(len(game.get("scenes", []))):
                scene = game["scenes"][scene_index]
                if str(scene.get("id")) == str(scene_id):
                    found_scene = 1
                    found_script = 0
                    for script_index in range(len(scene.get("scripts", []))):
                        script = scene["scripts"][script_index]
                        if str(script.get("id")) == str(script_id):
                            user_data["games"][game_index]["scenes"][scene_index]["scripts"][script_index]["result"] = a
                            found_script = 1
                            break
                    if not found_script:
                        print("script_id не валидный", end="\n\n======\n\n")
                        DatabasePool.put_connection(db_conn)
                        raise HTTPException(status_code=400, detail="script_id не валидный")
                    break
            if not found_scene:
                print("scene_id не валидный", end="\n\n======\n\n")
                DatabasePool.put_connection(db_conn)
                raise HTTPException(status_code=400, detail="scene_id не валидный")
            break
    if not found_game:
        print("game_id не валидный", end="\n\n======\n\n")
        DatabasePool.put_connection(db_conn)
        raise HTTPException(status_code=400, detail="game_id не валидный")
                        
    success = users_service.update_user_data(user_id, user_data)
    DatabasePool.put_connection(db_conn)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update user data")
    
    return {"ok": True}
