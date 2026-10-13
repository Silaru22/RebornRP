import re

from src.config import settings

_IDENTIFIER = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def table_ref(table_name: str) -> str:
    """Return a safely quoted Teable PostgreSQL schema/table reference."""
    schema = settings.teable_db_schema
    if not _IDENTIFIER.fullmatch(schema):
        msg = 'teable_db_schema must be a valid PostgreSQL identifier'
        raise RuntimeError(msg)
    if not _IDENTIFIER.fullmatch(table_name):
        msg = f'Invalid PostgreSQL table identifier: {table_name!r}'
        raise RuntimeError(msg)
    return f'"{schema}"."{table_name}"'
