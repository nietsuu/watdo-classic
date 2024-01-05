from discord.ext import commands as dc
from watdo.discord import DiscordBot


class BaseCog(dc.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
