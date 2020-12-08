from discord.ext import commands
from discord.utils import find, get
from tinydb import TinyDB, where
from commands.formatting.DatabaseFormatting import GetReactAssignmentList, CheckMessageForReactAssignment
import json
import requests
import discord
import asyncio
import time
# checks prefix database for each message. could probably improve this
default_prefix = ","


def prefix(bot, message):
    prefixList = TinyDB('data/databases/prefixdb.json')
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
# def ctime(func):
#     from timeit import default_timer
#     from functools import wraps
#     @wraps(func)
#     async def wrapper(*args, **kwargs):
#         time = default_timer()
#         ret = await func(*args,**kwargs)
#         print(f'{func.__name__.capitalize()}: {round((default_timer() - time),2)}')
#         return ret
#     return wrapper


@bot.event
async def on_ready():
    print("Connected..")
    CurrentGuildCount = 0
    for _ in bot.guilds:
        CurrentGuildCount += 1
    print('Current Server Count: ' + str(CurrentGuildCount))
    await bot.change_presence(activity=discord.Game(name='.help | discord.gg/wDu5CAA'))


# Temporary thing for WSC
@bot.event
async def on_member_join(member):
    from discord.member import Member
    guild = member.guild
    if guild.id == 542056038946439190:
        user = member
        role = get(user.guild.roles, name='Gatherer')
        await Member.add_roles(user, role)


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    if ctx.author.bot is False:
        await bot.invoke(ctx)


@bot.event
async def on_guild_join(guild):
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
bot.run(TOKEN)
