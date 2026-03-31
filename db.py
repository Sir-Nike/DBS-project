import pymysql
from flask import g
from config import Config

def get_db():
    """
    Opens a new DB connection if there isn't one for the current
    Flask application context (g). Reuses it within the same request.
    """
    if 'db' not in g:
        g.db = pymysql.connect(
            host     = Config.DB_HOST,
            user     = Config.DB_USER,
            password = Config.DB_PASSWORD,
            database = Config.DB_NAME,
            cursorclass = pymysql.cursors.DictCursor,  # rows as dicts, not tuples
            autocommit  = False
        )
    return g.db


def close_db(e=None):
    """
    Closes the DB connection at the end of every request.
    Registered in app factory so Flask calls this automatically.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query(sql, args=(), one=False):
    """
    Helper for SELECT queries.
    - one=False  → returns list of dicts
    - one=True   → returns single dict or None
    """
    cur = get_db().cursor()
    cur.execute(sql, args)
    result = cur.fetchall()
    return (result[0] if result else None) if one else result


def execute(sql, args=()):
    """
    Helper for INSERT / UPDATE / DELETE.
    Commits automatically. Returns lastrowid.
    """
    db  = get_db()
    cur = db.cursor()
    cur.execute(sql, args)
    db.commit()
    return cur.lastrowid
