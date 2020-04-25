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

# checks prefix database for each message. could probably improve this 
default_prefix = "!"
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


############
#   Loops  #
############
firstAPI = requests.get('https://bestdori.com/api/news/all.5.json').json()
async def postBestdoriNews():
    await bot.wait_until_ready()
    while not bot.is_closed():
        global firstAPI
        updatedAPI = requests.get('https://bestdori.com/api/news/all.5.json').json()
        embed=discord.Embed(color=0x09d9fd)
        if(sorted(firstAPI.items()) != sorted(updatedAPI.items())):
            fmt = "%Y-%m-%d %H:%M:%S %Z%z"
            now_time = datetime.now(timezone('US/Eastern'))
            
            jsonDif = diff(firstAPI,updatedAPI)
            for x in jsonDif:
                if "Patch Note" in jsonDif[x]['tags']:
                    if "EN" in jsonDif[x]['tags']:
                        ids = getNewsChannelsToPost('en')
                    elif "JP" in jsonDif[x]['tags']:
                        ids = getNewsChannelsToPost('jp')
                    elif "CN" in jsonDif[x]['tags']:
                        ids = getNewsChannelsToPost('cn')
                    
                    #post to channels that want all server patch updates as well
                    allids = getNewsChannelsToPost('all')
                    server = jsonDif[x]['tags'][2]
                    embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1126155698117562368/mW6W89Gg_200x200.png')
                    embed.add_field(name='New %s Patch Note Available!' % server.upper(), value='https://bestdori.com/home/news/' + str(x), inline=False)
                    embed.set_footer(text=now_time.strftime(fmt))               
                    for i in ids:
                        channel = bot.get_channel(i)
                        if channel != None:
                            await channel.send(embed=embed)
                    for i in allids:
                        channel = bot.get_channel(i)
                        if channel != None:
                            await channel.send(embed=embed)

                    embed=discord.Embed(color=0x09d9fd)
            firstAPI = updatedAPI
        await asyncio.sleep(300)

async def sendEventUpdates(message: str, server: str):
    ids = updatesDB(server)
    if(message):
        for i in ids:
            channel = bot.get_channel(i)
            if channel != None:
                await channel.send(message)

async def postEventNotif(server: str):
    await bot.wait_until_ready()
    while not bot.is_closed():
        from commands.apiFunctions import getBandoriGAAPI
        eventAPI = await getBandoriGAAPI(server)
        eventID = eventAPI['eventId']
        eventName = await GetEventName(server, eventID)
        currentTime = ((datetime.now().timestamp()) * 1000)
        eventEnd = float(eventAPI['endAt'])
        eventStart = float(eventAPI['publicStartAt'])
        timeTilEventEnd = (int(eventEnd) - currentTime) / 1000

        #check if event has started yet
        timeToStart = (eventStart - currentTime) / 1000
        if(timeToStart > 0):
            if (timeToStart > 3600):
                sleep = int(timeToStart - 3600)
                await asyncio.sleep(sleep)
                message = "```The " + server.upper() + " event %s begins in 1 hour!```" %eventName
                await sendEventUpdates(message, 'en')
                await asyncio.sleep(3600)
                message = "```The " + server.upper() + " event %s! has begun!```" %eventName
                await sendEventUpdates(message, 'en')
            else:
                await asyncio.sleep(timeToStart)
                message = "```The " + server.upper() + " event %s! has begun!```" %eventName
                await sendEventUpdates(message, 'en')
        # check if there's more than 1 day left
        elif(timeTilEventEnd > 86400):
            timeTo1DayLeft = (eventEnd - 86400000)
            sleep = int((timeTo1DayLeft - currentTime) / 1000)
            await asyncio.sleep(sleep)
            message = "```There is 1 day left in the " + server.upper() + " event %s!```" %eventName
            await sendEventUpdates(message, 'en')
            await asyncio.sleep(82800000 / 1000)
            message = "```There is 1 hour left in the " + server.upper() + " event %s!```" %eventName
            await sendEventUpdates(message, 'en')
            await asyncio.sleep(3600)
            message = "```The " + server.upper() + " event %s has concluded.```" %eventName
            await sendEventUpdates(message, 'en')
        await asyncio.sleep(60)

