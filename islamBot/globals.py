import os
from typing import Optional
import mysql.connector.pooling
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from dotenv import load_dotenv

load_dotenv()


PREFIX = 'ib!'

dbconfig = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME"),
}

def db_connect() -> MySQLConnectionPool:
    try:
        return mysql.connector.pooling.MySQLConnectionPool(
            pool_name="islambot_pool",
            pool_size=20,
            **dbconfig
        )
    except mysql.connector.Error as err:
        print(f"Error creating connection pool: {err}")
        raise

cnxPool = db_connect()

def return_connection_to_pool(connection: Optional[MySQLConnection], cursor: Optional[MySQLCursor]) -> None:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
