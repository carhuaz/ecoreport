import os
import sys
from contextlib import contextmanager

if sys.platform.startswith('win'):
    import pyodbc
    from .config import CONNECTION_STRING

    def get_connection():
        return pyodbc.connect(CONNECTION_STRING)

    _USE_QMARK = True
else:
    import pymssql

    def get_connection():
        return pymssql.connect(
            server=os.environ.get("DB_SERVER", "localhost"),
            database=os.environ.get("DB_NAME", "EcoReportDB"),
            user=os.environ.get("DB_USER", "sa"),
            password=os.environ.get("DB_PASSWORD", "continental"),
            tds_version="7.4"
        )

    _USE_QMARK = pymssql.paramstyle == 'qmark'


def _fix_qmark(query: str) -> str:
    return query if _USE_QMARK else query.replace('?', '%s')


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(_fix_qmark(query), params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def fetch_one(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(_fix_qmark(query), params)
        columns = [col[0] for col in cursor.description] if cursor.description else None
        row = cursor.fetchone()
        if row and columns:
            return dict(zip(columns, row))
        return None


def execute(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(_fix_qmark(query), params)
        return cursor.rowcount


def execute_returning_id(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(_fix_qmark(query), params)
        cursor.execute("SELECT @@IDENTITY AS id")
        row = cursor.fetchone()
        return int(row[0]) if row else None
