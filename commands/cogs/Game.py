import os

from commands.apiFunctions import GetSongAPI
from tabulate import tabulate
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from operator import itemgetter
from time import strftime
from time import gmtime
from commands.apiFunctions import GetBestdoriAllCharactersAPI, GetBestdoriAllEventsAPI, GetBestdoriBannersAPI, GetBestdoriEventArchivesAPI, GetBestdoriAllGachasAPI, GetBestdoriGachaAPI, GetBestdoriCardAPI, GetSongMetaAPI, GetBestdoriCharasAPI
from commands.cogs.Cards import parseCards, generateImage, Palette, filterArguments, findCardFromArguments, Card
from commands.formatting.GameCommands import GetStarsUsedOutput, GetEPGainOutput, characterOutput, GetSongInfo, GetSongMetaOutput, GetLeaderboardsOutput
from commands.formatting.TimeCommands import GetCurrentTime
import discord
import time
import requests
import math

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='level',
                    help='Given a current level, xp earned per song, and the amount of songs played, the end level will be provided')
    async def level(self, ctx, CurrentLevel: int, XPPerSong: int, SongsPlayed: int):
        from commands.formatting.GameCommands import GetLevelOutput
        NewLevel = await GetLevelOutput(CurrentLevel, XPPerSong, SongsPlayed)
        await ctx.send('New Level: %s' %(str(NewLevel)))


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
                    if event[0].isnumeric():
                        EventName = await GetEventName(server, event[0])
                        EventID = event[0]
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
                
                bannerAPI = await GetBestdoriBannersAPI(int(EventID))
                bannerName = bannerAPI['assetBundleName']
                eventUrl = 'https://bestdori.com/info/events/' + str(EventID)
                thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)
                embed=discord.Embed(title=EventName, url=eventUrl, color=embedColor)
                embed.set_thumbnail(url=thumbnail)
                embed.add_field(name='Attribute', value=str(attribute).capitalize(), inline=True)
                embed.add_field(name='Event Type', value=str(eventType).capitalize(), inline=True)
                if(currentTime > int(endTime)):
                    archiveAPI = await GetBestdoriEventArchivesAPI()
                    if str(EventID) in archiveAPI.keys():
                        cutoffs = []
                        if(server == 'en'):
                            CutoffKey = 1
                        elif(server == 'jp'):
                            CutoffKey = 0
                        elif(server == 'tw'):
                            CutoffKey = 2
                        elif(server == 'cn'):
                            CutoffKey = 3
                        if archiveAPI[str(EventID)]['cutoff'][CutoffKey]:
                            cutoffs = (archiveAPI[str(EventID)]['cutoff'][CutoffKey]).items()
                            embed.add_field(name='Cutoffs', value='\n'.join("{}: {}".format(k, "{:,}".format(v)) for k, v in cutoffs), inline=True)
                embed.add_field(name='Members', value='\n'.join(members), inline=False)
                embed.add_field(name='Start' , value=beginsString, inline=True)
                embed.add_field(name='End', value=endsString, inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Please enter a valid server (i.e. en, jp, tw, cn)")
        except:
            await ctx.send(f"No event information found for event `{EventID}` and server `{server}`. If using hiragana, try kana or vice versa (e.g. きみが doesn't work, but キミが does).")

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
            output = await GetSongMetaOutput(True, songs)
        else:
            output = await GetSongMetaOutput(True)
        await ctx.send(output)

    @commands.command(name='songmetanofever',
                      aliases=['smnf','metanf'],
                      brief='Shows song meta info (no fever)',
                      help='Shows song meta info (no fever). By default, it will show the top 10 songs. Given a list of songs (EX dif only), it will sort them based off efficiency. Assumes SL5 and 100% Perfects. I recommend using Bestdori for finer tuning.\n\nExamples\n\n.songmetanofever\n.smnf\n.metanf\n.songmetanofever unite guren jumpin')
    async def songmetanf(self, ctx, *songs):
        if songs:
            output = await GetSongMetaOutput(False, list(songs))
        else:
            output = await GetSongMetaOutput(False)
        await ctx.send(output)

    @commands.command(name='leaderboards',
                      aliases=['lb','lbs'],
                      help='Shows the player leaderboards from Bestdori\n\nSupports the EN/JP/TW/CN/KR Server.\nA valid type of leaderboard must be entered, these valid entries are: highscores/hs, fullcombo/fc, ranks/rank, and cleared\n\nExamples:\n\n.lb\n.lb en ranks\n.lb jp highscores 50')
    async def playerleaderboards(self, ctx, server: str = 'en', type: str = 'highscores', entries: int = 20):
        Output = await GetLeaderboardsOutput(server, type, entries)
        await ctx.send(Output)

    @commands.command(name='card',
                      aliases=['cards', 'ci', 'cardinfo'],
                      description="Provides embedded image of card with specified filters",
                      brief="Detailed card image",
                      help="Enter the character with optional filters to see card information\n\nExamples:\n.card kokoro 2 - Second Kokoro SSR\n.card lisa df - Lisa Dreamfes card\n.card moca last ssr - Last released SSR of Moca\n.card hina last sr happy - Last released happy SR of Hina\n.card title maritime decective - Lookup card with title \"Maritime Detective\"")
    async def card(self, ctx: discord.abc.Messageable, *args):
        resultFilteredArguments = filterArguments(*args)
        if resultFilteredArguments.failure:
            return await ctx.send(resultFilteredArguments.failure)
        cardsApi = requests.get('https://bestdori.com/api/cards/all.5.json').json()
        skillsApi = requests.get('https://bestdori.com/api/skills/all.5.json').json()
        cards = parseCards(cardsApi, skillsApi)
        resultCard = findCardFromArguments(cards, resultFilteredArguments.success)
        if resultCard.failure:
            return await ctx.send(resultCard.failure)
        card: Card = resultCard.success
        palette = Palette(card.attribute)
        imagePath = generateImage(card, palette)
        channel: discord.TextChannel = self.bot.get_channel(523339468229312555)  # Change this channel to the channel you want the bot to send images to so it can grab a URL for the embed
        fileSend: discord.Message = await channel.send(file=discord.File(imagePath))
        embed = discord.Embed(colour=palette.primaryInt)
        embed.set_image(url=fileSend.attachments[0].url)
        os.remove(imagePath)
        await ctx.send(embed=embed)

    @songinfo.error
    async def songinfo_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'songName':
                ctx.send("Song name not found, please provide the song name EXACTLY as it appears in game e.g. B.O.F not BOF, b.o.f, etc.")

    @starsused.error
    async def starsused_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help starsused`! Required arguments are enclosed in < >")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help starsused`")
    @epgain.error
    async def epgain_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help epgain`! Required arguments are enclosed in < >")


def setup(bot):
    bot.add_cog(Game(bot))