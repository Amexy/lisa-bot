import requests
import asyncio
import json
import re
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from tabulate import tabulate
from commands.apiFunctions import GetBestdoriAllEventsAPI, GetSongAPI
from commands.formatting.EventCommands import get_event_name
from startup.login import enICEObject, jpICEObject
from protodefs.ranks import t10ranks
from google.protobuf.json_format import MessageToJson

async def GetT10ArchiveFile(EventID: int, Server: str):
    from startup.google import CheckGoogleFile
    import discord
    if await CheckGoogleFile(EventID, Server):
        file = 't10archives/%s/' %(Server) + Server + '_' + str(EventID) + '.txt'
        FileToAttach = discord.File(file)
        return FileToAttach


async def t10logging(server: str, eventid: int, songs: bool = False):
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Eastern'))
    if server == 'en':
        ice = enICEObject
    else:
        ice = jpICEObject
    eventranking = await t10ranks(ice, server, eventid)
    i = 1
    if songs:
        songAPI = await GetSongAPI()
        if eventranking.cl_song_ranking:
            for song in eventranking.cl_song_ranking:
                i = 1
                songName = songAPI[str(song.live_id)]['musicTitle'][1]
                if songName is None:
                    songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    stringCheck
                songName = stringCheck(songName)
                fullPath = 't10archives' + '/' + server + '/' + str(eventid) + '/' + songName + '.txt'
                with open(fullPath, 'a+', encoding='utf-8') as file:
                    file.write("\n" + now_time.strftime(fmt) + "\n")
                    for x in song.top_10.contents:
                        for y in x.card_info:
                            if(x.main_team.card_1 == y.card_no):
                                c1sl = (y.skill_level)
                            if(x.main_team.card_2 == y.card_no):
                                c2sl = (y.skill_level)
                            if(x.main_team.card_3 == y.card_no):
                                c3sl = (y.skill_level)
                            if(x.main_team.card_4 == y.card_no):
                                c4sl = (y.skill_level)
                            if(x.main_team.card_5 == y.card_no):
                                c5sl = (y.skill_level)
                        x.name = stringCheck(x.name)
                        id = x.user_id
                        file.write(str(i) + " " + "{:,}".format(x.score) + " " + str(x.user_id) + " " + str(x.main_team.card_4) + '(' + str(c4sl) + ')' + " " + str(x.main_team.card_2) + '(' + str(c2sl) + ')' + " " + str(x.main_team.card_1) + '(' + str(c1sl) + ')'+ " " + str(x.main_team.card_3) + '(' + str(c3sl) + ')' + " " + str(x.main_team.card_5) + '(' + str(c5sl) + ')' + " " + str(x.name) + "\n")
                        i += 1
        elif eventranking.vs_song_ranking:
            for song in eventranking.vs_song_ranking:
                i = 1
                songName = songAPI[str(song.live_id)]['musicTitle'][1]
                if songName is None:
                    songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    stringCheck
                songName = stringCheck(songName)
                fullPath = 't10archives' + '/' + server + '/' + str(eventid) + '/' + songName + '.txt'
                with open(fullPath, 'a+', encoding='utf-8') as file:
                    file.write("\n" + now_time.strftime(fmt) + "\n")
                    for x in song.top_10.contents:
                        for y in x.card_info:
                            if(x.main_team.card_1 == y.card_no):
                                c1sl = (y.skill_level)
                            if(x.main_team.card_2 == y.card_no):
                                c2sl = (y.skill_level)
                            if(x.main_team.card_3 == y.card_no):
                                c3sl = (y.skill_level)
                            if(x.main_team.card_4 == y.card_no):
                                c4sl = (y.skill_level)
                            if(x.main_team.card_5 == y.card_no):
                                c5sl = (y.skill_level)
                        x.name = stringCheck(x.name)
                        id = x.user_id
                        file.write(str(i) + " " + "{:,}".format(x.score) + " " + str(x.user_id) + " " + str(x.main_team.card_4) + '(' + str(c4sl) + ')' + " " + str(x.main_team.card_2) + '(' + str(c2sl) + ')' + " " + str(x.main_team.card_1) + '(' + str(c1sl) + ')'+ " " + str(x.main_team.card_3) + '(' + str(c3sl) + ')' + " " + str(x.main_team.card_5) + '(' + str(c5sl) + ')' + " " + str(x.name) + "\n")
                        i += 1
                        
    else: 
        for x in eventranking.top_10.contents:
            x.name = stringCheck(x.name)
            id = x.user_id
            fullPath = 't10archives' + '/' + server + '/' + str(eventid) + '/' + str(id) + '.txt'
            with open(fullPath, 'a', encoding='utf-8') as file:
                file.write(now_time.strftime(fmt) + " " + str(i) + " " + "{:,}".format(x.event_pts) + " " + str(x.user_level) + " " + str(x.user_id) + " " + str(x.name) + "\n")
            i += 1

async def get_t10_info(server: str, event_id: int, songs: bool):
    from commands.apiFunctions import get_bestdori_t10_api, get_bestdori_t10_song_api
    
