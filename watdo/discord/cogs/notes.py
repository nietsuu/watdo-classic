import discord
from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog
from watdo.discord.embeds import Embed, PagedEmbed


class RandomNotes(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def note(self, ctx: dc.Context[DiscordBot], *, note: str) -> None:
        """Write a random note to remember."""
        todo_list = await self.get_list(ctx)
        todo_list.notes.append(note)
        await todo_list.save_changes()
        await self.bot.update_sticky(ctx, "Note added ✅")

    @dc.hybrid_command()  # type: ignore[arg-type]
    async def notes(self, ctx: dc.Context[DiscordBot]) -> None:
        """List all your notes."""
        todo_list = await self.get_list(ctx)

        async def embeds_getter() -> tuple[discord.Embed, ...]:
            return tuple(
                Embed(
                    self.bot,
                    f"Note {index + 1}",
                    description=note,
                )
                for index, note in enumerate(todo_list.notes)
            )

        paged_embed = PagedEmbed(ctx, embeds_getter)
        await paged_embed.send()


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(RandomNotes(bot))
