from discord.ext import commands as dc
from watdo.discord import DiscordBot
from watdo.discord.cogs import BaseCog
from watdo.discord.embeds import ProfileEmbed
from watdo.models.profile import Profile as ProfileModel


class Profile(BaseCog):
    @dc.hybrid_command()  # type: ignore[arg-type]
    async def profile(self, ctx: dc.Context) -> None:
        """Show your profile info."""
        profile = await ProfileModel.from_ctx(ctx)
        await self.send(ctx.channel, embed=ProfileEmbed(self.bot, profile))


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Profile(bot))
