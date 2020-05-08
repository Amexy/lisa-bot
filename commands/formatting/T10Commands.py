import requests
import asyncio
import json
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from tabulate import tabulate
from commands.apiFunctions import GetBestdoriAllEventsAPI, GetSongAPI
from commands.formatting.EventCommands import GetEventName
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

# functions to format t10 output
async def t10formatting(server: str, eventid: int, ids: bool):
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Central'))
    eventName = await GetEventName(server, eventid)
    if server == 'en':
        ice = enICEObject
    else:
        ice = jpICEObject
    eventranking = await t10ranks(ice, server, eventid)
    if not eventranking.top_10.contents:
        output = (f'No data found for event `{eventid}` on `{server}`. You can use the `.t10e` command to find which events have data. If you suspect this is an error, please use the `.notify` command')
    else:
        if(ids):
            entries = []
            i = 1
            for x in eventranking.top_10.contents:
                x.name = stringCheck(x.name)
                entries.append([
                    (str(i) + "."),
                    "{:,}".format(x.event_pts),
                    x.user_level,
                    str(x.user_id),
                    str(x.name)   
                ])
                i += 1
            output = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + eventName + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "ID","Player"]) + "```")
        else:
            entries = []
            i = 1
            for x in eventranking.top_10.contents:
                x.name = stringCheck(x.name)
                entries.append([
                    (str(i) + "."),
                    "{:,}".format(x.event_pts),
                    x.user_level,
                    str(x.name)
                ])
                i += 1
            output = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + eventName + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "Player"]) + "```")
    return output

async def t10songsformatting(server: str, eventid: int, ids: bool):
    entries = []
    songsOutput = []
    i = 1
    songAPI = await GetSongAPI()
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Eastern'))
    if server == 'en':
        ice = enICEObject
    else:
        ice = jpICEObject
    eventranking= await t10ranks(ice, server, eventid)
    if not eventranking.top_10.contents:
        songsOutput = (f'No song data found for event `{eventid}` on `{server}`. You can use the `.t10e` command to find which events have data. If you suspect this is an error, please use the `.notify` command')
    else:
        if ids:
            if eventranking.cl_song_ranking:
                for song in eventranking.cl_song_ranking:
                    i = 1
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    output = '```'
                    output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
                        entries.append([
                        (str(i) + "."),
                        "{:,}".format(x.score),
                        str(x.user_id),
                        str(x.name)
                    ])
                        i += 1
                    output += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","Player"])  + "```"
                    songsOutput.append(output)
                    entries = []
            elif eventranking.vs_song_ranking:
                for song in eventranking.vs_song_ranking:
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]                    
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    songsOutput = '```'
                    songsOutput += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
                        entries.append([
                        (str(i) + "."),
                        "{:,}".format(x.score),
                        str(x.user_id),
                        str(x.name)
                    ])
                        i += 1
                    songsOutput += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","Player"])  + "```"
            else:
                songsOutput = "This event doesn't have a song ranking."
        else:
            if eventranking.cl_song_ranking:
                for song in eventranking.cl_song_ranking:
                    i = 1
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    output = '```'
                    output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
                        entries.append([
                        (str(i) + "."),
                        "{:,}".format(x.score),
                        str(x.name)
                    ])
                        i += 1
                    output += tabulate(entries,tablefmt="plain",headers=["#","Score","Player"])  + "```"
                    songsOutput.append(output)
                    entries = []
            elif eventranking.vs_song_ranking:
                for song in eventranking.vs_song_ranking:
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]                    
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    songsOutput = '```'
                    songsOutput += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
                        entries.append([
                        (str(i) + "."),
                        "{:,}".format(x.score),
                        str(x.name)
                    ])
                        i += 1
                    songsOutput += tabulate(entries,tablefmt="plain",headers=["#","Score","Player"])  + "```"
            else:
                songsOutput = "This event doesn't have a song ranking."

    return songsOutput

