from discord.ext import commands
from discord.ext.commands import CommandNotFound
from tinydb import TinyDB, where
from jsondiff import diff
from datetime import datetime
from datetime import timedelta
from discord.utils import find
from tabulate import tabulate
from pytz import timezone
from commands.formatting.DatabaseFormatting import getNewsChannelsToPost, getChannelsToPost, updatesDB, removeChannelFromDatabase, getCutoffChannels, rmChannelFromCutoffDatabase, removeChannelFromDatabaseSongs
from commands.formatting.T10Commands import t10formatting, t10logging, t10membersformatting
from commands.formatting.TimeCommands import GetEventTimeLeftSeconds
from commands.formatting.EventCommands import GetCutoffFormatting, GetCurrentEventID, GetEventName
from commands.apiFunctions import GetBestdoriCutoffAPI
from commands.cogs.Event import Event
import json, requests, discord, asyncio, time
import startup.OpenWebdrivers

# checks prefix database for each message. could probably improve this 
default_prefix = "."
def prefix(bot, message):
    prefixList = TinyDB('databases\prefixdb.json')
    results = prefixList.search(where('id') == message.guild.id)
    if results:
        prefix = results[0]['prefix']
    else:
        prefix = default_prefix
    return prefix

bot = commands.Bot(command_prefix=prefix, case_insensitive=True)

# read config information
with open("config.json") as file:
    config_json = json.load(file)
    TOKEN = config_json["token"]

#################
#   Bot Stuff   #
#################   
@bot.event
async def on_ready():
    print("Connected..")
    CurrentGuildCount = 0
    for _ in bot.guilds:
        CurrentGuildCount += 1
    print('Current Server Count: ' + str(CurrentGuildCount))
    await bot.change_presence(activity=discord.Game(name='.help | discord.gg/wDu5CAA'))

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Thanks for inviting me! You can get started by typing .help to find the current command list and change the command prefix by typing .setprefix followed by the desired prefix e.g. !.\nSource Code: https://github.com/Amexy/lisa-bot\nSupport: https://ko-fi.com/lisabot\nIf you have any feedback or requests, please dm Josh#1373 or join discord.gg/wDu5CAA.")


bot.get_command('help').hidden=True
bot.load_extension("commands.cogs.Game")
bot.load_extension("commands.cogs.Misc")
bot.load_extension("commands.cogs.Admin")
bot.load_extension("commands.cogs.Event")
bot.load_extension("commands.cogs.Updates")
bot.load_extension("commands.cogs.Moderation")
bot.load_extension("commands.cogs.Loops")

bot.run(TOKEN) 
