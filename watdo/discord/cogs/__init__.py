import asyncio
from typing import cast, Any, Mapping, Callable, Awaitable, Optional
from dataclasses import dataclass
import discord
from discord.ext import commands as dc
from watdo.errors import CancelCommand
from watdo.logging import get_logger
from watdo.discord import DiscordBot
from watdo.discord.embeds import Embed
from watdo.models.list import TodoList


@dataclass(kw_only=True, frozen=True)
class ParsedCommandParam:
    value: str
    is_required: bool
    description: str | None


class BaseCog(dc.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.logger = get_logger(type(self).__name__)

    def run_coro(self, coro: Awaitable[None]) -> None:
        async def async_wrapper() -> None:
            try:
                await coro
            except Exception as error:
                self.logger.exception(error)

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
        ctx: dc.Context,
        msg: Optional[str] = None,
    ) -> discord.Message:
        async def delete_previous_sticky_message() -> None:
            prev_id = todo_list.sticky_message_id

            if prev_id is not None:
                prev_message = ch.get_partial_message(prev_id)
                await self.delete_message(prev_message)

        todo_list = await TodoList.from_ctx(ctx)
        ch = cast(discord.TextChannel, ctx.channel)
        embed = Embed(self.bot, f"#{ch.name}")

        if msg is not None:
            embed.add_field(name="", value=msg, inline=False)

        self.run_coro(delete_previous_sticky_message())

        message = await self.send(ctx.channel, embed=embed)
        await todo_list.set_sticky_message_id(message.id)
        return message

    @staticmethod
    async def delete_message(message: discord.PartialMessage) -> None:
        await message.delete()

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
        ctx: dc.Context,
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
                message = await self.bot.wait_for(
                    "message", check=check, timeout=60 * 5
                )
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