async def postEventT101hr():
    await bot.wait_until_ready()
    while not bot.is_closed():
        timeStart = datetime.now()
        timeFinish = (timeStart + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).timestamp()            
        timeStart = timeStart.timestamp()
        await asyncio.sleep(timeFinish - timeStart)

        try:
            EnEventID = await GetCurrentEventID('en')
        except Exception as e:
            print('Failed posting 2 minute data. Exception: ' + str(e))            


        if EnEventID:
            print('1 hour ' + str(EnEventID))
            timeLeftEn = await GetEventTimeLeftSeconds('en', EnEventID)
            if(timeLeftEn > 0):
                print('1 hour ' + str(timeLeftEn))
                EnMessage = await t10formatting('en', EnEventID, True)
                #await t10logging('en', EnEventID, False)
                #await t10logging('en', EnEventID, True)
                ids = getChannelsToPost(3600, 'en')
                for i in ids:
                    channel = bot.get_channel(i)
                    if channel != None:
                        try:
                            await channel.send(EnMessage)
                        except: 
                            channel2 = bot.get_channel(523339468229312555)
                            await channel2.send('Removing 1 hour updates from channel: ' + str(channel.id))
                            removeChannelFromDatabase(channel, 3600, 'en')
        
        JPEventID = await GetCurrentEventID('jp')
        if JPEventID:
            timeLeftJp = await GetEventTimeLeftSeconds('jp', JPEventID)
            if(timeLeftJp > 0):
                JPMessage = await t10formatting('jp', JPEventID, True)
                ids = getChannelsToPost(3600, 'jp')
                for i in ids:
                    channel = bot.get_channel(i)
                    if channel != None:
                        try:
                            await channel.send(JPMessage)
                        except: 
                            channel2 = bot.get_channel(523339468229312555)
                            await channel2.send('Removing 1 hour updates from channel: ' + str(channel.id))
                            removeChannelFromDatabase(channel, 3600, 'jp')                  

async def postEventT102min():
    await bot.wait_until_ready()
    while not bot.is_closed():
        timeStart = datetime.now()
        if (timeStart.minute % 2) != 0: 
            timeFinish = (timeStart + timedelta(minutes=1)).replace(second=0, microsecond=0).timestamp()
        else:
            timeFinish = (timeStart + timedelta(minutes=2)).replace(second=0, microsecond=0).timestamp()
        timeStart = timeStart.timestamp()
        await asyncio.sleep(timeFinish - timeStart)
        
        try:
            EnEventID = await GetCurrentEventID('en')
        except Exception as e:
            print('Failed posting 2 minute data. Exception: ' + str(e))            
        if EnEventID:
            timeLeftEn = await GetEventTimeLeftSeconds('en', EnEventID)
            if(timeLeftEn > 0):
                EnMessage = await t10formatting('en', EnEventID, True)
                await t10logging('en', EnEventID, False)
                await t10logging('en', EnEventID, True)
                ids = getChannelsToPost(2, 'en')
                for i in ids:
                    channel = bot.get_channel(i)
                    if channel != None:
                        try:
                            await channel.send(EnMessage)
                        except: 
                            channel2 = bot.get_channel(523339468229312555)
                            await channel2.send('Removing 2 minute updates from channel: ' + str(channel.id))
                            removeChannelFromDatabase(channel, 2, 'en')
                            
        JPEventID = await GetCurrentEventID('jp')
        if JPEventID:
            timeLeftJp = await GetEventTimeLeftSeconds('jp', JPEventID)
            if(timeLeftJp > 0):
                JPMessage = await t10formatting('jp', JPEventID, True)
                ids = getChannelsToPost(2, 'jp')
                for i in ids:
                    channel = bot.get_channel(i)
                    if channel != None:
                        try:
                            await channel.send(JPMessage)
                        except: 
                            channel2 = bot.get_channel(523339468229312555)
                            await channel2.send('Removing 2 minute updates from channel: ' + str(channel.id))
                            removeChannelFromDatabase(channel, 2, 'jp')
            
