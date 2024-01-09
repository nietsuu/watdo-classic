import discord
from discord.ext import commands as dc
from watdo.utils import truncate
from watdo.errors import FailCommand
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog


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
        notes = []

        for index, note in enumerate(todo_list.notes):
            notes.append(f"`{index + 1}` {note}")

        await self.bot.update_sticky(ctx, "\n".join(notes))

    @dc.hybrid_command()  # type: ignore[arg-type]
    async def delete_note(self, ctx: dc.Context[DiscordBot]) -> None:
        """Delete a note."""
        todo_list = await self.get_list(ctx)

        if len(todo_list.notes) == 0:
            await self.bot.update_sticky(ctx, "No notes to delete.")
            return

        notes = []

        for index, note in enumerate(todo_list.notes):
            notes.append(f"`{index + 1}` {truncate(note, 50)}")

        await self.bot.update_sticky(ctx, "\n".join(notes))

        async def validate_note_num(message: discord.Message) -> int:
            num = int(message.content)

            if 0 < num < len(todo_list.notes) + 1:
                return num

            raise FailCommand("Note number out of range.")

        note_num = (
            await self.bot.interview(
                ctx,
                questions={
                    "Please type in the note number:": validate_note_num,
                },
            )
        )[0]

        del todo_list.notes[note_num - 1]
        await todo_list.save_changes()
        await self.bot.update_sticky(ctx, "Note deleted ✅")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(RandomNotes(bot))
