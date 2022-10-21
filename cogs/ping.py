from http import client
import discord
from discord.ext import commands

class Ping(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print('------')
        print(f'Logged in as {self.client.user} (ID: {self.client.user.id}!)')
        print('------')

    # commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong!!')

async def setup(client):
    await client.add_cog(Ping(client))
        