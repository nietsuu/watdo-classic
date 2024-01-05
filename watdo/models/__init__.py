import json
from abc import ABC, abstractmethod
from typing import Unpack, TypedDict, Any, Type
from typeddict_validator import validate_typeddict


class DataModelDict(TypedDict):
    uuid: str
    created_at: float
    created_by: str


class DataModel(ABC):
    @staticmethod
    @abstractmethod
    def get_dict_type() -> Type[DataModelDict]:
        raise NotImplementedError

    def __init__(self, **kwargs: Unpack[DataModelDict]) -> None:
        self.uuid = kwargs["uuid"]
        self.created_at = kwargs["created_at"]
        self.created_by = kwargs["created_by"]

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    @classmethod
    async def validate(cls, data: Any) -> None:
        validate_typeddict(data, cls.get_dict_type())
