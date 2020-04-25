from commands.apiFunctions import GetSongAPI
from tabulate import tabulate
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from operator import itemgetter
from time import strftime
from time import gmtime
from commands.apiFunctions import GetBestdoriAllCharactersAPI, GetBestdoriAllEventsAPI, GetBestdoriBannersAPI, GetBestdoriEventArchivesAPI, GetBestdoriAllGachasAPI, GetBestdoriGachaAPI, GetBestdoriCardAPI, GetSongMetaAPI, GetBestdoriCharasAPI
from commands.formatting.GameCommands import GetStarsUsedOutput, GetEPGainOutput, characterOutput, GetSongInfo, GetSongMetaOutput, GetLeaderboardsOutput
from commands.formatting.TimeCommands import GetCurrentTime
import discord
import time
import requests
import math

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gacha',
                      brief='Gives info on the current gachas',
                      help="Gives info on the current gachas available. Doesn't show the gachas that are always available (new player, 3+ ticket, etc)")
    async def gacha(self, ctx, server: str = 'en'):
        api = await GetBestdoriAllGachasAPI()
        gachas = []
        gachasEnd = []
        cardDetails = []
        currentTime = await GetCurrentTime()
        for x in list(api):
            if(server == 'en'):
                if api[str(x)]['gachaName'][1] and api[str(x)]['closedAt'][1] and api[str(x)]['publishedAt'][1]:
                    closedAt = int(api[str(x)]['closedAt'][1])
                    startAt = int(api[str(x)]['publishedAt'][1])
                    gachaName = api[str(x)]['gachaName'][1]
                    gachaNameAndChars = gachaName
                    if 'Beginners' not in gachaName and '3+' not in gachaName and 'Head Start' not in gachaName:
                        if(closedAt > currentTime and currentTime > startAt):
                            gachaAPI = await GetBestdoriGachaAPI(x)
                            for y in list(gachaAPI['details'][0]):
                                if(gachaAPI['details'][0][str(y)]['weight'] == 5000):
                                    cardApi = await GetBestdoriCardAPI(y)
                                    cardChara = cardApi['characterId']
                                    cardAttr = cardApi['attribute']
                                    cardType = cardApi['type']
                                    charaApi = await GetBestdoriCharasAPI(cardChara)
                                    charaName = charaApi['characterName'][1]
                                    cardInfo = cardType.capitalize() + " " + cardAttr.capitalize() + " " + charaName 
                                    cardDetails.append(cardInfo)
                            gachas.append(gachaName)
                            gachasEnd.append(time.strftime("%d %b %Y", time.localtime(int(closedAt / 1000))))
            if(server == 'jp'):
                if api[str(x)]['gachaName'][0] and api[str(x)]['closedAt'][0] and api[str(x)]['publishedAt'][0]:
                    closedAt = int(api[str(x)]['closedAt'][0])
                    startAt = int(api[str(x)]['publishedAt'][0])
                    gachaName = api[str(x)]['gachaName'][1]
                    if gachaName is None:
                        gachaName = api[str(x)]['gachaName'][0]
                    #gachaNameAndChars = gachaName
                    if 'Beginners' not in gachaName and '3+' not in gachaName and 'Head Start' not in gachaName:
                        if(closedAt > currentTime and currentTime > startAt):
                            gachaAPI = await GetBestdoriGachaAPI(x)
                            for y in list(gachaAPI['details'][0]):
                                if(gachaAPI['details'][0][str(y)]['weight'] == 5000):
                                    cardApi = await GetBestdoriCardAPI(y)
                                    cardChara = cardApi['characterId']
                                    cardAttr = cardApi['attribute']
                                    cardType = cardApi['type']
                                    charaApi = await GetBestdoriCharasAPI(cardChara)
                                    charaName = charaApi['characterName'][1]
                                    cardInfo = cardType.capitalize() + " " + cardAttr.capitalize() + " " + charaName 
                                    cardDetails.append(cardInfo)
                            gachas.append(gachaName)
                            gachasEnd.append(time.strftime("%d %b %Y", time.localtime(int(closedAt / 1000))))
        embed=discord.Embed()
        embed.add_field(name='Gacha', value='\n'.join(gachas), inline=True)
        embed.add_field(name='End', value='\n'.join(gachasEnd), inline=True)
        embed.add_field(name='Cards', value='\n'.join(cardDetails), inline=False)

        await ctx.send(embed=embed)
        #await ctx.send("```" + tabulate(gachas,tablefmt="plain",headers=["Gacha","Ends"]) + "```")

    @commands.command(name='character',
                      aliases=['chara','c'],
                      help='Posts character info\n\nExamples\n.character lisa',
                      brief='Posts character info')
    async def characterinfo(self, ctx, character: str):
        try:
            output = await characterOutput(character)
            await ctx.send(embed=output)
        except:
            await ctx.send("Couldn't find the character entered, possible mispell?")


    @commands.command(name='starsused',
                      aliases=['su'],
                      brief="Star usage for tiering",
                      help="Provides star usage when aiming for a certain amount of EP. Challenge live calculations aren't incorporated yet. I recommended using Bestdori's event calculator.\n\nExamples\n\n.starsused 9750 100 0 2000000 3 en\n.starsused 9750 100 0 2000000 3 jp\n.starsused 9750 100 0 2000000 3 168\n.starsused 9750 100 0 2000000 3")
    async def starsused(self, ctx, epPerSong: int, begRank: int, begEP: int, targetEP: int, flamesUsed: int, *ServerOrHoursLeft):
        starsUsedTable = await GetStarsUsedOutput(epPerSong, begRank, begEP, targetEP, flamesUsed, *ServerOrHoursLeft)
        await ctx.send(starsUsedTable)

    @commands.command(name='epgain',
                      description="Provides EP gain given user-provided inputs",
                      brief="Calculates EP gain",
                      help="BPPercent should be between 1 and 150 and in intervals of 10 e.g. 10, 20, 30\nNormal Event = 1\nLive Trial = 2\nChallenge = 3\nBand Battle* = 4\n*For Band Battles, specify placement between 1-5.")
    async def epgain(self, ctx, yourScore: int, multiScore: int, bpPercent: int, flamesUsed: int, eventType: int, bbPlace: int = 0):
        ep = GetEPGainOutput(yourScore, multiScore, bpPercent, flamesUsed, eventType, bbPlace)
        await ctx.send("EP Gain: " + str(math.floor(ep)))

    @commands.command(name='event',
                      help='Posts event info, defaults to en and the current event id. Only supports EN and JP currently\n\nExamples\n.event\n.event jp\n.event en 12\n.event en Lisa\n.event jp 一閃',
                      brief='Posts event info')
    async def event(self, ctx, server: str = 'en', *event):
        from commands.formatting.EventCommands import GetEventName, GetCurrentEventID, GetEventAttribute
        from protodefs.ranks import GetEventType
        try:
            validServer = ["en","jp","tw","cn"]
            if server in validServer:
                charaAPI = await GetBestdoriAllCharactersAPI()
                eventAPI = await GetBestdoriAllEventsAPI()
                
                if event:
                    if isinstance(event, int):
                        EventName = await GetEventName(server, event)
                        EventID = event
                    else:
                        eventString = event[0]
                        for x in event:
                            if x == eventString:
                                continue
                            eventString += " %s" % x

                        try:
                            if float(str(eventString)):
                                EventID = eventString
                                EventName = eventAPI[str(EventID)]['eventName'][1] + ' (' + str(EventID) + ')'
                        except:
                            if server == 'en':
                                namePathPosition = 1
                            elif server == 'jp':
                                namePathPosition = 0
                            for x in eventAPI:
                                
                                if str(eventString).lower() in eventAPI[str(x)]['eventName'][namePathPosition].lower():
                                    EventName = eventAPI[str(x)]['eventName'][namePathPosition] + ' (' + str(x) + ')'
                                    EventID = x
                                    break
                else:
                    EventID = await GetCurrentEventID(server)
                    EventName = await GetEventName(server,EventID)

                attribute = await GetEventAttribute(EventID)
                eventType = await GetEventType(EventID)
                if(eventType == 'live_try'):
                    eventType = 'Live Try'
                if(attribute == 'powerful'):
                    embedColor = 0x0ff345a
                elif(attribute == 'cool'):
                    embedColor = 0x04057e3
                elif(attribute == 'pure'):
                    embedColor = 0x044c527
                else:
                    embedColor = 0x0ff6600

                #format time
                if(server == 'en'):
                    beginTime = eventAPI[str(EventID)]['startAt'][1]
                    endTime = eventAPI[str(EventID)]['endAt'][1]
                elif(server == 'jp'):
                    beginTime = eventAPI[str(EventID)]['startAt'][0]
                    endTime = eventAPI[str(EventID)]['endAt'][0]
                elif(server == 'tw'):
                    beginTime = eventAPI[str(EventID)]['startAt'][2]
                    endTime = eventAPI[str(EventID)]['endAt'][2]
                elif(server == 'cn'):
                    beginTime = eventAPI[str(EventID)]['startAt'][3]
                    endTime = eventAPI[str(EventID)]['endAt'][3]
                if beginTime is None:
                    beginsString = 'N/A'
                    endsString = 'N/A'
                else:
                    beginsString = int(beginTime) / 1000
                    endsString = int(endTime) / 1000
                    beginsString = datetime.fromtimestamp(beginsString).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' CST'
                    endsString = datetime.fromtimestamp(endsString).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' CST'

                members = []
                for member in eventAPI[str(EventID)]['characters']:
                    id = member['characterId']
                    member = charaAPI[str(id)]['characterName'][1]
                    members.append(member)
                
                #check to see if event requested is an active event or not
                currentTime = int(round(time.time() * 1000))
                
                if(currentTime > int(endTime)):
                    bannerAPI = await GetBestdoriBannersAPI(int(EventID))
                    archiveAPI = await GetBestdoriEventArchivesAPI()
                    cutoffs = []
                    if(server == 'en'):
                        cutoffs = (archiveAPI[str(EventID)]['cutoff'][1]).items()
                    elif(server == 'jp'):
                        cutoffs = (archiveAPI[str(EventID)]['cutoff'][0]).items()
                    elif(server == 'tw'):
                        cutoffs = (archiveAPI[str(EventID)]['cutoff'][2]).items()
                    elif(server == 'cn'):
                        cutoffs = (archiveAPI[str(EventID)]['cutoff'][3]).items()
                    bannerName = bannerAPI['assetBundleName']
                    eventUrl = 'https://bestdori.com/info/events/' + str(EventID)
                    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)
                    embed=discord.Embed(title=EventName, url=eventUrl, color=embedColor)
                    embed.set_thumbnail(url=thumbnail)
                    embed.add_field(name='Attribute', value=str(attribute).capitalize(), inline=True)
                    embed.add_field(name='Event Type', value=str(eventType).capitalize(), inline=True)
                    if cutoffs:
                        embed.add_field(name='Members', value='\n'.join(members), inline=True)
                        embed.add_field(name='Cutoffs', value='\n'.join("{}: {}".format(k, "{:,}".format(v)) for k, v in cutoffs), inline=True)
                    else:
                        embed.add_field(name='Members', value='\n'.join(members), inline=False)
                    embed.add_field(name='Start' , value=beginsString, inline=True)
                    embed.add_field(name='End', value=endsString, inline=True)
                    await ctx.send(embed=embed)
                else:
                    bannerAPI = await GetBestdoriBannersAPI(int(EventID))
                    cutoffs = []
                    bannerName = bannerAPI['assetBundleName']
                    eventUrl = 'https://bestdori.com/info/events/' + str(EventID)
                    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)
                    embed=discord.Embed(title=EventName, url=eventUrl, color=embedColor)
                    embed.set_thumbnail(url=thumbnail)
                    embed.add_field(name='Attribute', value=str(attribute).capitalize(), inline=True)
                    embed.add_field(name='Event Type', value=str(eventType).capitalize(), inline=True)
                    embed.add_field(name='Members', value='\n'.join(members), inline=False)
                    embed.add_field(name='Start' , value=beginsString, inline=True)
                    embed.add_field(name='End', value=endsString, inline=True)
                    await ctx.send(embed=embed)
            else:
                await ctx.send("Please enter a valid server (i.e. en, jp, tw, cn)")
        except Exception as e:
            print('Failed posting event data for event ' + str(event) + '\n' + str(e))
            await ctx.send("Couldn't find the event entered. If using hiragana, try kana or vice versa (e.g. きみが doesn't work, but キミが does).")

    @commands.command(name='songinfo',
                      aliases=['song','songs'],
                      description='Provides info about a song',
                      brief='Game Song information',
                      help='Please provide the song name EXACTLY as it appears in game e.g. B.O.F not BOF, b.o.f, etc.')
    async def songinfo(self, ctx, *args: str):
        try:
            songName = args[0]
            for x in args:
                if x == songName:
                    continue
                songName += " %s" % x
            string = await GetSongInfo(songName)
            await ctx.send(string)
        except: 
            await ctx.send("Couldn't find the song entered, it was possibly entered incorrectly. The song needs to be spelled exactly as it appears in game")
    

    @commands.command(name='songmeta',
                      aliases=['sm','smf','meta'],
                      brief='Shows song meta info (fever)',
                      help='Shows song meta info (fever). By default, it will show the top 10 songs. Given a list of songs (EX dif only), it will sort them based off efficiency. Assumes SL5 and 100% Perfects. I recommend using Bestdori for finer tuning.\n\nExamples\n\n.songmeta\n.sm\n.meta\n.songmeta unite guren jumpin')
    async def songmeta(self, ctx, *songs):
        if songs:
            output = await getSongMetaOutput(True, songs)
        else:
            output = await getSongMetaOutput(True)
        await ctx.send(output)

    @commands.command(name='songmetanofever',
                      aliases=['smnf','metanf'],
                      brief='Shows song meta info (no fever)',
                      help='Shows song meta info (no fever). By default, it will show the top 10 songs. Given a list of songs (EX dif only), it will sort them based off efficiency. Assumes SL5 and 100% Perfects. I recommend using Bestdori for finer tuning.\n\nExamples\n\n.songmetanofever\n.smnf\n.metanf\n.songmetanofever unite guren jumpin')
    async def songmetanf(self, ctx, *songs):
        if songs:
            output = await getSongMetaOutput(False, list(songs))
        else:
            output = await getSongMetaOutput(False)
        await ctx.send(output)

    @commands.command(name='leaderboards',
                      aliases=['lb','lbs'],
                      help='Shows the player leaderboards from Bestdori\n\nSupports the EN/JP/TW/CN/KR Server.\nA valid type of leaderboard must be entered, these valid entries are: highscores/hs, fullcombo/fc, ranks/rank, and cleared\n\nExamples:\n\n.lb\n.lb en ranks\n.lb jp highscores 50')
    async def playerleaderboards(self, ctx, server: str = 'en', type: str = 'highscores', entries: int = 20):
        Output = await GetLeaderboardsOutput(server, type, entries)
        await ctx.send(Output)

        
    @commands.command(name='cards',
                      aliases=['card'],
                      description="Provides bestdori link of the card being searched",
                      brief="Bestdori card link",
                      help="Enter the title/name or ID(s) of the card you want to search\n\nExamples:\n.card crystal\n.card 100\n.card 100 200 300")
    async def cards(self, ctx, *args):

        output = []
        cardAPI = requests.get('https://bestdori.com/api/cards/all.0.json').json()
        AllCardsAPI = requests.get('https://bestdori.com/api/cards/all.3.json').json()
        if all(x.isnumeric() for x in args):
            for x in args:
                if(x not in cardAPI):
                    output.append('Card with ID `%s` not found' %(x))
                else:
                    output.append('https://bestdori.com/info/cards/%s' %(x))    
        else:
            from langdetect import detect
            CardTitle = args[0]
            for x in args:
                if x == CardTitle:
                    continue
                CardTitle += " %s" % x
            if detect(CardTitle) == 'ja':
                KeyValue = 0
            else:
                KeyValue = 1
            for x in AllCardsAPI:
                if AllCardsAPI[x]['prefix'][KeyValue]: # Not all cards have an english entry
                    if CardTitle.lower() in AllCardsAPI[x]['prefix'][KeyValue].lower():
                        output.append('https://bestdori.com/info/cards/%s' %(x))
                            
        await ctx.send('\n'.join(output))

    @songinfo.error
    async def songinfo_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'songName':
                ctx.send("Song name not found, please provide the song name EXACTLY as it appears in game e.g. B.O.F not BOF, b.o.f, etc.")

    @starsused.error
    async def starsused_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
    @epgain.error
    async def epgain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")


def setup(bot):
    bot.add_cog(Game(bot))