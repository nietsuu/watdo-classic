from typing import Any
import discord
from watdo.discord import DiscordBot


class Embed(discord.Embed):
    def __init__(self, bot: DiscordBot, title: str, **kwargs: Any) -> None:
        if kwargs.get("color") is None:
            kwargs["color"] = bot.color

        super().__init__(title=title, **kwargs)
