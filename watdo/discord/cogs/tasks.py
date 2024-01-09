from discord.ext import commands as dc
from watdo.models.task import Task
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


class Tasks(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def todo(self, ctx: dc.Context[DiscordBot], *, content: str) -> None:
        """Create a task."""
        await Task.new_from_ctx(ctx, content)
        await self.bot.update_sticky(ctx, "Task created ✅")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Tasks(bot))
