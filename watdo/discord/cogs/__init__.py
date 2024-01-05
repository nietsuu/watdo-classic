from discord.ext import commands as dc
from watdo.logging import get_logger
from watdo.discord import DiscordBot


class BaseCog(dc.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.logger = get_logger(type(self).__name__)
