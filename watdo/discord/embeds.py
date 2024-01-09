import math
import asyncio
from typing import TYPE_CHECKING, Any, Tuple, Callable, Awaitable
import discord
from discord.ext import commands as dc
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


class PagedEmbed:
    def __init__(
        self,
        ctx: dc.Context["DiscordBot"],
        embeds_getter: Callable[[], Awaitable[Tuple[discord.Embed, ...]]],
        *,
        timeout: float = 60 * 60,  # 1 hour
        empty_message: str = "No items.",
    ) -> None:
        self.ctx = ctx
        self.embeds_getter = embeds_getter
        self.timeout = timeout
        self.empty_message = Embed(ctx.bot, empty_message)

        self.current_page = 0
        self.embeds_len = 1

        self.message: discord.Message
        self.embeds: Tuple[discord.Embed, ...]

        self._controls = {
            "extract": "✴",
            "first": "\u23ee",
            "previous": "\u25c0",
            "next": "\u25b6",
            "last": "\u23ed",
            "refresh": "🔄",
        }

    async def update_embeds(self) -> None:
        self.embeds = await self.embeds_getter()
        self._set_embeds_footer()

    def _set_embeds_footer(self) -> None:
        for index, embed in enumerate(self.embeds):
            page_no = f"{index + 1}/{len(self.embeds)}"

            if embed.footer.text is None:
                embed.set_footer(text=page_no)
            else:
                embed.set_footer(text=f"{page_no} • {embed.footer.text}")

    def _get_last_page_index(self) -> int:
        try:
            current = (len(self.embeds) - 1) % (len(self.embeds) / self.embeds_len)
            return math.ceil(current)
        except ZeroDivisionError:
            return 0

    def _process_reaction(self, reaction: str, user: discord.User) -> None:
        embeds = self.embeds

        if len(embeds) == 0:
            pass
        elif reaction == self._controls["first"]:
            self.current_page = 0
        elif reaction == self._controls["previous"]:
            if self.current_page != 0:
                self.current_page -= 1
        elif reaction == self._controls["next"]:
            if self.current_page != len(embeds) - 1:
                self.current_page += 1
        elif reaction == self._controls["last"]:
            self.current_page = self._get_last_page_index()
        elif reaction == self._controls["extract"]:
            self.embeds_len = 10 if self.embeds_len == 1 else 1
        elif reaction == self._controls["refresh"]:
            pass

        embeds = embeds[
            self.current_page * self.embeds_len : self.current_page * self.embeds_len
            + self.embeds_len
        ]

        if len(embeds) == 0:
            self.current_page = self._get_last_page_index()
            embeds = embeds[
                self.current_page
                * self.embeds_len : self.current_page
                * self.embeds_len
                + self.embeds_len
            ]

        self.ctx.bot.loop.create_task(
            self.message.edit(embeds=embeds or [self.empty_message])
        )
        self.ctx.bot.loop.create_task(
            self.ctx.bot.remove_reaction(
                self.message,
                reaction=reaction,
                user=user,
            )
        )

    async def _start_loop(self) -> None:
        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (user.id == self.ctx.author.id) and (
                reaction.message.id == self.message.id
            )

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
            except asyncio.TimeoutError:
                break

            await self.update_embeds()
            self._process_reaction(str(reaction), user)

    async def send(self) -> discord.Message:
        await self.update_embeds()
        self.message = await self.ctx.bot.send(
            self.ctx,
            embeds=self.embeds[self.current_page : self.embeds_len]
            or [self.empty_message],
        )

        for emoji in self._controls.values():
            self.ctx.bot.loop.create_task(self.message.add_reaction(emoji))

        self.ctx.bot.loop.create_task(self._start_loop())
        return self.message
