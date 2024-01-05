from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


class Miscellaneous(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def ping(self, ctx: dc.Context) -> None:
        """Show watdo's brain processing speed."""
        await self.send(ctx, f"Pong! **{round(self.bot.latency * 1000)}ms**")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Miscellaneous(bot))
