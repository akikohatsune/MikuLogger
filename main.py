import asyncio
import os

import discord
from discord.ext import commands

from db import init_db

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.synced = False


@bot.event
async def on_ready() -> None:
    if not bot.synced:
        await bot.tree.sync()
        bot.synced = True
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


async def main() -> None:
    init_db()
    await bot.load_extension("cogs.logger")
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
