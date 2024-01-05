from typing import Unpack
from watdo.models import DataModel, DataModelDict


class ProfileDict(DataModelDict):
    pass


class Profile(DataModel):
    def __init__(self, **kwargs: Unpack[ProfileDict]) -> None:
        super().__init__(
            uuid=kwargs["uuid"],
            created_at=kwargs["created_at"],
            created_by=kwargs["created_by"],
        )
