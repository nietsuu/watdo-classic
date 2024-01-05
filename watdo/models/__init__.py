import json
import asyncio
from abc import ABC, abstractmethod
from typing import Unpack, TypedDict, Any, Type, Awaitable
from typeddict_validator import validate_typeddict
from watdo.logging import get_logger


class DataModelDict(TypedDict):
    created_at: float
    created_by: str


class DataModel(ABC):
    @staticmethod
    @abstractmethod
    def get_dict_type() -> Type[DataModelDict]:
        raise NotImplementedError

    def __init__(self, uuid: str, **data: Unpack[DataModelDict]) -> None:
        self.uuid = uuid
        self.created_at = data["created_at"]
        self.created_by = data["created_by"]

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    def run_coro(self, coro: Awaitable[None]) -> None:
        async def async_wrapper() -> None:
            try:
                await coro
            except Exception as error:
                get_logger(f"{type(self).__name__}.run_coro").exception(error)

        asyncio.create_task(async_wrapper())

    @classmethod
    async def validate(cls, data: Any) -> None:
        validate_typeddict(data, cls.get_dict_type())
