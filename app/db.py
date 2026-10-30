import sqlite3

from app import config

connection = sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)
connection.row_factory = sqlite3.Row


def init():
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT);
        CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner_id INTEGER, title TEXT, body TEXT, archived INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY, note_id INTEGER, name TEXT);
        CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER);
        """
    )


def query(sql, params=()):
    cursor = connection.execute(sql, params)
    return cursor.fetchall()


def execute(sql, params=()):
    connection.execute(sql, params)
    connection.commit()
