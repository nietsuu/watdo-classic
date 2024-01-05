from typing import Any
import discord
from discord.ext import commands as dc
from watdo.discord import DiscordBot


class BaseCog(dc.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    @staticmethod
    async def send(
        messageable: discord.abc.Messageable,
        content: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> discord.Message:
        if content is None:
            return await messageable.send(*args, **kwargs)

        return await messageable.send(str(content)[:2000], *args, **kwargs)
