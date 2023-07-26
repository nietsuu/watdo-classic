from typing import Any
import discord
from app.discord import Bot


class Embed(discord.Embed):
    def __init__(self, bot: Bot, title: str, **kwargs: Any) -> None:
        super().__init__(title=title, color=bot.color, **kwargs)