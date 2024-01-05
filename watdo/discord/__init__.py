import os
import glob
import asyncio
from typing import Any
import discord
from discord.ext import commands as dc
from watdo.logging import get_logger


class DiscordBot(dc.Bot):
    def __init__(self, *, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(
            loop=loop,
            command_prefix=":",
            help_command=None,
            intents=discord.Intents.all(),
        )
        self.logger = get_logger("DiscordBot")

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
