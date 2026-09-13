from __future__ import annotations

import os
from typing import Any

import psycopg


def get_database_url() -> str:
    return os.getenv(
        "GESTION_ATENCION_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/gestion_atencion",
    )


def get_connection(**kwargs: Any) -> psycopg.Connection:
    return psycopg.connect(get_database_url(), **kwargs)
