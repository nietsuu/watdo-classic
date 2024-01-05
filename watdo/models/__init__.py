import json
from abc import ABC, abstractmethod
from typing import Unpack, TypedDict, Any, Type
from typeddict_validator import validate_typeddict


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

    @classmethod
    async def validate(cls, data: Any) -> None:
        validate_typeddict(data, cls.get_dict_type())
