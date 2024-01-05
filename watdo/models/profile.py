from typing import Unpack, Any
from discord.ext import commands as dc
from watdo import dt, db
from watdo.models import DataModel, DataModelDict


class ProfileDict(DataModelDict):
    pass


class Profile(DataModel):
    @classmethod
    async def from_ctx(cls, ctx: dc.Context) -> "Profile":
        uuid = str(ctx.author.id)

        try:
            data: Any = await db.get(f"profiles.{uuid}")
        except KeyError:
            data = {
                "uuid": uuid,
                "created_at": dt.ms_now(),
                "created_by": uuid,
            }
            await db.set(f"profiles.{uuid}", data)

        return Profile(**data)

    def __init__(self, **kwargs: Unpack[ProfileDict]) -> None:
        super().__init__(
            uuid=kwargs["uuid"],
            created_at=kwargs["created_at"],
            created_by=kwargs["created_by"],
        )
