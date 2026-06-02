import sqlite3
import os
from config import DATABASE


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def close_db(conn):
    """Safely close database connection"""
    if conn:
        try:
            conn.close()
        except:
            pass