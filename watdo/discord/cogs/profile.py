from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


class Profile(BaseCog):
    pass


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Profile(bot))
