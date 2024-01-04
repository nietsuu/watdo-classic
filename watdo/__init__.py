import asyncio
from watdo.discord import DiscordBot
from watdo.environ import DISCORD_TOKEN


async def main(loop: asyncio.AbstractEventLoop) -> int:
    bot = DiscordBot(loop=loop)
    await bot.start(DISCORD_TOKEN)
    return 0
