import os
import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from watdo import db


class DatabaseConnector(ABC):
    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, path: str) -> list[tuple[str, "db.D"]]:
        raise NotImplementedError

    @abstractmethod
    async def set(self, path: str, data: "db.D") -> None:
        raise NotImplementedError


class FileDatabase(DatabaseConnector):
    async def open(self) -> None:
        if not os.path.exists("file_db.json"):
            with open("file_db.json", "w") as file:
                json.dump({}, file)

        self._file = open("file_db.json")

    async def close(self) -> None:
        self._file.close()

    def _read(self) -> list[tuple[str, "db.D"]]:
        self._file.seek(0)
        return [(k, v) for k, v in json.load(self._file).items()]

    async def get(self, path: str) -> list[tuple[str, "db.D"]]:
        data = []

        for key, value in self._read():
            if key.startswith(path):
                data.append((key, value))

        return data

    async def set(self, path: str, data: "db.D") -> None:
        pass
