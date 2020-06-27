import requests
import json
import time
import aiohttp

"""
async def getBandoriGAAPI(server: str):
    async with aiohttp.ClientSession() as session:
        api = 'https://api.bandori.ga/v1/%s/event' %str(server)
        async with session.get(api) as BandoriGAAPI:
            return await BandoriGAAPI.json()
"""


async def GetBestdoriRateAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/tracker/rates.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriEventAPI(EventID: int):
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/events/%s.json' %str(EventID)
        async with session.get(api) as CurrentEventAPI:
            return await CurrentEventAPI.json()

async def GetTierKey(tier):
    if tier == 100:
        tier = '0'
    elif tier == 1000:
        tier = '1'
    else:
        tier = '2'
    return int(tier)


async def GetBestdoriCutoffAPI(server: int, tier: int):
    async with aiohttp.ClientSession() as session:
        from commands.formatting.EventCommands import GetCurrentEventID
        EventID = await GetCurrentEventID(server)
        tier = await GetTierKey(tier)
        ServerKey = await GetServerAPIKey(server)
        api = 'https://bestdori.com/api/tracker/data?server={}&event={}&tier={}'.format(
            ServerKey, str(EventID), tier)
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriPlayerLeaderboardsAPI(server: str, lbtype: str, entries: int):
    async with aiohttp.ClientSession() as session:
        if server == 'en':
            server = 1
        elif server == 'jp':
            server = 0
        elif server == 'tw':
            server = 2
        elif server == 'cn':
            server = 3
        elif server == 'kr':
            server = 4
        if lbtype in ['highscores','hs']:
            lbtype = 'hsr'
        elif lbtype in ['fullcombo','fc']:
            lbtype = 'fullComboCount'
        elif lbtype in 'cleared':
            lbtype = 'cleared'
        elif lbtype in ['rank','ranks']:
            lbtype = 'rank'
        api = 'https://bestdori.com/api/sync/list/player?server=%s&stats=%s&limit=%s&offset=0' %(str(server),lbtype,str(entries))
        async with session.get(api) as r:
            return await r.json()

async def GetSongAPI():
    async with aiohttp.ClientSession() as session:
        apiURL = 'https://bestdori.com/api/songs/all.7.json'
        async with session.get(apiURL) as r:
            return await r.json()
 
async def GetBestdoriAllEventsAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/events/all.5.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriAllCharactersAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/characters/all.2.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriBannersAPI(eventId: int):
    async with aiohttp.ClientSession() as session:
        eventId = str(eventId)
        api = 'https://bestdori.com/api/events/%s.json' %eventId
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriEventArchivesAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/archives/all.5.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriAllCardsAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/cards/all.5.json'
        async with session.get(api) as r:
            return await r.json()
        
async def GetBestdoriAllCharasAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/characters/all.2.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriAllTitlesAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/degrees/all.3.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriCharasAPI(charaId: int):
    async with aiohttp.ClientSession() as session:
        eventId = str(charaId)
        api = 'https://bestdori.com/api/characters/%s.json' %eventId
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriAllGachasAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/gacha/all.5.json'
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriGachaAPI(gachaid: int):
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/gacha/%s.json' %str(gachaid)
        async with session.get(api) as r:
            return await r.json()

async def GetBestdoriCardAPI(cardid: int):
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/cards/%s.json' %str(cardid)
        async with session.get(api) as r:
            return await r.json()

async def GetSongMetaAPI():
    async with aiohttp.ClientSession() as session:
        api = 'https://bestdori.com/api/songs/meta/all.5.json'
        async with session.get(api) as r:
            return await r.json()

async def GetServerAPIKey(server: str):
    if server == 'en':
        Key = 1 
    elif server == 'jp':
        Key = 0 
    elif server == 'tw':
        Key = 2
    elif server == 'cn':
        Key = 3
    elif server == 'kr':
        Key = 4
    return Key

