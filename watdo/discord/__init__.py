import os
import glob
import asyncio
from typing import Any
import discord
from discord.ext import commands as dc
from watdo.errors import CancelCommand
from watdo.logging import get_logger
from watdo.discord.cogs import BaseCog


class DiscordBot(dc.Bot):
    def __init__(self, *, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(
            loop=loop,
            command_prefix=">",
            help_command=None,
            intents=discord.Intents.all(),
        )
        self.logger = get_logger("DiscordBot")
        self.color = discord.Color.from_rgb(191, 155, 231)

        # Add event handlers
        for name in dir(self):
            if name.startswith("_on_") and name.endswith("_event"):
                self._add_event(name.lstrip("_").rstrip("_event"))

    def _add_event(self, event_name: str) -> None:
        event = getattr(self, f"_{event_name}_event")

        async def event_wrapper(*args: Any, **kwargs: Any) -> None:
            try:
                await event(*args, **kwargs)
            except Exception as error:
                get_logger(f"Bot.{event_name}").exception(error)
                raise error

        self.add_listener(event_wrapper, event_name)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.logger.info("Starting...")

        # Load cogs
        for path in glob.iglob(
            os.path.join("watdo", "discord", "cogs", "**", "*"),
            recursive=True,
        ):
            if path.endswith("__init__.py"):
                continue

            if path.endswith(".py"):
                path = path.rstrip(".py").replace("/", ".").replace("\\", ".")
                await self.load_extension(path)

        # Ensure docstring for all commands
        for cog in self.cogs.values():
            for command in cog.get_commands():
                if command.help is None:
                    raise Exception(
                        f"Please add docstring for {command.module}.{command.name}"
                    )

        await super().start(token, reconnect=reconnect)

    async def _on_ready_event(self) -> None:
        self.logger.info("Ready!")

    async def _on_command_error_event(
        self, ctx: dc.Context, error: dc.CommandError
    ) -> None:
        if isinstance(error, dc.MissingRequiredArgument) and ctx.command is not None:
            params = BaseCog.parse_params(ctx.command)
            await BaseCog.send(ctx, f"{ctx.prefix}{ctx.invoked_with} {params}")
        elif isinstance(error, dc.CommandNotFound):
            await BaseCog.send(ctx, f'No command "{ctx.invoked_with}" ❌')
        elif isinstance(error, CancelCommand):
            pass
        else:
            await BaseCog.send(ctx, f"**{type(error).__name__}:** {error}")
