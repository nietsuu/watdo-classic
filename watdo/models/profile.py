from typing import Unpack, Any, Type
from discord.ext import commands as dc
from watdo import dt, db
from watdo.models import DataModel, DataModelDict


class ProfileDict(DataModelDict):
    pass


class Profile(DataModel):
    @staticmethod
    def get_dict_type() -> Type[ProfileDict]:
        return ProfileDict

    @classmethod
    async def from_ctx(cls, ctx: dc.Context) -> "Profile":
        uuid = str(ctx.author.id)

        try:
            data: Any = await db.get(f"profiles.{uuid}")
            profile = Profile(**data)
        except KeyError:
            profile = Profile(
                uuid=uuid,
                created_at=dt.ms_now(),
                created_by=uuid,
            )
            await db.set_model(f"profiles.{uuid}", profile)

        return profile

    def __init__(self, **kwargs: Unpack[ProfileDict]) -> None:
        super().__init__(
            uuid=kwargs["uuid"],
            created_at=kwargs["created_at"],
            created_by=kwargs["created_by"],
        )
