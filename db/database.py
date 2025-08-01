import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
import json
import logging
import os
from dotenv import load_dotenv
from urllib.parse import urlparse


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='db.log',
    filemode='a'
)
class DatabasePool:
    _pool = None

    @classmethod
    def init_pool(cls):
        cls.dburl = os.getenv('DATABASE_URL')
        cls.dbname = os.getenv('DB_NAME')
        cls.user = os.getenv('DB_USER')
        cls.password = os.getenv('DB_PASSWORD')
        cls.host = os.getenv('DB_HOST')
        cls.port = int(os.getenv('DB_PORT'))
        cls.min_conn = int(os.getenv('MIN_CONN'))
        cls.max_conn = int(os.getenv('MAX_CONN'))
        cls.connect_pool()
    
    def connect_pool(cls):
        try:
            cls._pool = ThreadedConnectionPool(
                minconn=cls.min_conn,
                maxconn=cls.max_conn,
                dsn=cls.dburl,
                sslmode="require"
            )
            logging.info(f"Connection to the database is successful: {cls.host}:{cls.port}/{cls.dbname}")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            raise

    @classmethod
    def check_pool(cls):
        if not cls._pool:
            cls.connect_pool()

    @classmethod
    def get_connection(cls):
        cls.check_pool()
        return cls._pool.getconn()
    
    @classmethod
    def put_connection(cls, conn):
        cls.check_pool()
        return cls._pool.putconn(conn)

# class Database:
#     def __init__(self):
#         self.dbres = os.getenv('DATABASE_URL')
#         self.dbname = os.getenv('DB_NAME')
#         self.user = os.getenv('DB_USER')
#         self.password = os.getenv('DB_PASSWORD')
#         self.host = os.getenv('DB_HOST')
#         self.port = int(os.getenv('DB_PORT'))

#         try:
#             self.db_params = urlparse(self.dbres)
#             self.conn = psycopg2.connect(
#                 self.dbres,
#                 sslmode = "require"
#             )
#             self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
#             logging.info(f"Connection to the database is successful: {self.host}:{self.port}/{self.dbname}")
#         except Exception as e:
#             logging.error(f"Error connecting to the database: {e}")
#             raise

#     def close(self):
#         try:
#             self.cursor.close()
#             self.conn.close()
#             logging.info("The database connection is closed")
#         except Exception as e:
#             logging.error(f"Error closing the connection: {e}")