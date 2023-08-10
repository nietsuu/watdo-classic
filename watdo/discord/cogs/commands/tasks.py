import math
import time
from typing import Optional, Tuple, Dict, List
import recurrent
import dateparser
import discord
from discord.ext import commands as dc
from watdo import dt
from watdo.models import Task
from watdo.discord import Bot
from watdo.safe_data import Timestamp, String
from watdo.discord.cogs import BaseCog
from watdo.discord.embeds import Embed, TaskEmbed, PagedEmbed


class Tasks(BaseCog):
    @dc.command()
    async def summary(self, ctx: dc.Context[Bot]) -> None:
        """Show the summary of all your tasks."""
        user = await self.get_user_data(ctx)
        tasks = await self.db.get_user_tasks(user)
        embed = Embed(self.bot, "TASKS SUMMARY")

        total = 0
        is_important = 0
        overdue = 0
        recurring = 0
        one_time = 0
        done = 0
        max_categ_len = 0
        categories: Dict[str, int] = {}

        for task in tasks:
            total += 1

            if task.is_important.value:
                is_important += 1

            if task.is_overdue:
                overdue += 1

            if isinstance(task.due, String):
                recurring += 1
            else:
                one_time += 1

            if task.is_done:
                done += 1

            if len(task.category.value) > max_categ_len:
                max_categ_len = len(task.category.value)

            try:
                categories[task.category.value] += 1
            except KeyError:
                categories[task.category.value] = 1

        embed.add_field(name="Total", value=total)
        embed.add_field(name="Important", value=is_important)
        embed.add_field(name="Overdue", value=overdue)
        embed.add_field(name="Recurring", value=recurring)
        embed.add_field(name="One-Time", value=one_time)
        embed.add_field(name="Done", value=done)

        if categories:
            c = "\n".join(
                f"{k.ljust(max_categ_len)} {v}" for k, v in categories.items()
            )
            embed.add_field(
                name="Categories", value=f"```\n{c[:1000]}\n```", inline=False
            )

        await ctx.send(embed=embed)

    async def _send_tasks(
        self, ctx: dc.Context[Bot], tasks: List[Task], *, as_text: bool
    ) -> None:
        if not tasks:
            await ctx.send("No tasks.")
            return

        if as_text:
            await ctx.send(self.tasks_to_text(tasks)[:2000])
            return

        paged_embed = PagedEmbed(
            ctx,
            embeds=tuple(TaskEmbed(self.bot, t) for t in tasks),
        )
        await paged_embed.send()

    @dc.command()
    async def list(
        self,
        ctx: dc.Context[Bot],
        category: Optional[str] = None,
        as_text: bool = False,
    ) -> None:
        """Show your tasks list."""
        user = await self.get_user_data(ctx)
        tasks = await self.db.get_user_tasks(user, category=category or None)
        tasks.sort(key=lambda t: t.is_important.value, reverse=True)
        tasks.sort(key=lambda t: t.due_date.timestamp() if t.due_date else math.inf)
        tasks.sort(key=lambda t: t.last_done.value if t.last_done else math.inf)
        await self._send_tasks(ctx, tasks, as_text=as_text)

    def _parse_due(self, due: str, utc_offset_hour: float) -> Optional[float | str]:
        tz = dt.utc_offset_hour_to_tz(utc_offset_hour)
        date = dateparser.parse(
            due,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TIMEZONE": tz.tzname(dt.date_now(utc_offset_hour)) or "",
            },
        )

        if date is not None:
            return date.timestamp()

        rr: Optional[str | dt.datetime] = recurrent.parse(
            due,
            now=dt.date_now(utc_offset_hour),
        )

        if isinstance(rr, str):
            if "DTSTART:" not in rr:
                date_now = dt.date_now(utc_offset_hour)
                d = date_now.strftime("%Y%m%dT%H%M%S")
                rr = f"DTSTART:{d}\n{rr}"

            return rr

        if isinstance(rr, dt.datetime_type):
            return rr.timestamp()

        return None

    @dc.command()
    async def todo(
        self,
        ctx: dc.Context[Bot],
        title: str,
        category: str,
        is_important: bool,
        due: Optional[str] = dc.parameter(
            default=None,
            description='**Examples:**\n"tomorrow at 5PM"\n"every morning"\n"in 3 hours"',
        ),
        description: Optional[str] = None,
        has_reminder: bool = True,
        is_auto_done: bool = False,
    ) -> None:
        """Add a task to do.
        **Use this please: https://nietsuu.github.io/watdo**
        If the title is a duplicate, the old task will be overwritten."""
        uid = str(ctx.author.id)
        user = await self.get_user_data(ctx)
        utc_offset_hour = user.utc_offset_hour.value
        existing_task = await self.db.get_user_task(user, title)
        task = Task(
            title=title,
            category=category,
            is_important=is_important,
            utc_offset_hour=utc_offset_hour,
            due=self._parse_due(due, utc_offset_hour) if due else None,
            description=description,
            has_reminder=has_reminder,
            is_auto_done=is_auto_done,
            channel_id=None
            if isinstance(ctx.channel, discord.channel.DMChannel)
            else ctx.channel.id,
            created_at=time.time()
            if existing_task is None
            else existing_task.created_at.value,
        )

        if task.due_date:
            task.next_reminder = Timestamp(task.due_date.timestamp())
        else:
            task.next_reminder = None

        if existing_task is None:
            content = "Task added ✅"
            await self.db.add_user_task(uid, task)
        else:
            content = "Task updated ✅"
            await self.db.set_user_task(
                user,
                old_task_str=existing_task.as_json_str(),
                new_task=task,
            )

        await ctx.send(content, embed=TaskEmbed(self.bot, task))

    @dc.command(aliases=["do"])
    async def do_priority(
        self,
        ctx: dc.Context[Bot],
        category: Optional[str] = None,
        as_text: bool = False,
    ) -> None:
        """Show priority tasks."""
        user = await self.get_user_data(ctx)
        tasks = await self.db.get_user_tasks(
            user,
            category=category or None,
            ignore_done=True,
        )
        tasks.sort(key=lambda t: t.is_important.value, reverse=True)
        tasks.sort(key=lambda t: t.due_date.timestamp() if t.due_date else math.inf)
        tasks.sort(key=lambda t: t.last_done.value if t.last_done else math.inf)
        await self._send_tasks(ctx, tasks, as_text=as_text)

    async def _confirm_task_action(
        self, ctx: dc.Context[Bot], title: str
    ) -> Tuple[Optional[discord.Message], Optional[Task]]:
        user = await self.get_user_data(ctx)
        task = await self.db.get_user_task(user, title=title)

        if task is None:
            await ctx.send(f'Task "{title}" not found ❌')
            return None, None

        message = await ctx.send(
            "Are you sure?",
            embed=TaskEmbed(self.bot, task),
        )
        is_confirm = await self.wait_for_confirmation(ctx, message)

        if is_confirm:
            return message, task

        return None, None

    @dc.command()
    async def done(self, ctx: dc.Context[Bot], title: str) -> None:
        """Mark a task as done. If the task is not a recurring task, it will get removed."""
        user = await self.get_user_data(ctx)
        message, task = await self._confirm_task_action(ctx, title)

        if (message is not None) and (task is not None):
            await self.db.done_user_task(user, task)
            await message.edit(
                content="Done ✅",
                embed=TaskEmbed(self.bot, task),
            )

    @dc.command()
    async def cancel(self, ctx: dc.Context[Bot], title: str) -> None:
        """Remove a task."""
        message, task = await self._confirm_task_action(ctx, title)

        if (message is not None) and (task is not None):
            await self.db.remove_user_task(str(ctx.author.id), task)
            await message.edit(
                content="Cancelled ✅",
                embed=TaskEmbed(self.bot, task),
            )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tasks(bot, bot.db))
