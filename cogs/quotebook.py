from concurrent.futures import thread
from xmlrpc import client
import discord
from discord.ext import commands

import asyncio
import os
from pyairtable import Table

from datetime import datetime
import random

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')


class Quotebook(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    # commands
    @commands.command()
    async def new_quote(self, ctx, *, args):
        '''create a new quote'''
        print('hi')
        quote_timestamp = datetime.now()
        quote_timestamp_str = quote_timestamp.strftime("%m᜵%d᜵%y - %I.%M %p")
        quote_msg = args
        if len(quote_msg) > 20:
            thread = await ctx.channel.create_thread(name=f'{quote_timestamp_str} - {quote_msg[0:20]}', type=discord.ChannelType.public_thread)
        else:
            thread = await ctx.channel.create_thread(name=f'Quote - {quote_msg}', type=discord.ChannelType.public_thread)
        print(thread)
        list_of_prompts = ['Who said this?', 'Context of quote?']
        for i in range(len(list_of_prompts)):
            await prompt_wait(ctx, thread)
            await thread.send(list_of_prompts[i])

            def check(m):
                return m.author == ctx.author and m.channel

            reply = await self.client.wait_for('message', check=check)

            if i == 0:
                who = reply.content
            else:
                context = reply.content

            await prompt_wait(ctx, thread)

        table = Table(AIRTABLE_API_KEY,
                      AIRTABLE_BASE_ID, 'Quotebook')

        await upload_to_airtable(table, quote=quote_msg, who=who, context=context, timestamp=quote_timestamp, thread=thread)
    
    @commands.command()
    async def currently_feeling(self, ctx, *, args):
        '''tell the bot what you're currently feeling and why'''
        current_feeling_timestamp = datetime.now()
        current_feeling_timestamp_str = current_feeling_timestamp.strftime("%m᜵%d᜵%y - %I.%M %p")
        current_feeling = args
        thread = await ctx.channel.create_thread(name=f'Currently feeling {current_feeling} - {current_feeling_timestamp_str}', type=discord.ChannelType.public_thread)
        
        list_of_prompts = [f'Why are you feeling {current_feeling}?',
                          ]
        rant = ''
        for prompt in list_of_prompts:
            await prompt_wait(ctx, thread)
            await thread.send(prompt)

            def check(m):
                return m.author == ctx.author and m.channel

            reply = await self.client.wait_for('message', check=check)

            rant = f'{rant}{prompt}: \n{reply.content}\n\n'
            await prompt_wait(ctx, thread)

        table = Table(AIRTABLE_API_KEY,
                      AIRTABLE_BASE_ID, 'CurrentlyFeeling')

        try:
            table.create({'mood': f'{current_feeling}',
                        'context': f'{rant}',
                        'timestamp': f'{current_feeling_timestamp}'})
            await prompt_wait(ctx, thread)
            await thread.send(f'Hey, I wrote your rant up onto the cloud so you can look back on it later.')
            await prompt_wait(ctx, thread)
            await thread.send(f'I really hope you\'re doing alright.')
        except:
            await thread.send(f'Rant failed to save to Airtable... please try again.')

    @commands.command()
    async def rant(self, ctx):
        '''rant to the bot'''
        rant_timestamp = datetime.now()
        rant_timestamp_str = rant_timestamp.strftime("%m᜵%d᜵%y - %I.%M %p")
        rant_msg = ''
        emoji = '💭'
        thread = await ctx.channel.create_thread(name=f'{rant_timestamp_str}', type=discord.ChannelType.public_thread)

        await prompt_wait(ctx, thread)
        await thread.send("Hey! Release all your thoughts to me until you say you're 'done'. I don't mind. :)")

        def check(m):
            return m.author == ctx.author and m.channel

        reply = await self.client.wait_for('message', check=check)
        rant_msg = reply.content
        

        while reply.content != 'done':
            await reply.add_reaction(emoji)
            reply = await self.client.wait_for('message', check=check)
            if reply.content == 'done':
                done = '🤐'
                await reply.add_reaction(done)
            else:
                rant_msg = f'{rant_msg}\n{reply.content}'


        table = Table(AIRTABLE_API_KEY,
                      AIRTABLE_BASE_ID, 'Rants')

        try:
            table.create({'rant': f'{rant_msg}',
                          'timestamp': f'{rant_timestamp}'})
            await prompt_wait(ctx, thread)
            await thread.send(f'Hey, I wrote your rant up onto the cloud so you can look back on it later.')
            await prompt_wait(ctx, thread)
            await thread.send(f'Always here to chat if you need to. <3')
        except:
            await thread.send(f'Rant failed to save to Airtable... please try again.')

async def prompt_wait(ctx, thread):
    async with thread.typing():
        # Random typing time
        type_time = random.uniform(4, 5)
        await asyncio.sleep(type_time)

async def upload_to_airtable(airtable, quote, who, context, timestamp, thread):
    try:
        airtable.create({'quote': f'{quote}',
                          'who': f'{who}',
                          'context': f'{context}',
                          'timestamp': f'{timestamp}'})
        await thread.send(f'Quote successfully saved to Airtable!')
    except:
        await thread.send(f'Quote failed to save to Airtable!')

async def setup(client):
    await client.add_cog(Quotebook(client))
