from typing import TYPE_CHECKING, Any
import discord
from watdo.models.profile import Profile

if TYPE_CHECKING:
    from watdo.discord import DiscordBot


class Embed(discord.Embed):
    def __init__(self, bot: "DiscordBot", title: str, **kwargs: Any) -> None:
        if kwargs.get("color") is None:
            kwargs["color"] = bot.color

        super().__init__(title=title, **kwargs)


class ProfileEmbed(Embed):
    def __init__(self, bot: "DiscordBot", profile: Profile) -> None:
        user = bot.get_user(int(profile.uuid))
        super().__init__(bot, user.display_name if user else profile.uuid)

        if user is not None:
            self.set_thumbnail(url=user.display_avatar.url)
