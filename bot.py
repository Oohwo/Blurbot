import discord
import config
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

async def load_extensions():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            # cut off the .py from the file name
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load_extensions()
        await client.start(os.environ.get('DISCORD_BOT_TOKEN')
)

asyncio.run(main())
