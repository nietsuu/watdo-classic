from typing import Type, Any, Unpack, Optional
from discord.ext import commands as dc
from watdo import db, dt
from watdo.models import DataModel, DataModelDict


class TodoListDict(DataModelDict):
    guild_id: Optional[int]
    sticky_message_id: Optional[int]
    utc_offset: float


class TodoList(DataModel):
    @staticmethod
    def get_dict_type() -> Type[TodoListDict]:
        return TodoListDict

    @classmethod
    async def from_ctx(cls, ctx: dc.Context) -> "TodoList":
        uuid = str(ctx.channel.id)
        data: Any = await db.get(f"lists.{uuid}")
        return cls(uuid, **data)

    @classmethod
    async def new_from_ctx(cls, ctx: dc.Context, *, utc_offset: float) -> "TodoList":
        uuid = str(ctx.channel.id)
        todo_list = cls(
            uuid,
            created_at=dt.ms_now(),
            created_by=str(ctx.author.id),
            guild_id=ctx.guild.id if ctx.guild else None,
            sticky_message_id=None,
            utc_offset=utc_offset,
        )
        await db.set_model(f"lists.{uuid}", todo_list)
        return todo_list

    def __init__(self, uuid: str, **data: Unpack[TodoListDict]) -> None:
        super().__init__(
            uuid,
            created_at=data["created_at"],
            created_by=data["created_by"],
        )
        self.guild_id = data["guild_id"]
        self.sticky_message_id = data["sticky_message_id"]
        self.utc_offset = data["utc_offset"]

    async def set_sticky_message_id(self, value: Optional[int]) -> None:
        self.sticky_message_id = value
        await db.set_model(f"lists.{self.uuid}", self)
