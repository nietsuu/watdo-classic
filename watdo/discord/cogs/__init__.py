from discord.ext import commands as dc
from watdo.errors import FailCommand
from watdo.logging import get_logger
from watdo.discord import DiscordBot
from watdo.models.list import TodoList


class BaseCog(dc.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.logger = get_logger(type(self).__name__)

    async def get_list(self, ctx: dc.Context[DiscordBot]) -> TodoList:
        todo_list = await TodoList.from_ctx(ctx)

        if todo_list is None:
            raise FailCommand("You need to setup a list for this channel first.")

        return todo_list
