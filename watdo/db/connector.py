import os
import json
from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set(self) -> None:
        raise NotImplementedError


class FileDatabase(DatabaseConnector):
    async def open(self) -> None:
        if not os.path.exists("file_db.json"):
            with open("file_db.json", "w") as file:
                json.dump({}, file)

        self._file = open("file_db.json")

    async def close(self) -> None:
        self._file.close()
