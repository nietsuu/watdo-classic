from typing import TYPE_CHECKING, Any, Type
from discord.ext import commands as dc
from watdo import dt, db
from watdo.models import DataModel, DataModelDict

if TYPE_CHECKING:
    from watdo.discord import DiscordBot


class ProfileDict(DataModelDict):
    pass


class Profile(DataModel):
    @staticmethod
    def get_dict_type() -> Type[ProfileDict]:
        return ProfileDict

    @classmethod
    async def from_ctx(cls, ctx: dc.Context["DiscordBot"]) -> "Profile":
        uuid = str(ctx.author.id)

        try:
            data: Any = await db.get(f"profiles.{uuid}")
            profile = cls(uuid, **data)
        except KeyError:
            profile = cls(
                uuid,
                created_at=dt.ms_now(),
                created_by=uuid,
            )
            await db.set_model(f"profiles.{uuid}", profile)

        return profile
