from typing import Any
from dataclasses import dataclass
import discord
from discord.ext import commands as dc
from watdo.discord import DiscordBot


@dataclass(kw_only=True, frozen=True)
class ParsedCommandParam:
    value: str
    is_required: bool
    description: str | None


class BaseCog(dc.Cog):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

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
