from pydantic import EmailStr
from fastapi import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from db.database import DatabasePool
from db.logging import logger
import json 

class Users:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_user(self, mail, name, surname, password_hash, is_deleted=False, data=None):
        if not mail or not name or not surname or not password_hash:
            logger.error(f"Error when creating user: missing required fields")
            return None
        if data is None:
            data = {
                "games": [],
                "selectedGameId": None,
                "selectedSceneId": None,
                "selectedScriptId": None,
                "token": None,
                "user": {
                    "firstName": "",
                    "lastName": "",
                    "email": "",
                    "avatar": ""
                }
            }
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                if not isinstance(data, str):
                    data_json = json.dumps(data)
                else:
                    data_json = data
                curs.execute(
                    """
                    INSERT INTO users_data (mail, name, surname, password_hash, is_deleted, data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (mail, name, surname, password_hash, is_deleted, data_json)
                )
                user_id = curs.fetchone().get("id")
                self.db_conn.commit()
                print(f"The user has been created: {user_id} ({mail}, {name})", end="\n\n======\n\n")
                logger.info(f"The user has been created: {user_id} ({name})")
                return user_id
        except Exception as e:
            logger.error(f"Error when creating user {name}: {e}")
            print(f"Error when creating user {mail} ({name}): {e}", end="\n\n======\n\n")
            if self.db_conn: 
                self.db_conn.rollback()
            return None

    def get_user_by_mail(self, mail: EmailStr):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute("SELECT * FROM users_data WHERE mail = %s;", (mail,))
                user = curs.fetchone()
                logger.info(f"Received user by mail: {mail}")
                print(f"Received user by mail: {mail}", user, sep = "\n", end="\n\n======\n\n")
                if not user or user.get('is_deleted'):
                    return None
                return user
        except Exception as e:
            logger.error(f"Error when receiving user by mail {mail}: {e}")
            print(f"Error when receiving user by mail {mail}: {e}", end="\n\n======\n\n")
            return None

    def get_user_by_id(self, user_id: int):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute("SELECT * FROM users_data WHERE id = %s;", (user_id,))
                user = curs.fetchone()
                logger.info(f"Received user by id: {user_id}")
                print(f"Received user by id: {user_id}", user, sep = "\n", end="\n\n======\n\n")
                if not user or user.get('is_deleted'):
                    return None
                return user
        except Exception as e:
            logger.error(f"Error when receiving user by id {user_id}: {e}")
            print(f"Error when receiving user by id {user_id}: {e}", end="\n\n======\n\n")
            return None

    def get_user_data(self, user_id: int):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute("SELECT data FROM users_data WHERE id = %s;", (user_id,))
                row = curs.fetchone()
                logger.info(f"Received data for user {user_id}")
                print(f"Received data for user: {user_id}", row.get("data") if row else None, sep = "\n", end="\n\n======\n\n")
                return row.get("data") if row else None
        except Exception as e:
            logger.error(f"Error when receiving data for user {user_id}: {e}")
            print(f"Error when receiving data for user {user_id}: {e}", end="\n\n======\n\n")
            return None

    def update_user_data(self, user_id: int, new_data: dict):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(
                    "UPDATE users_data SET data = %s WHERE id = %s;",
                    (json.dumps(new_data), user_id)
                )
                self.db_conn.commit()
                logger.info(f"Updated data for user {user_id}")
                print(f"Updated data for user: {user_id}", new_data, sep = "\n", end="\n\n======\n\n")
                return True
        except Exception as e:
            logger.error(f"Error updating data for user {user_id}: {e}")
            print(f"Error updating data for user {user_id}: {e}", end="\n\n======\n\n")
            if self.db_conn:
                self.db_conn.rollback()
            return False 

    def update_user_name(self, user_id: int, new_name: str, new_surname: str):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(
                    "UPDATE users_data SET name = %s, surname = %s WHERE id = %s;",
                    (new_name, new_surname, user_id)
                )
                self.db_conn.commit()
                logger.info(f"User name {user_id} updated ")
                print(f"Updated name for user: {user_id}", new_name, sep = "\n", end="\n\n======\n\n")
                return True
        except Exception as e:
            logger.error(f"Error updating user name {user_id}: {e}")
            print(f"Error updating name for user {user_id}: {e}", end="\n\n======\n\n")
            if self.db_conn:
                self.db_conn.rollback()
            return False

    def update_user_password(self, user_id: int, new_pass: str):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(
                    "UPDATE users_data SET password_hash = %s WHERE id = %s;",
                    (new_pass, user_id)
                )
                self.db_conn.commit()
                logger.info(f"Password updated for user {user_id}")
                print(f"Updated password for user: {user_id}", new_pass, sep = "\n", end="\n\n======\n\n")
                return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            print(f"Error updating password for user {user_id}: {e}", end="\n\n======\n\n")
            self.db_conn.rollback()
            return False

    def update_user_result(self, result: dict, user_id: int, game_id: int, scene_id: int, script_id: int):
        user_data = self.get_user_data(user_id)
        if not user_data:
            DatabasePool.put_connection(self.db_conn)
            raise HTTPException(status_code=404, detail="User data not found")
        if isinstance(user_data, str):
            user_data = json.loads(user_data)
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
                                user_data["games"][game_index]["scenes"][scene_index]["scripts"][script_index]["result"] = result
                                found_script = 1
                                break
                        if not found_script:
                            print("script_id не валидный", end="\n\n======\n\n")
                            DatabasePool.put_connection(self.db_conn)
                            raise HTTPException(status_code=400, detail="script_id не валидный")
                        break
                if not found_scene:
                    print("scene_id не валидный", end="\n\n======\n\n")
                    DatabasePool.put_connection(self.db_conn)
                    raise HTTPException(status_code=400, detail="scene_id не валидный")
                break
        if not found_game:
            print("game_id не валидный", end="\n\n======\n\n")
            DatabasePool.put_connection(self.db_conn)
            raise HTTPException(status_code=400, detail="game_id не валидный")
        return self.update_user_data(user_id, user_data)

    def delete_user(self, user_id: int):
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute("UPDATE users_data SET is_deleted = %s WHERE id = %s;",
                    (True, user_id))
                self.db_conn.commit()
                logger.info(f"User {user_id} deleted")
                print(f"User {user_id} deleted", end="\n\n======\n\n")
                return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            print(f"Error deleting user {user_id}: {e}", end="\n\n======\n\n")
            if self.db_conn:
                self.db_conn.rollback()

    def reactivate_user(self, mail, name, surname, password_hash, data=None):
        try:
            if data is None:
                data = {
                    "games": [],
                    "selectedGameId": None,
                    "selectedSceneId": None,
                    "selectedScriptId": None,
                    "token": None,
                    "user": {
                        "firstName": "",
                        "lastName": "",
                        "email": "",
                        "avatar": ""
                    }
                }
            if not isinstance(data, str):
                data_json = json.dumps(data)
            else:
                data_json = data
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(
                    """
                    UPDATE users_data SET name = %s, surname = %s, password_hash = %s, is_deleted = %s, data = %s WHERE mail = %s RETURNING id;
                    """,
                    (name, surname, password_hash, False, data_json, mail)
                )
                user_id = curs.fetchone()["id"]
                self.db_conn.commit()
                logger.info(f"User reactivated: {user_id} ({name})")
                print(f"User {mail} ({name}) reactivated", end="\n\n======\n\n")
                return user_id
        except Exception as e:
            logger.error(f"Error reactivating user {name}: {e}")
            print(f"Error reactivating user {mail} ({name}): {e}", end="\n\n======\n\n")
            if self.db_conn:
                self.db_conn.rollback()
            return None
