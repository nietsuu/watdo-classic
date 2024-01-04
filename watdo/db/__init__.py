from typing import Union
from watdo.logging import get_logger
from watdo.db.connector import DatabaseConnector, FileDatabase

T = Union[
    str,
    int,
    float,
    bool,
    None,
    list["T"],
    dict[str, "T"],
]

logger = get_logger("Database")
_db: DatabaseConnector


async def open() -> None:
    global _db
    _db = FileDatabase()
    await _db.open()


async def close() -> None:
    global _db
    await _db.close()
    logger.info("Database closed.")
