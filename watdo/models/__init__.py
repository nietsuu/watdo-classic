import json
from abc import ABC
from typing import Unpack, TypedDict


class DataModelDict(TypedDict):
    uuid: str
    created_at: float
    created_by: str


class DataModel(ABC):
    def __init__(self, **kwargs: Unpack[DataModelDict]) -> None:
        self.uuid = kwargs["uuid"]
        self.created_at = kwargs["created_at"]
        self.created_by = kwargs["created_by"]

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=4)
