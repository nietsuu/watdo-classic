from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


class Tasks(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def task(self, ctx: dc.Context[DiscordBot], *, task: str) -> None:
        """Create a task."""


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Tasks(bot))