async def t10membersformatting(server: str, eventid: int, songs: bool):
    i = 1
    entries = []
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Eastern'))
    eventName = await GetEventName(server, eventid)
    #optimal = []
    if server == 'en':
        ice = enICEObject
    else:
        ice = jpICEObject
    eventranking= await t10ranks(ice, server, eventid)
    if not eventranking.top_10.contents:
        songsOutput = (f'No data found for event `{eventid}` on `{server}`. You can use the `.t10e` command to find which events have data. If you suspect this is an error, please use the `.notify` command')
    else:
        if songs:
            songsOutput = []
            i = 1
            fmt = "%Y-%m-%d %H:%M:%S %Z%z"
            songAPI = await GetSongAPI()
            if eventranking.cl_song_ranking:
                for song in eventranking.cl_song_ranking:
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    output = '```'
                    output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
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
                        entries.append([
                            (str(i) + "."),
                            "{:,}".format(x.score),
                            str(x.user_id),
                            str(x.main_team.card_4) + '(' + str(c4sl) + ')',
                            str(x.main_team.card_2) + '(' + str(c2sl) + ')',
                            str(x.main_team.card_1) + '(' + str(c1sl) + ')',
                            str(x.main_team.card_3) + '(' + str(c3sl) + ')',
                            str(x.main_team.card_5) + '(' + str(c5sl) + ')',
                            str(x.name)
                            ])
                        i += 1
                    output += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","C1","C2","C3","C4","C5","Player"])  + "```"
                    songsOutput.append(output)
                    entries = []
                    i = 1
            elif eventranking.vs_song_ranking:
                for song in eventranking.vs_song_ranking:
                    songName = songAPI[str(song.live_id)]['musicTitle'][1]
                    if songName is None:
                        songName = songAPI[str(song.live_id)]['musicTitle'][0]
                    output = '```'
                    output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
                    for x in song.top_10.contents:
                        x.name = stringCheck(x.name)
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
                        entries.append([
                        (str(i) + "."),
                        "{:,}".format(x.score),
                        str(x.user_id),
                        str(x.main_team.card_4) + '(' + str(c4sl) + ')',
                        str(x.main_team.card_2) + '(' + str(c2sl) + ')',
                        str(x.main_team.card_1) + '(' + str(c1sl) + ')',
                        str(x.main_team.card_3) + '(' + str(c3sl) + ')',
                        str(x.main_team.card_5) + '(' + str(c5sl) + ')',
                        str(x.name)
                    ])
                        i += 1
                    output += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","C1","C2","C3","C4","C5","Player"])  + "```"
                    songsOutput.append(output)
            else:
                songsOutput = "This event doesn't have a song ranking."
        else:
            for x in eventranking.top_10.contents:
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
                entries.append([
                    (str(i) + "."),
                    "{:,}".format(x.event_pts),
                    x.user_level,
                    str(x.user_id),
                    str(x.main_team.card_4) + '(' + str(c4sl) + ')',
                    str(x.main_team.card_2) + '(' + str(c2sl) + ')',
                    str(x.main_team.card_1) + '(' + str(c1sl) + ')',
                    str(x.main_team.card_3) + '(' + str(c3sl) + ')',
                    str(x.main_team.card_5) + '(' + str(c5sl) + ')',
                    str(x.name)
                ])
                i += 1
            songsOutput = ("```" + "  Time:  " + now_time.strftime(fmt) + "\n  Event: " + eventName + "\n\n" + tabulate(entries, tablefmt="plain", headers=["#", "Points", "Level", "ID","C1","C2","C3","C4","C5","Player"]) + "```")
    return songsOutput


def stringCheck(string: str):
    if "```" in string:
        string = string.replace('```','')
    if "?" in string:
        string = string.replace("?",'')
    return string


#going to remove this since there needs to be a way to return 3 values for challenge lives, but not aware of how to do it right now
"""
def t10membersSongFormatting(server: str, eventid: int):
    entries = []
    i = 1
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    await songAPI =   songAPI()
    now_time = datetime.now(timezone('US/Eastern'))
    eventranking=t10ranks(server, eventid)
    if eventranking.cl_song_ranking:
        for song in eventranking.cl_song_ranking:
            songName = await songAPI[str(song.live_id)]['musicTitle'][1]
            output = '```'
            output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
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
                entries.append([
                (str(i) + "."),
                "{:,}".format(x.score),
                str(x.name)
            ])
                i += 1
            output += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","C1","C2","C3","C4","C5","Player"])  + "```"
            await ctx.send(output)
            entries = []
    elif eventranking.vs_song_ranking:
        for song in eventranking.vs_song_ranking:
            songName = await songAPI[str(song.live_id)]['musicTitle'][1]
            output = '```'
            output += "  Song:  " + songName + "\n  Time:  " + now_time.strftime(fmt) + "\n\n"
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
                entries.append([
                (str(i) + "."),
                "{:,}".format(x.score),
                str(x.user_id),
                str(x.main_team.card_4) + '(' + str(c4sl) + ')',
                str(x.main_team.card_2) + '(' + str(c2sl) + ')',
                str(x.main_team.card_1) + '(' + str(c1sl) + ')',
                str(x.main_team.card_3) + '(' + str(c3sl) + ')',
                str(x.main_team.card_5) + '(' + str(c5sl) + ')',
                str(x.name)
            ])
                i += 1
            output += tabulate(entries,tablefmt="plain",headers=["#","Score","ID","C1","C2","C3","C4","C5","Player"])  + "```"
            entries = []
    else:
        output = "This event doesn't have a song ranking."
    return output
"""