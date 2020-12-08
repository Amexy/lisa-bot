import datetime
import requests
import json
import time
import aiohttp
#from main import ctime

"""
@cachedRequest
async def GetBandoriGAAPI(server: str):
        return 'https://api.bandori.ga/v1/%s/event' %str(server)
        async with session.get(api) as BandoriGAAPI:
            return await BandoriGAAPI.json()
"""

_cache = {}
_etags = {}

use_cache = True

def cachedRequest(func):
    async def wrapper(*args, **kwargs):
        url = await func(*args, **kwargs)
        if use_cache:
            async with aiohttp.ClientSession() as session:
                etag = _etags.get(func)
                async with session.get(url, headers={'If-None-Match': etag} if etag else None) as r:
                    if r.status != 304:
                        _etags[func] = r.headers['ETag']
                        _cache[func] = await r.json()
            return _cache[func]
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    return await r.json()

    return wrapper


#@ctime
@cachedRequest
async def GetBestdoriRateAPI():
    return 'https://bestdori.com/api/tracker/rates.json'

#@ctime
@cachedRequest
async def GetBestdoriEventAPI(EventID: int):
    return 'https://bestdori.com/api/events/%s.json' % str(EventID)

#@ctime 
@cachedRequest
async def get_bestdori_all_cards_api2():
    return 'https://bestdori.com/api/cards/all.2.json'

async def GetTierKey(tier):
    if tier == 100:
        tier = '0'
    elif tier == 1000 or tier == 500:
        tier = '1'
    elif tier == 2000 or tier == 2500:
        tier = '2'
    elif tier == 5000:
        tier = '3'
    elif tier == 10000:
        tier = '4'
    else:
        tier = '0'
    return int(tier)

#@ctime
@cachedRequest
async def GetBestdoriCutoffAPI(server: int, tier: int):
    from commands.formatting.EventCommands import GetCurrentEventID
    EventID = await GetCurrentEventID(server)
    tier = await GetTierKey(tier)
    ServerKey = await GetServerAPIKey(server)
    return 'https://bestdori.com/api/tracker/data?server={}&event={}&tier={}'.format(
        ServerKey, str(EventID), tier)

#@ctime
@cachedRequest
async def GetBestdoriPlayerLeaderboardsAPI(server: str, lbtype: str, entries: int):
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
    if lbtype in ['highscores', 'hs']:
        lbtype = 'hsr'
    elif lbtype in ['fullcombo', 'fc']:
        lbtype = 'fullComboCount'
    elif lbtype in 'cleared':
        lbtype = 'cleared'
    elif lbtype in ['rank', 'ranks']:
        lbtype = 'rank'
    return 'https://bestdori.com/api/sync/list/player?server=%s&stats=%s&limit=%s&offset=0' % (
        str(server), lbtype, str(entries))

#@ctime
@cachedRequest
async def GetSongAPI():
    return 'https://bestdori.com/api/songs/all.7.json'

#@ctime
@cachedRequest
async def GetBestdoriAllEventsAPI():
    return 'https://bestdori.com/api/events/all.5.json'

#@ctime
@cachedRequest
async def GetBestdoriAllCharactersAPI2():
    return 'https://bestdori.com/api/characters/all.2.json'

#@ctime
@cachedRequest
async def GetBestdoriAllCharactersAPI5():
    return 'https://bestdori.com/api/characters/all.5.json'

#@ctime
@cachedRequest
async def GetBestdoriBannersAPI(eventId: int):
    eventId = str(eventId)
    return 'https://bestdori.com/api/events/%s.json' % eventId

#@ctime
@cachedRequest
async def GetBestdoriEventArchivesAPI():
    return 'https://bestdori.com/api/archives/all.5.json'

#@ctime
@cachedRequest
async def get_bestdori_all_cards_api5():
    return 'https://bestdori.com/api/cards/all.5.json'

#@ctime
@cachedRequest
async def GetBestdoriAllCharasAPI():
    return 'https://bestdori.com/api/characters/all.2.json'

#@ctime
@cachedRequest
async def Get_bestdori_title_names_api(server: str):
    return f'https://bestdori.com/api/explorer/{server}/assets/thumb/degree.json'

#@ctime
@cachedRequest
async def GetBestdoriAllTitlesAPI():
    return 'https://bestdori.com/api/degrees/all.3.json'

#@ctime
@cachedRequest
async def GetBestdoriCharasAPI(charaId: int):
    eventId = str(charaId)
    return 'https://bestdori.com/api/characters/%s.json' % eventId

#@ctime
@cachedRequest
async def GetBestdoriAllGachasAPI():
    return 'https://bestdori.com/api/gacha/all.5.json'

#@ctime
@cachedRequest
async def GetBestdoriGachaAPI(gachaid: int):
    return 'https://bestdori.com/api/gacha/%s.json' % str(gachaid)

#@ctime
@cachedRequest
async def GetBestdoriCardAPI(cardid: int):
    return 'https://bestdori.com/api/cards/%s.json' % str(cardid)

#@ctime
@cachedRequest
async def GetSongMetaAPI():
    return 'https://bestdori.com/api/songs/meta/all.5.json'


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
