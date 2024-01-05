import asyncio
from typing import cast, Union
from watdo.models import DataModel
from watdo.logging import get_logger
from watdo.db.connector import DatabaseConnector, FileDatabase

D = Union[
    str,
    int,
    float,
    bool,
    None,
]
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


def _construct_data(parent_path: str, parent_items: list[tuple[str, D]]) -> T:
    items = []

    for key, value in parent_items:
        if not key.startswith(parent_path):
            continue

        try:
            key = key.split(parent_path + ".")[1]
        except IndexError:
            key = ""

        items.append((key, value))

    arr: list["T"] = []
    obj: dict[str, "T"] = {}

    for path, value in items:
        if path == "":
            return value

        keys = path.split(".")
        data = _construct_data(keys[0], items)

        if keys[0].startswith("["):
            index = int(keys[0].strip("[]"))

            if index == -1:
                if data == 0:
                    return []

                continue

            try:
                arr[index] = data
            except IndexError:
                arr.append(data)
        else:
            obj[keys[0]] = data

    return arr or obj or None


def _flatten_data(parent_path: str, data: T) -> list[tuple[str, D]]:
    items = []

    if isinstance(data, dict):
        for k, v in data.items():
            items.extend(_flatten_data(f"{parent_path}.{k}", v))

    elif isinstance(data, list):
        d = data[:]
        d.insert(0, len(data))

        for i, e in enumerate(d, start=-1):
            items.extend(_flatten_data(f"{parent_path}.[{i}]", e))

    else:
        return [(parent_path, cast(D, data))]

    return items


async def get(path: str) -> T:
    global _db

    items = await _db.get(path)

    if len(items) == 0:
        raise KeyError(path)

    return _construct_data(path, items)


async def set(path: str, data: T) -> None:
    global _db

    coros = []

    for key, value in _flatten_data(path, data):
        coros.append(_db.set(key, value))

    await asyncio.gather(*coros)


async def rem(path: str) -> None:
    global _db

    coros = []

    async for path in _db.iter_paths(path):
        coros.append(_db.rem(path))

    if len(coros) == 0:
        raise KeyError(path)

    await asyncio.gather(*coros)


async def set_model(path: str, model: DataModel) -> None:
    data = {**model.__dict__}
    del data["uuid"]

    await model.validate(data)
    await set(path, data)