# functions to format t10 output
async def t10formatting(server: str, event_id: int, ids: bool):
    from commands.apiFunctions import get_bestdori_t10_api
    from commands.formatting.misc_functions import format_number
    import time
    t10_api = await get_bestdori_t10_api(server, event_id)
    event_name = await get_event_name(server, event_id)
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Central'))    
    i = 1
    entries = []
    if ids:
        for points in t10_api['points']:
            uid = points['uid']
            for user in t10_api['users']:
                if uid == user['uid']:
                    entries.append([i, format_number(points['value']), user['rank'], user['uid'], stringCheck(user['name'])])
                    break
            i += 1
        output = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + event_name + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "ID","Player"]) + "```")
    else:
        for points in t10_api['points']:
            uid = points['uid']
            for user in t10_api['users']:
                if uid == user['uid']:
                    entries.append([i, format_number(points['value']), user['rank'], stringCheck(user['name'])])
                    break
            i += 1
        output = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + event_name + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "Player"]) + "```")
    return output

# removing ids bool since ids is pretty much required for song data due to name changing. i'm also too lazy to implement proper if/else logic
async def t10songsformatting(server: str, event_id: int):
    try:
        from commands.apiFunctions import GetBestdoriEventAPI, get_bestdori_t10_song_api
        from commands.formatting.misc_functions import format_number
        songs_output = []
        song_ids = []
        song_api = await GetSongAPI()
        event_api = await GetBestdoriEventAPI(event_id)
        for x in event_api['musics'][0]:
            song_ids.append(x['musicId'])
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        now_time = datetime.now(timezone('US/Central'))
        for song in song_ids:
            i = 1
            entries = []
            song_name = song_api[str(song)]['musicTitle'][1]
            if song_name is None:
                song_name = song_api[str(song)]['musicTitle'][0]
            output = '```'
            output += "  Song:  " + song_name + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
            t10_api = await get_bestdori_t10_song_api(server, event_id, song)
            for points in t10_api['points']:
                uid = points['uid']
                for user in t10_api['users']:
                    if uid == user['uid']:
                        entries.append([i, format_number(points['value']), user['rank'], user['uid'],stringCheck(user['name'])])
                        break
                i += 1
            output += tabulate(entries,tablefmt="plain",headers=["#","Score","Level","ID","Player"])  + "```"
            songs_output.append(output)
    except KeyError:
        songs_output = "This event doesn't have any songs"
    return songs_output


async def t10membersformatting(server: str, event_id: int, songs: bool):
    from commands.apiFunctions import lookup_bestdori_player
    from commands.formatting.misc_functions import format_number
    entries = []
    i = 1
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Central'))
    event_name = await get_event_name(server, event_id)
    if not songs:
        from commands.apiFunctions import get_bestdori_t10_api
        t10_api = await get_bestdori_t10_api(server, event_id)
        for points in t10_api['points']:
            uid = points['uid']
            for user in t10_api['users']:
                if uid == user['uid']:
                    band_members = []
                    user_info = await lookup_bestdori_player(server, uid)
                    for card in user_info['data']['profile']['mainDeckUserSituations']['entries']:
                        band_members.append([card['situationId'],card['skillLevel']])
                    entries.append([i, format_number(points['value']), user['rank'], user['uid'], f"{band_members[3][0]}({band_members[3][1]})", f"{band_members[1][0]}({band_members[1][1]})", f"{band_members[0][0]}({band_members[0][1]})", f"{band_members[2][0]}({band_members[2][1]})", f"{band_members[4][0]}({band_members[4][1]})",stringCheck(user['name'])]) #lmao
                    break
            i += 1
        output = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + event_name + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "ID","C1","C2","C3","C4","C5","Player"]) + "```")
    else:
        try:
            from commands.apiFunctions import get_bestdori_t10_song_api, GetBestdoriEventAPI
            output = []
            song_ids = []
            song_api = await GetSongAPI()
            event_api = await GetBestdoriEventAPI(event_id)
            for x in event_api['musics'][0]:
                song_ids.append(x['musicId'])
            for song in song_ids:
                i = 1
                entries = []
                song_name = song_api[str(song)]['musicTitle'][1]
                if song_name is None:
                    song_name = song_api[str(song)]['musicTitle'][0]
                songs_output = '```'
                songs_output += "  Song:  " + song_name + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                t10_api = await get_bestdori_t10_song_api(server, event_id, song)
                for points in t10_api['points']:
                    uid = points['uid']
                    for user in t10_api['users']:
                        if uid == user['uid']:
                            band_members = []
                            user_info = await lookup_bestdori_player(server, uid)
                            for card in user_info['data']['profile']['mainDeckUserSituations']['entries']:
                                band_members.append([card['situationId'],card['skillLevel']])
                            entries.append([i, format_number(points['value']), user['rank'], user['uid'],f"{band_members[3][0]}({band_members[3][1]})", f"{band_members[1][0]}({band_members[1][1]})", f"{band_members[0][0]}({band_members[0][1]})", f"{band_members[2][0]}({band_members[2][1]})", f"{band_members[4][0]}({band_members[4][1]})",stringCheck(user['name'])])
                            break
                    i += 1
                songs_output += tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "ID","C1","C2","C3","C4","C5","Player"])  + "```"
                output.append(songs_output)
        except KeyError:
            output = "This event doesn't have any songs"
    return output
        

def stringCheck(string: str):
    import re
    string = string.replace('```','')
    string = string.replace("?",'')
    string = re.sub('(\[(\w{6}|\w{2})\])','', string)
    string = re.sub('\[([CcIiBbSsUu]|(sup|sub){1})\]', '', string)
    return string


