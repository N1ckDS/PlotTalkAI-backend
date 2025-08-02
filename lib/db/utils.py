from db.users_db import Users
from lib.auth.auth import Auth
from db.database import DatabasePool
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from dotenv import load_dotenv
import os
from contextlib import wraps
import logging

load_dotenv(override=True)

def get_users_service():
    with DatabasePool.connection() as conn:
        yield Users(conn)

def get_auth_service():
    with DatabasePool.connection() as conn:
        yield Auth(conn)

def get_db_retry():
    max_attempts = os.getenv('MAX_DATABASE_TRANSACTION_ATEMPTS')
    max_wait_time = os.getenv('MAX_DATABASE_TRANSACTION_WAIT_TIME')
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(max_wait_time)
    )

def db_retry_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return get_db_retry()(func)(*args, **kwargs)
        except RetryError as e:
            # Логируем все неудачные попытки
            logging.error(f"Database overload after multiple retries: {e}")
            raise HTTPException(
                status_code=503,
                detail="Database overload after multiple retries"
            )
    return wrapper