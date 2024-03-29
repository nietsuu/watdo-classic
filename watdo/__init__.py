import asyncio
from watdo.discord import Bot
from watdo.database import Database
from watdo.environ import DISCORD_TOKEN
from watdo._main_runner import async_main_runner

bot: Bot


async def async_main(loop: asyncio.AbstractEventLoop) -> int:
    global bot

    db = Database()
    await db.initialize(loop=loop)

    bot = Bot(loop=loop, database=db)
    await bot.start(DISCORD_TOKEN)

    return 0


def main() -> int:
    return async_main_runner(async_main)
