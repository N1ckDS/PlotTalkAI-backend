from db.users_db import Users
from lib.auth.auth import Auth
import psycopg2
from db.database import DatabasePool
from fastapi import Depends
def get_users_service(db_conn: psycopg2.extensions.connection = Depends(DatabasePool.get_connection)):
    return Users(db_conn) 

def get_auth_service(db_conn: psycopg2.extensions.connection = Depends(DatabasePool.get_connection)):
    return Auth(db_conn) 