async def postSongUpdates1min():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            timeStart = datetime.now()
            timeFinish = (timeStart + timedelta(minutes=1)).replace(second=0, microsecond=0).timestamp()
            timeStart = timeStart.timestamp()
            await asyncio.sleep(timeFinish - timeStart)
            eventid = await GetCurrentEventID('en')
            if eventid:
                timeLeft = await GetEventTimeLeftSeconds('en', eventid)
                if(timeLeft > 0):
                    message = await t10membersformatting('en', eventid, True)
                    await t10logging('en', eventid, True)
                    ids = getChannelsToPost(1, 'en')
                    for i in ids:
                        channel = bot.get_channel(i)
                        if channel != None:
                            try:
                                for x in message:
                                    await channel.send(x)
                            except Exception as e:
                                print(e) 
                                channel2 = bot.get_channel(523339468229312555)
                                await channel2.send('Removing 1 minute updates from channel: ' + str(channel.id))
                                removeChannelFromDatabaseSongs(channel)
        except Exception as e:
            print('Failed posting 1 minute song data.\n'+ str(e))

initialT100Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=1&event=75&tier=0').json()
initialT1000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=1&event=75&tier=1').json()
async def postT100CutoffUpdates():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            EventID = await GetCurrentEventID('en')
            if EventID:
                timeLeft = await GetEventTimeLeftSeconds('en', EventID)
                if(timeLeft > 0):
                    ids = getCutoffChannels(100)
                    global initialT100Cutoffs           
                    cutoffAPI = await GetBestdoriCutoffAPI(100)
                    if(sorted(initialT100Cutoffs.items()) != sorted(cutoffAPI.items())):
                        from startup.login import enDriver      
                        output = await GetCutoffFormatting(enDriver, 'en', 100)
                        ids = getCutoffChannels(100)
                        for i in ids:
                            channel = bot.get_channel(i)
                            if channel != None:
                                try:
                                    await channel.send('T100 update found!')
                                    await channel.send(embed=output)
                                except: 
                                    print('Removing T100 Updates from channel: ' + str(channel.id))
                                    rmChannelFromCutoffDatabase(channel, 100)
                        initialT100Cutoffs = cutoffAPI
                await asyncio.sleep(60)
        except Exception as e:
            print('Failed posting t100 data.\n'+ str(e))


async def postT1000CutoffUpdates():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            EventID = await GetCurrentEventID('en')
            if EventID:
                timeLeft = await GetEventTimeLeftSeconds('en', EventID)
                if(timeLeft > 0):
                    ids = getCutoffChannels(1000)
                    global initialT1000Cutoffs           
                    cutoffAPI = await GetBestdoriCutoffAPI(1000)
                    if(sorted(initialT1000Cutoffs.items()) != sorted(cutoffAPI.items())):
                        from startup.login import enDriver
                        output = await GetCutoffFormatting(enDriver, 'en', 1000)
                        ids = getCutoffChannels(1000)
                        for i in ids:
                            channel = bot.get_channel(i)
                            if channel != None:
                                try:
                                    await channel.send('T1000 update found!')
                                    await channel.send(embed=output)
                                except: 
                                    print('Removing T1000 Updates from channel: ' + str(channel.id))
                                    rmChannelFromCutoffDatabase(channel, 1000)
                        initialT1000Cutoffs = cutoffAPI
                await asyncio.sleep(60)
        except Exception as e:
            print('Failed posting t1000 data.\n'+ str(e))

#################
#   Bot Stuff   #
#################   
@bot.event
async def on_ready():
    print("Connected..")
    CurrentGuildCount = 0
    for guild in bot.guilds:
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


"""
#bot.loop.create_task(updateAPI()) #pretty sure this is unused, keeping for now just incase
bot.loop.create_task(postEventNotif('en'))
bot.loop.create_task(postEventNotif('jp'))
bot.loop.create_task(postEventT101hr())
bot.loop.create_task(postSongUpdates1min())
bot.loop.create_task(postT1000CutoffUpdates())
bot.loop.create_task(postBestdoriNews())
bot.loop.create_task(postT100CutoffUpdates())
bot.loop.create_task(postEventT102min())
"""
bot.get_command('help').hidden=True
bot.load_extension("commands.cogs.Game")
bot.load_extension("commands.cogs.Misc")
bot.load_extension("commands.cogs.Admin")
bot.load_extension("commands.cogs.Event")
bot.load_extension("commands.cogs.Updates")
bot.load_extension("commands.cogs.Moderation")

bot.run(TOKEN) 