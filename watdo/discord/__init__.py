import os
import glob
import random
import asyncio
from typing import cast, Any, Awaitable, Mapping, Callable
from dataclasses import dataclass
import discord
from discord.ext import commands as dc
from watdo.errors import CancelCommand, FailCommand
from watdo.logging import get_logger
from watdo.models.list import TodoList
from watdo.discord.embeds import Embed


@dataclass(kw_only=True, frozen=True)
class ParsedCommandParam:
    value: str
    is_required: bool
    description: str | None


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
        self, ctx: dc.Context["DiscordBot"], error: dc.CommandError
    ) -> None:
        if isinstance(error, dc.MissingRequiredArgument) and ctx.command is not None:
            params = self.parse_params(ctx.command)
            await self.update_sticky(
                ctx,
                dc.CommandError(f"{ctx.prefix}{ctx.invoked_with} {params}"),
            )
        elif isinstance(error, dc.CommandNotFound):
            await self.update_sticky(
                ctx,
                dc.CommandError(f'No command "{ctx.invoked_with}" ❌'),
            )
        elif isinstance(error, CancelCommand):
            pass
        elif isinstance(error, FailCommand):
            await self.update_sticky(ctx, error)
        else:
            await self.update_sticky(
                ctx,
                dc.CommandError(f"**{type(error).__name__}:** {error}"),
            )

    def run_coro(self, coro: Awaitable[None]) -> None:
        async def async_wrapper() -> None:
            try:
                await coro
            except Exception as error:
                get_logger(f"{type(self).__name__}.run_coro").exception(error)

        asyncio.create_task(async_wrapper())

    @staticmethod
    async def send(
        messageable: discord.abc.Messageable,
        content: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> discord.Message:
        if content is None:
            return await messageable.send(*args, **kwargs)

        return await messageable.send(str(content)[:2000], *args, **kwargs)

    async def update_sticky(
        self,
        ctx: dc.Context["DiscordBot"],
        msg: str | Exception | None = None,
    ) -> discord.Message:
        async def delete_previous_sticky_message() -> None:
            if todo_list is None:
                return

            prev_id = todo_list.sticky_message_id

            if prev_id is not None:
                prev_message = ch.get_partial_message(prev_id)
                await self.delete_message(prev_message)

        todo_list = await TodoList.from_ctx(ctx)
        ch = cast(discord.TextChannel, ctx.channel)
        embed = Embed(
            self,
            f"#{ch.name}" if todo_list is None else random.choice(todo_list.notes),
            color=discord.Color.from_rgb(255, 8, 8)
            if isinstance(msg, Exception)
            else self.color,
        )

        if msg is not None:
            if isinstance(msg, dc.CommandError):
                msg = str(msg)
            elif isinstance(msg, Exception):
                msg = f"```\n{repr(msg)}\n```"

            embed.add_field(name="", value=msg, inline=False)

        self.run_coro(delete_previous_sticky_message())

        message = await self.send(ctx.channel, embed=embed)

        if todo_list is not None:
            todo_list.sticky_message_id = message.id
            await todo_list.save_changes()

        return message

    @staticmethod
    async def delete_message(message: discord.PartialMessage) -> None:
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass

    @staticmethod
    def parse_params_list(
        command: dc.Command[Any, Any, Any]
    ) -> list[ParsedCommandParam]:
        params = []

        for param in command.clean_params.values():
            if "[" in str(param.annotation):
                t = str(param.annotation)
            else:
                t = param.annotation.__name__

            if "typing.Optional[" in t:
                t = str(t).lstrip("typing.Optional[").rstrip("]")

            if t == "bool":
                t = "yes/no"

            if t == "Message":
                t = "message link/id"

            if t in ("int", "float"):
                t = "number"

            t = f"*{t}*"
            p = param.name if t == "*str*" else f"{param.name}: {t}"
            p = p.replace("_", " ")

            if param.required:
                p = f"**[{p}]**"
            else:
                p = f"[{p}]"

            params.append(
                ParsedCommandParam(
                    value=p,
                    is_required=param.required,
                    description=param.description,
                )
            )

        return params

    @classmethod
    def parse_params(cls, command: dc.Command[Any, Any, Any]) -> str:
        params = [p.value for p in cls.parse_params_list(command)]
        return " ".join(params)

    async def interview(
        self,
        ctx: dc.Context["DiscordBot"],
        *,
        questions: Mapping[
            str,
            None | Callable[[discord.Message], Awaitable[Any]],
        ],
    ) -> list[Any]:
        def check(m: discord.Message) -> bool:
            if m.channel.id == ctx.channel.id:
                if m.author.id == ctx.author.id:
                    return True

            return False

        async def ask(question: str) -> Any:
            try:
                message = await self.wait_for("message", check=check, timeout=60 * 5)
            except asyncio.TimeoutError:
                raise CancelCommand()

            validator = questions[question]

            if validator is None:
                return message.content

            return await validator(message)

        answers = []
        keys = list(questions.keys())
        bot_msg = await self.send(ctx, keys[0])

        for index, question in enumerate(keys):
            if index != 0:
                await bot_msg.edit(content=question)

            while (answer := await ask(question)) is None:
                pass

            answers.append(answer)

        return answers
