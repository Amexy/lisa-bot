import requests
import discord
import time
import math
import asyncio
from tabulate import tabulate
from datetime import datetime
from datetime import timedelta
from pytz import timezone

from commands.formatting.EventCommands import is_event_active


async def GetCurrentTime():
    currentTime = time.time()*1000.0
    return currentTime

async def GetEventTimeLeftSeconds(server: str, eventid: int):
    CurrentTime = await GetCurrentTime()
    EventEndTime = await get_event_end_time(server, eventid)
    TimeLeftSeconds = (float(EventEndTime) - CurrentTime) / 1000
    return TimeLeftSeconds

async def get_event_end_time(server: str, eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
    TimeKey = await GetServerAPIKey(server)
    api = await GetBestdoriEventAPI(eventid)  
    EventEndTime = api['endAt'][TimeKey]
    return float(EventEndTime)

async def GetEventStartTime(server: str, eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
    TimeKey = await GetServerAPIKey(server)
    api = await GetBestdoriEventAPI(eventid)  
    EventStartTime = api['startAt'][TimeKey]
    return float(EventStartTime)

async def get_event_progress(server: str, eventid: int):
    EventEndTime = await get_event_end_time(server, eventid)
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

async def get_time_to_next_event_formatted(server: str, eventid: int):
    current_time = await GetCurrentTime()
    event_start_time = await GetEventStartTime(server, eventid)
    time_to_event = (event_start_time - current_time) / 1000
    days = str(int(time_to_event // 86400))
    hours = str(int(time_to_event // 3600 % 24))
    minutes = str(int(time_to_event // 60 % 60))
    return (days + "d " + hours + "h " + minutes + "m")
     
async def get_time_left_command_output(server: str, eventid: int):
    from commands.formatting.EventCommands import get_event_name, get_event_attribute
    from commands.apiFunctions import get_bestdori_banners_api
    event_active = await is_event_active(server, eventid)
    current_event_name = await get_event_name(server, eventid)
    event_end_time = datetime.fromtimestamp(await get_event_end_time(server, eventid) / 1000).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' UTC'
    event_progress = f"{await get_event_progress(server,eventid)}%" if event_active else "N/A"
    banner_api = await get_bestdori_banners_api(eventid)
    event_attribute = await get_event_attribute(eventid)
    if(event_attribute == 'powerful'):
        embed_color = 0x0ff345a
    elif(event_attribute == 'cool'):
        embed_color = 0x04057e3
    elif(event_attribute == 'pure'):
        embed_color = 0x044c527
    else:
        embed_color = 0x0ff6600
    banner_name = banner_api['assetBundleName']
    event_url = 'https://bestdori.com/info/events/' + str(eventid)
    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,banner_name)
    time_left = await GetTimeLeftString(server,eventid) if event_active else await get_time_to_next_event_formatted(server, eventid)

    embed=discord.Embed(title=current_event_name, url=event_url, color=embed_color)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Time Left' if event_active else 'Begins In', value=time_left, inline=True)
    embed.add_field(name='Progress', value=event_progress, inline=True)
    embed.add_field(name='End Date', value=event_end_time, inline=True)
    embed.set_footer(text=f"\n\n\nFor more info, try .event {server} command\n{datetime.now(timezone('US/Eastern'))}")
    output = embed
    return output
 
async def GetEventLengthSeconds(server, eventid):
    from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
    API = await GetBestdoriEventAPI(eventid)
    Key = await GetServerAPIKey(server)
    EventLengthSeconds = (float(API['endAt'][Key]) - float(API['startAt'][Key])) / 1000
    return EventLengthSeconds
    
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