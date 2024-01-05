from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


class RandomNotes(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def note(self, ctx: dc.Context[DiscordBot], *, note: str) -> None:
        """Write a random note to remember."""


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(RandomNotes(bot))
