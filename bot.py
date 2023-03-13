import os
import pickle
import random
import threading
import urllib.request
import requests
import discord
from urllib.error import HTTPError
from discord.ext import commands
from discord.ext import tasks
from datetime import date, datetime, timedelta
from libgen_api import LibgenSearch

TOKEN = os.environ.get("API_KEY")
GUILD = 'sgmaff'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)
guild = None

MY_USERID = 275628620725092354

########## SETUP ###########
@bot.event
async def on_ready():
    global guild
    print(f'connected to Discord')
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(guild)
    print(f'connected to guild {GUILD}')
    print(f'guild id: {guild.id}')

@bot.event
async def on_command_error(ctx, error):
    print(f'ERROR: {error}')
    await ctx.send(f'ERROR: {error}')

######### LIBGEN ##########
class LibgenDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(options=options)

    async def callback(self, interaction):
        author, _id = self.values[0].split('@')
        s = LibgenSearch()
        item = s.search_author_filtered(author, {'ID': _id})[0]
        links = s.resolve_download_links(item)
        title = item['Title']
        msg = f'Download links for {title}: ' + \
            ''.join([f'[{k}]({v}) ' for k,v in links.items()])
        await interaction.response.send_message(msg)

class LibgenDropdownView(discord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.add_item(LibgenDropdown(options))

def format_label(s):
    author, title = s['Author'], s['Title']
    size, extension, pages = s['Size'], s['Extension'], s['Pages']
    year = s['Year']
    label = f'{title}'
    desc = f'{author} ({size} {extension}, {pages} pages, {year})'
    return label, desc

bot.remove_command('lg')

@bot.command(name='lg', brief='Search and download books from Libgen')
async def libgen(ctx, *, arg):
    if len(arg) < 3:
        await ctx.send('Query must be at least 3 characters long!')
        return
    arg = ''.join(arg)
    s = LibgenSearch()
    results = s.search_title(arg)
    options = []
    if not results:
        await ctx.send('No results :(')
        return
    for res in results:
        label, desc = format_label(res)
        if len(label) >= 100:
            label = label[:97] + '...'
        if len(desc) >= 100:
            desc = desc[:97] + '...'
        options.append(discord.SelectOption(
            label=label,
            description=desc,
            value=f'{res["Author"]}@{res["ID"]}'
        ))
    await ctx.send(f'Search results for "{arg}"',
                   view=LibgenDropdownView(options))

##### MISC COMMANDS #####
@bot.command(name='alive', brief='Check if alive')
async def alive(ctx):
    await ctx.send('Hey there!')

@bot.command(name='say', brief='Say')
async def say(ctx, *, arg):
    await ctx.send(arg)

@bot.command(name='die', brief='Die')
async def die(ctx):
    global MY_USERID
    if ctx.author.id != MY_USERID:
        await ctx.send('Nice try, but you have not earnt the privilege to kill me.')
        return

    await ctx.send('I shall die')
    await bot.close()

bot_thread = threading.Thread(target=bot.run,
                              name="Discord bot",
                              args=[TOKEN])
bot_thread.start()
bot_thread.join()

