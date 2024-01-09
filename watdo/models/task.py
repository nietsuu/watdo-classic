from typing import Unpack, Optional, Union, Type
from discord.ext import commands as dc
from watdo import db, dt
from watdo.models import DataModel, DataModelDict
from watdo.discord import DiscordBot


class TaskDict(DataModelDict):
    list_uuid: str
    content: str
    tags: list[str]
    due: Union[str, float, None]
    has_reminder: bool
    is_auto_done: bool
    last_done: Optional[float]
    next_reminder: Optional[float]


class Task(DataModel):
    @staticmethod
    def get_dict_type() -> Type[TaskDict]:
        return TaskDict

    @classmethod
    async def new_from_ctx(cls, ctx: dc.Context["DiscordBot"], content: str) -> "Task":
        todo_list = await ctx.bot.get_list(ctx)
        uuid = str(ctx.message.id)
        task = cls(
            uuid,
            created_at=dt.ms_now(),
            created_by=str(ctx.author.id),
            list_uuid=todo_list.uuid,
            content=content,
            tags=[],
            due=None,
            has_reminder=True,
            is_auto_done=False,
            last_done=None,
            next_reminder=None,
        )
        await db.set_model(f"tasks.{uuid}", task)
        return task

    def __init__(self, uuid: str, **data: Unpack[TaskDict]) -> None:
        super().__init__(
            uuid,
            created_at=data["created_at"],
            created_by=data["created_by"],
        )
        self.list_uuid = data["list_uuid"]
        self.content = data["content"]
        self.tags = data["tags"]
        self.due = data["due"]
        self.has_reminder = data["has_reminder"]
        self.is_auto_done = data["is_auto_done"]
        self.last_done = data["last_done"]
        self.next_reminder = data["next_reminder"]

    async def save_changes(self) -> None:
        await db.set_model(f"tasks.{self.uuid}", self)
