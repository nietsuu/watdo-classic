import asyncio
import discord
from discord.ext import commands as dc
from app.discord import Bot
from app.database import Database


class BaseCog(dc.Cog):
    def __init__(self, bot: Bot, database: Database) -> None:
        self.bot = bot
        self.db = database

    @staticmethod
    def parse_params(command: dc.Command) -> str:
        params = []

        for param in command.clean_params.values():
            t = param.annotation

            if t is bool:
                t = "yes/no"

            if t in (int, float):
                t = "number"

            if "typing.Optional[" in str(t):
                t = str(t).lstrip("typing.Optional[").rstrip("]")

            t = f"*{t}*"
            p = param.name if param.annotation is str else f"{param.name}: {t}"
            p = p.replace("_", " ")

            if param.required:
                p = f"**[{p}]**"
            else:
                p = f"[{p}]"

            params.append(p)

        return " ".join(params)

    async def wait_for_confirmation(
        self, ctx: dc.Context, message: discord.Message
    ) -> bool:
        buttons = ("✅", "❌")

        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            if user.id == ctx.author.id:
                if reaction.message.id == message.id:
                    if str(reaction) in buttons:
                        return True

            return False

        for button in buttons:
            self.bot.loop.create_task(message.add_reaction(button))

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", check=check, timeout=60
            )
            reaction = str(reaction)
        except asyncio.TimeoutError:
            return False

        if reaction == buttons[0]:
            return True

        return False
