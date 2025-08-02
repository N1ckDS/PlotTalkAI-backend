import psycopg2
from psycopg2.pool import ThreadedConnectionPool, PoolError
from fastapi import HTTPException
from psycopg2.extras import RealDictCursor
import json
import logging
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from fastapi import Depends
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='db.log',
    filemode='a'
)

class DatabasePool:
    _pool = None
    _config = None
    @classmethod
    def init_pool(cls):
        cls._config = {
            'dburl': os.getenv('DATABASE_URL')+"?pgbouncer_mode=transaction",
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'min_conn': int(os.getenv('MIN_CONN', 1)),
            'max_conn': int(os.getenv('MAX_CONN', 10))
        }
        cls.connect_pool()
    
    @classmethod
    def connect_pool(cls):
        try:
            cls._pool = ThreadedConnectionPool(
                minconn=cls._config["min_conn"],
                maxconn=cls._config["max_conn"],
                dsn=cls._config["dburl"],
                sslmode="require"
            )
            logging.info(f"Pool connected: {cls._config}")
        except Exception as e:
            logging.error(f"Pool connection failed: {e}")
            raise

    @classmethod
    def check_pool(cls):
        if not cls._pool:
            cls.init_pool()

    @classmethod
    @contextmanager
    def connection(cls):
        cls.check_pool()
        try:
            conn = cls._pool.getconn()
            logging.debug(f"Connection acquired ({len(cls._pool._used)} used, {len(cls._pool._rused)} free)")
            yield conn
        except PoolError as e:
            logging.error(f"Pool exhausted: {e}")
            raise HTTPException(503, detail="Database is overloaded")
        finally:
            try:
                if 'conn' in locals() and not conn.closed:
                    cls._pool.putconn(conn)
                    logging.debug(f"Connection returned ({len(cls._pool._used)} used, {len(cls._pool._rused)} free)")
            except Exception as e:
                logging.error(f"Error returning connection: {e}")


    @classmethod
    def close_all(cls, conn):
        if cls._pool:
            cls._pool.closeall()
