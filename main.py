from discord.ext import commands
from discord.utils import find, get
from tinydb import TinyDB, where
from commands.formatting.DatabaseFormatting import GetReactAssignmentList, CheckMessageForReactAssignment
from tabulate import tabulate
from pytz import timezone
from datetime import datetime
import json
import discord
import requests
import asyncio
import time
# checks prefix database for each message. could probably improve this
default_prefix = "."
def prefix(bot, message):
    prefixList = TinyDB('data/databases/tinydb/prefixdb.json')
    results = prefixList.search(where('id') == message.guild.id)
    if results:
        prefix = results[0]['prefix']
    else:
        prefix = default_prefix
    return prefix

from discord import AutoShardedClient
bot = commands.AutoShardedBot(command_prefix=prefix, case_insensitive=True)

# read config information
with open("config.json") as file:
    config_json = json.load(file)
    TOKEN = config_json["token"]

#################
#   Bot Stuff   #
#################
def ctime(func):
    from timeit import default_timer
    from functools import wraps
    @wraps(func)
    async def wrapper(*args, **kwargs):
        time = default_timer()
        ret = await func(*args,**kwargs)
        print(f'{func.__name__.capitalize()}: {round((default_timer() - time),2)}')
        return ret
    return wrapper

@bot.event
async def on_ready():
    print("Connected..")
    CurrentGuildCount = 0
    for _ in bot.guilds:
        CurrentGuildCount += 1
    print('Current Server Count: ' + str(CurrentGuildCount))
    await bot.change_presence(activity=discord.Game(name='.help | discord.gg/wDu5CAA'))

@bot.event
async def on_command(ctx):
    untracked_accounts = [699901466776829972,631047517907451926,557654769670553650,523337807847227402,562409515585110037,235088799074484224,235148962103951360,580021037157187584]
    if ctx.message.author.id not in untracked_accounts:
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        now_time = datetime.now(timezone('US/Central'))
        channel = bot.get_channel(666793281522368533)
        message = []
        message.append(["Time", now_time.strftime(fmt)])
        message.append(["ID", str(ctx.message.author.id)]) 
        message.append(["User", str(ctx.message.author.name) + "#" + str(ctx.message.author.discriminator)]) 
        message.append(["Server", str(ctx.message.guild.name)]) 
        message.append(["Channel", str(ctx.message.channel.name)]) 
        message.append(["Command", str(ctx.invoked_with)]) 
        message.append(["Parameters", str(ctx.message.content)])
        await channel.send("```" + tabulate(message,tablefmt="plain") + "```")

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    if ctx.author.bot is False:
        #this is for a personal server of mine, just ignore it
        if 'rinboi' in ctx.message.content.lower():
            await ctx.send("rin is a cute girl!")
        if 'rin boi' in ctx.message.content.lower():
            await ctx.send("rin is a cute girl!")
        await bot.invoke(ctx)

@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(846143175927398431)
    guild_owner = await bot.fetch_user(guild.owner_id)
    message = f'```Joined Server: {guild.name}\nOwner: {guild_owner.name}#{guild_owner.discriminator}\nMember Count: {str(guild.member_count)}\nDate Made: {str(guild.created_at)}```'
    await channel.send(message)
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Thanks for inviting me! You can get started by typing .help to find the current command list and change the command prefix by typing .setprefix followed by the desired prefix e.g. !.\nSource Code: https://github.com/Amexy/lisa-bot\nSupport: https://ko-fi.com/lisabot\nIf you have any feedback or requests, please dm Josh#1373 or join discord.gg/wDu5CAA.")

@bot.event
async def on_raw_reaction_add(payload):
    if CheckMessageForReactAssignment(payload.message_id):
        reactList = GetReactAssignmentList(payload.message_id)
        for rolename in reactList:
            if str(payload.emoji) == reactList[rolename]:
                role = discord.utils.find(lambda r: r.name == rolename, payload.member.guild.roles)
                if role:
                    try:
                        if not payload.member.bot:
                            await payload.member.add_roles(role)
                        return
                    except:
                        print("Could not complete action for react based role assignment.")


@bot.event
async def on_raw_reaction_remove(payload):
    if CheckMessageForReactAssignment(payload.message_id):
        reactList = GetReactAssignmentList(payload.message_id)
        for rolename in reactList:
            if str(payload.emoji) == reactList[rolename]:
                # raw reaction removal does not provide us with the member object, so we have to fetch the guild, then the member :(
                # this is literally the saddest thing :eve:
                guild = bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if not member.bot:
                    role = discord.utils.find(lambda r: r.name == rolename, guild.roles)
                    if role:
                        try:
                            await member.remove_roles(role)
                            return
                        except:
                            print("Could not complete action for react based role assignment.")


bot.remove_command('help')
bot.load_extension("commands.cogs.Game")
bot.load_extension("commands.cogs.Misc")
bot.load_extension("commands.cogs.Admin")
bot.load_extension("commands.cogs.Event")
bot.load_extension("commands.cogs.Updates")
bot.load_extension("commands.cogs.Moderation")
bot.load_extension("commands.cogs.Loops")
bot.load_extension("commands.cogs.Help")
bot.load_extension("commands.cogs.Fun")
bot.load_extension("commands.cogs.CommandErrorHandler")
bot.run(TOKEN)
