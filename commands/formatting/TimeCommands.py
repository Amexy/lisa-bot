import requests
import discord
import time
import math
import asyncio
from tabulate import tabulate
from datetime import datetime
from datetime import timedelta
from pytz import timezone


async def GetCurrentTime():
    currentTime = time.time()*1000.0
    return currentTime

async def GetEventTimeLeftSeconds(server: str, eventid: int):
    CurrentTime = await GetCurrentTime()
    EventEndTime = await GetEventEndTime(server, eventid)
    TimeLeftSeconds = (float(EventEndTime) - CurrentTime) / 1000
    return TimeLeftSeconds

async def GetEventEndTime(server: str, eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI
    if server == 'en':
        TimeKey = 1 # en
    else: 
        TimeKey = 0 # jp 
    api = await GetBestdoriEventAPI(eventid)  
    EventEndTime = api['endAt'][TimeKey]
    return float(EventEndTime)

async def GetEventStartTime(server: str, eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI
    if server == 'en':
        TimeKey = 1 # en
    else: 
        TimeKey = 0 # jp 
    api = await GetBestdoriEventAPI(eventid)  
    EventStartTime = api['startAt'][TimeKey]
    return float(EventStartTime)

async def GetEventProgress(server: str, eventid: int):
    EventEndTime = await GetEventEndTime(server, eventid)
    CurrentTime = await GetCurrentTime()
    StartTime = await GetEventStartTime(server, eventid)
    TimeLeft = EventEndTime - CurrentTime

    if(TimeLeft < 0):
        EventProgressPercent = str(100)
    else:
        EventLength = EventEndTime - StartTime
        EventProgressPercent = round((((EventLength - TimeLeft) / EventLength) * 100), 2)
    if int(EventProgressPercent) < 0:
        EventProgressPercent = 100
    return EventProgressPercent

async def GetTimeLeftCommandOutput(server: str, eventid: int):
    TimeLeftSeconds = await GetEventTimeLeftSeconds(server, eventid)
    if(TimeLeftSeconds < 0):
        output = "The event is completed."
    else:
        EventEndTime = await GetEventEndTime(server, eventid) 
        EndDate = datetime.fromtimestamp(EventEndTime / 1000).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' UTC'
        EventProgress = await GetEventProgress(server,eventid)
        from commands.formatting.EventCommands import GetEventName, GetEventAttribute
        EventName = await GetEventName(server, eventid)
        from commands.apiFunctions import GetBestdoriBannersAPI
        BannerAPI = await GetBestdoriBannersAPI(eventid)
        Attribute = await GetEventAttribute(eventid)
        if(Attribute == 'powerful'):
            EmbedColor = 0x0ff345a
        elif(Attribute == 'cool'):
            EmbedColor = 0x04057e3
        elif(Attribute == 'pure'):
            EmbedColor = 0x044c527
        else:
            EmbedColor = 0x0ff6600
        BannerName = BannerAPI['assetBundleName']
        EventUrl = 'https://bestdori.com/info/events/' + str(eventid)
        Thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,BannerName)
        EventProgress = str(EventProgress) + "%"
        StringTimeLeft = await GetTimeLeftString(server,eventid)

        embed=discord.Embed(title=EventName, url=EventUrl, color=EmbedColor)
        embed.set_thumbnail(url=Thumbnail)
        embed.add_field(name='Time Left', value=StringTimeLeft, inline=True)
        embed.add_field(name='Progress', value=EventProgress, inline=True)
        embed.add_field(name='End Date', value=EndDate, inline=True)
        output = embed

    return output
 
async def GetTimeLeftString(server: str, eventid):
    TimeLeftSeconds = await GetEventTimeLeftSeconds(server, eventid)
    if(TimeLeftSeconds < 0):
        StringTimeLeft = "The event is completed."
    else:
        TimeLeftSeconds = TimeLeftSeconds
        Days = str(int(TimeLeftSeconds // 86400))
        Hours = str(int(TimeLeftSeconds // 3600 % 24))
        Minutes = str(int(TimeLeftSeconds // 60 % 60))
        StringTimeLeft = (Days + "d " + Hours + "h " + Minutes + "m")
    return StringTimeLeft



