import discord
from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog
from watdo.models.list import TodoList
from watdo.models.validators import UTCOffset


class Lists(BaseCog):
    async def _validate_utc_offset(self, message: discord.Message) -> float | None:
        try:
            return UTCOffset(float(message.content)).value
        except Exception:
            await self.bot.send(
                message.channel,
                "Please only send a number between -24 and 24.\n"
                "Example: `8` for UTC+8.",
            )
            return None

    @dc.hybrid_command()  # type: ignore[arg-type]
    async def setup(self, ctx: dc.Context[DiscordBot]) -> None:
        """Setup a todo list in this channel."""
        try:
            await TodoList.from_ctx(ctx)
            await self.bot.update_sticky(ctx, "There's already a list in this channel.")
            return
        except KeyError:
            pass

        utc_offset = (
            await self.bot.interview(
                ctx,
                questions={
                    "What is the UTC offset of this profile?": self._validate_utc_offset,
                },
            )
        )[0]

        await TodoList.new_from_ctx(ctx, utc_offset=utc_offset)
        await self.bot.update_sticky(ctx, "This channel is now under watdo's control.")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Lists(bot))
