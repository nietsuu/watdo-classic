from discord.ext import commands as dc
from watdo import dt
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog
from watdo.models.profile import Profile as ProfileModel


class Profile(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def profile(self, ctx: dc.Context) -> None:
        """Show your profile info."""
        profile = ProfileModel(
            uuid=str(ctx.author.id),
            created_at=dt.ms_now(),
            created_by=str(ctx.author.id),
        )

        await self.send(ctx.channel, profile)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Profile(bot))
