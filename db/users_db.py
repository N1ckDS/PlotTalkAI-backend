from pydantic import EmailStr

from db.database import Database
from db.logging import logger
import json 

class Users:
    def __init__(self, db: Database):
        self.db = db

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
            if not isinstance(data, str):
                data_json = json.dumps(data)
            else:
                data_json = data
            self.db.cursor.execute(
                """
                INSERT INTO users_data (mail, name, surname, password_hash, is_deleted, data)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (mail, name, surname, password_hash, is_deleted, data_json)
            )
            user_id = self.db.cursor.fetchone()["id"]
            print("Register", user_id)
            self.db.conn.commit()
            logger.info(f"The user has been created: {user_id} ({name})")
            return user_id
        except Exception as e:
            logger.error(f"Error when creating user {name}: {e}")
            self.db.conn.rollback()

    def get_user_by_mail(self, mail: EmailStr):
        try:
            self.db.cursor.execute("SELECT * FROM users_data WHERE mail = %s;", (mail,))
            user = self.db.cursor.fetchone()
            logger.info(f"Received user by mail: {mail}")
            if user and user.get('is_deleted'):
                return None
            return user
        except Exception as e:
            logger.error(f"Error when receiving user by mail {mail}: {e}")

    def get_user_by_id(self, user_id: int):
        try:
            self.db.cursor.execute("SELECT * FROM users_data WHERE id = %s;", (user_id,))
            user = self.db.cursor.fetchone()
            logger.info(f"Received user by id: {user_id}")
            if not user and user.get('is_deleted'):
                return None
            return user
        except Exception as e:
            logger.error(f"Error when receiving user by id {user_id}: {e}")

    def get_user_data(self, user_id: int):
        try:
            self.db.cursor.execute("SELECT data FROM users_data WHERE id = %s;", (user_id,))
            row = self.db.cursor.fetchone()
            logger.info(f"Received data for user {user_id}")
            return row["data"] if row else None
        except Exception as e:
            logger.error(f"Error when receiving data for user {user_id}: {e}")

    def update_user_data(self, user_id: int, new_data: dict):
        try:
            self.db.cursor.execute(
                "UPDATE users_data SET data = %s WHERE id = %s;",
                (json.dumps(new_data), user_id)
            )
            self.db.conn.commit()
            logger.info(f"Updated data for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating data for user {user_id}: {e}")
            self.db.conn.rollback()
            return False 

    def update_user_name(self, user_id: int, new_name: str, new_surname: str):
        try:
            self.db.cursor.execute(
                "UPDATE users_data SET name = %s, surname = %s WHERE id = %s;",
                (new_name, new_surname, user_id)
            )
            self.db.conn.commit()
            logger.info(f"User name {user_id} updated ")
            return True
        except Exception as e:
            logger.error(f"Error updating user name {user_id}: {e}")
            self.db.conn.rollback()

    def update_user_password(self, user_id: int, new_pass: str):
        try:
            self.db.cursor.execute(
                "UPDATE users_data SET password_hash = %s WHERE id = %s;",
                (new_pass, user_id)
            )
            self.db.conn.commit()
            logger.info(f"Password updated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            self.db.conn.rollback()

    def delete_user(self, user_id: int):
        try:
            self.db.cursor.execute("UPDATE users_data SET is_deleted = %s WHERE id = %s;",
                (True, user_id))
            self.db.conn.commit()
            logger.info(f"User {user_id} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            self.db.conn.rollback()

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
            self.db.cursor.execute(
                """
                UPDATE users_data SET name = %s, surname = %s, password_hash = %s, is_deleted = %s, data = %s WHERE mail = %s RETURNING id;
                """,
                (name, surname, password_hash, False, data_json, mail)
            )
            user_id = self.db.cursor.fetchone()["id"]
            self.db.conn.commit()
            logger.info(f"User reactivated: {user_id} ({name})")
            return user_id
        except Exception as e:
            logger.error(f"Error reactivating user {name}: {e}")
            self.db.conn.rollback()
