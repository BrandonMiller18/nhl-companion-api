from typing import Any

import mysql.connector

from .config import get_env


def get_db_connection():  # type: ignore[no-untyped-def]
    return mysql.connector.connect(
        host=get_env("DB_HOST", "127.0.0.1"),
        port=int(get_env("DB_PORT", "3306")),
        user=get_env("DB_USER", "root"),
        password=get_env("DB_PASSWORD", ""),
        database=get_env("DB_NAME"),
        autocommit=True,
    )


