from discord.ext import commands as dc
from watdo.errors import FailCommand
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog
from watdo.models.list import TodoList


class RandomNotes(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def note(self, ctx: dc.Context[DiscordBot], *, note: str) -> None:
        """Write a random note to remember."""
        todo_list = await TodoList.from_ctx(ctx)

        if todo_list is None:
            raise FailCommand("You need to setup a list for this channel first.")

        todo_list.notes.append(note)
        todo_list.save_changes()
        await self.bot.update_sticky(ctx, "Note added ✅")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(RandomNotes(bot))
