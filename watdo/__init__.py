import asyncio
from watdo import db
from watdo.discord import DiscordBot
from watdo.environ import DISCORD_TOKEN


async def main(loop: asyncio.AbstractEventLoop) -> int:
    await db.open()

    bot = DiscordBot(loop=loop)

    try:
        await bot.start(DISCORD_TOKEN)
    finally:
        await db.close()

    return 0
