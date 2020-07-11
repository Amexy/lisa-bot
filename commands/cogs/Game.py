import os
from commands.apiFunctions import GetSongAPI
from tabulate import tabulate
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from operator import itemgetter
from time import strftime
from time import gmtime
from commands.apiFunctions import GetBestdoriAllCharactersAPI, GetBestdoriAllEventsAPI, GetBestdoriBannersAPI, GetBestdoriEventArchivesAPI, GetBestdoriAllGachasAPI, GetBestdoriGachaAPI, GetBestdoriCardAPI, GetSongMetaAPI, GetBestdoriCharasAPI, GetServerAPIKey, GetBestdoriAllCardsAPI
from commands.cogs.Cards import parseCards, generateImage, Palette, filterArguments, findCardFromArguments, Card
from commands.formatting.GameCommands import GetStarsUsedOutput, GetEPGainOutput, characterOutput, GetSongInfo, GetSongMetaOutput, GetLeaderboardsOutput
from commands.formatting.TimeCommands import GetCurrentTime
import discord, shutil, time, requests, math, asyncio


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='updatecardicons',
                      aliases=['uci'],
                      hidden=True,
                      enabled=False)
    async def uci(self, ctx):
        from commands.apiFunctions import GetBestdoriAllCardsAPI, GetBestdoriAllCharactersAPI        
        CardAPI = await GetBestdoriAllCardsAPI()
        from PIL import Image
        from PIL.ImageDraw import Draw
        from PIL.ImageFont import truetype
        from io import BytesIO
        from os import path
        for x in CardAPI:
            try:
                im = Image.new("RGBA", (180, 180))
                Folder = str(math.floor(int(x) / 50)).zfill(2)
                ResourceSetName = CardAPI[x]['resourceSetName']
                IconsPath = f"img/icons/base_icons/{x}.png"
                Rarity = str(CardAPI[x]['rarity']) 
                 
                if int(Rarity) > 0:
                    if not path.exists(IconsPath):              
                        # These urls will need changed around depending if it's a jp/cn limited card and for some reason the card000 part may need changed to card00
                        if CardAPI[x]['type'] == 'others':
                            IconURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_normal.png'    
                        elif CardAPI[x]['type'] == 'campaign': 
                            IconURL = f'https://bestdori.com/assets/en/thumb/chara/card00{Folder}_rip/{ResourceSetName}_normal.png'    
                        else:
                            IconURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_normal.png'    
                        image = requests.get(IconURL)
                        image = Image.open(BytesIO(image.content))
                        im.paste(image)
                        im.save(IconsPath)
            except:
                print(f"Failed adding card with ID {x}")
                pass
    
    @commands.command(name='lookup',
                      aliases=['find','search','lu'],
                      description='Searches a player on the specified server by ID',
                      help='Currently only supports EN. JP functionality coming at a later date.\n\n.lookup en 1540')
    async def lookup(self, ctx, server: str, id: int):
        try:
            from protodefs.ranks import profileinfo
            from startup.login import enICEObject, jpICEObject
            from discord import File
            from commands.formatting.GameCommands import GenerateBandandTitlesImage
            from commands.formatting.T10Commands import stringCheck
            if server == 'en':
                ice = enICEObject
            else:
                ice = jpICEObject

            info = await profileinfo(ice, server, id)
            if info.name == '':
                info.name = 'No Name Found'
            info.name = stringCheck(info.name)
            embed=discord.Embed(title=f'{info.name} [{id}]',color=discord.Color.blue())
            embed.add_field(name='Description', value=info.description, inline=True)
            embed.add_field(name='Level', value=info.rank, inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)

            if info.center_info.card_id == 0:
                info.center_info.card_id = 1
            if info.center_info.trained == 'after_training':
                ProfilePicture = f'{info.center_info.card_id}_trained.png'
            else:
                ProfilePicture = f'{info.center_info.card_id}.png'
                
            if len(info.cleared_songs.song) > 0:
                embed.add_field(name='EX Cleared / FC', value=f'{info.cleared_songs.song._values[2].amount} / {info.fced_songs.song._values[2].amount}', inline=True)
                embed.add_field(name='SP Cleared / FC', value=f'{info.cleared_songs.song._values[0].amount} / {info.fced_songs.song._values[0].amount}', inline=True)



            TitlesInfo = []
            if len(info.equipped_titles.title._values) == 2:
                TitlesInfo.append(info.equipped_titles.title._values[0].titleinfo.title_id)
                TitlesInfo.append(info.equipped_titles.title._values[1].titleinfo.title_id)
            else:
                TitlesInfo.append(info.equipped_titles.title._values[0].titleinfo.title_id)
                
            if len(info.hsr.val1.val) > 0:
                # I know there's a better way to do this, but whatever
                hsr = 0
                hsr += info.hsr.val1.val._values[0].rating
                hsr += info.hsr.val1.val._values[1].rating
                hsr += info.hsr.val1.val._values[2].rating
                hsr += info.hsr.val2.val._values[0].rating
                hsr += info.hsr.val2.val._values[1].rating
                hsr += info.hsr.val2.val._values[2].rating
                hsr += info.hsr.val3.val._values[0].rating
                hsr += info.hsr.val3.val._values[1].rating
                hsr += info.hsr.val3.val._values[2].rating
                hsr += info.hsr.val4.val._values[0].rating
                hsr += info.hsr.val4.val._values[1].rating
                hsr += info.hsr.val4.val._values[2].rating
                hsr += info.hsr.val5.val._values[0].rating
                hsr += info.hsr.val5.val._values[1].rating
                hsr += info.hsr.val5.val._values[2].rating
                hsr += info.hsr.val6.val._values[0].rating
                hsr += info.hsr.val6.val._values[1].rating
                #hsr += info.hsr.val6.val._values[2].rating
                embed.add_field(name='High Score Rating', value=hsr, inline=True)
            BandMembers = []
            # Since you can't iterate over it, I think
            BandMembers.append(info.current_band.card4)
            BandMembers.append(info.current_band.card2)
            BandMembers.append(info.current_band.card1)
            BandMembers.append(info.current_band.card3)
            BandMembers.append(info.current_band.card5)
            BandFileName = await GenerateBandandTitlesImage(BandMembers,TitlesInfo, server)
            BandImageFile = discord.File(BandFileName[1], filename=BandFileName[0])
            icon = discord.File(f"img/icons/base_icons/{ProfilePicture}", filename=f'{ProfilePicture}')
            embed.set_thumbnail(url=f"attachment://{ProfilePicture}")
            embed.set_image(url=f"attachment://{BandFileName[0]}")

            await ctx.send(files=[icon,BandImageFile],embed=embed)
        except:
            await ctx.send('Failed looking up that player. If you believe this to be a mistake, please use the notify command to let Josh know')
        
    @commands.command(name='level',
                    description='Given a current level, xp earned per song, and the amount of songs played, the end level will be provided',
                    help='.level 100 500 10')
    async def level(self, ctx, CurrentLevel: int, XPPerSong: int, SongsPlayed: int):
        from commands.formatting.GameCommands import GetLevelOutput
        NewLevel = await GetLevelOutput(CurrentLevel, XPPerSong, SongsPlayed)
        await ctx.send('New Level: %s' %(str(NewLevel)))

    @commands.command(name='gacha',
                      description="Gives info on the current gachas. Doesn't show the gachas that are always available (new player, 3+ ticket, etc)",
                      help=".gacha en\n.gacha (defaults to en)")
    async def gacha(self, ctx, server: str = 'en'):
        from PIL import Image
        from PIL.ImageDraw import Draw
        from PIL.ImageFont import truetype
        from commands.apiFunctions import GetServerAPIKey
        api = await GetBestdoriAllGachasAPI()
        gachas = []
        gachasEnd = []
        cardDetails = []
        CardIds = []
        CardCharaNames = []
        currentTime = await GetCurrentTime()
        ServerKey = await GetServerAPIKey(server)
        for x in list(api):
            if api[str(x)]['gachaName'][ServerKey] and api[str(x)]['closedAt'][ServerKey] and api[str(x)]['publishedAt'][ServerKey]:
                closedAt = int(api[str(x)]['closedAt'][ServerKey])
                startAt = int(api[str(x)]['publishedAt'][ServerKey])
                gachaName = api[str(x)]['gachaName'][ServerKey]
                if 'Beginners' not in gachaName and '3+' not in gachaName and 'Head Start' not in gachaName:
                    if(closedAt > currentTime and currentTime > startAt):
                        gachaAPI = await GetBestdoriGachaAPI(x)
                        if gachaAPI['details'][0]:
                            for y in list(gachaAPI['details'][0]):
                                if(gachaAPI['details'][0][str(y)]['weight'] == 5000):
                                    CardApi = await GetBestdoriCardAPI(y)
                                    CardIds.append(y)
                                    cardChara = CardApi['characterId']
                                    cardAttr = CardApi['attribute']
                                    cardType = CardApi['type']
                                    charaApi = await GetBestdoriCharasAPI(cardChara)
                                    charaName = charaApi['characterName'][1] # icons are stored in their english name
                                    cardInfo = cardType.capitalize() + " " + cardAttr.capitalize() + " " + charaName 
                                    CardCharaNames.append(charaName.split()[0])
                                    cardDetails.append(cardInfo)
                                    cardDetails.append(f'https://bestdori.com/info/cards/{y}')
                        gachas.append(gachaName)
                        gachasEnd.append(time.strftime("%d %b %Y", time.localtime(int(closedAt / 1000))))        
        IconPaths = []
        for chara, id in zip(CardCharaNames, CardIds):
            IconPaths.append(f"img/icons/{chara.lower()}/4/{id}.png")
        images = [Image.open(x) for x in IconPaths]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths) 
        max_height = max(heights)
        new_im = Image.new('RGBA', (int(total_width), max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        from discord import File
        import uuid
        FileName = str(uuid.uuid4()) + '.png'
        SavedFile = "img/imgTmp/" + FileName
        new_im.save(SavedFile)
        DiscordFileObject = File(SavedFile, filename=FileName)
        embed=discord.Embed()
        embed.add_field(name='Gacha', value='\n'.join(gachas), inline=True)
        embed.add_field(name='End', value='\n'.join(gachasEnd), inline=True)
        embed.add_field(name='Cards', value='\n'.join(cardDetails), inline=False)
        embed.set_image(url=f"attachment://{FileName}")
        await ctx.send(file=DiscordFileObject, embed=embed)
        os.remove(SavedFile)


    @commands.command(name='character',
                      aliases=['chara','c'],
                      description='Posts character info',
                      help='.character lisa\n.c kasumi')
    async def characterinfo(self, ctx, character: str):
        try:
            output = await characterOutput(character)
            await ctx.send(embed=output)
        except:
            await ctx.send("Couldn't find the character entered, possible mispell?")

    @commands.command(name='starsused',
                      aliases=['su'],
                      description="Provides star usage when aiming for a certain amount of EP. Challenge live calculations aren't incorporated yet. I recommended using Bestdori's event calculator",
                      help=".starsused 9750 100 0 2000000 3 en\n.starsused 9750 100 0 2000000 3 jp\n.starsused 9750 100 0 2000000 3 168\n.su 9750 100 0 2000000 3",
                      enabled=False)
    async def starsused(self, ctx, epPerSong: int, begRank: int, begEP: int, targetEP: int, flamesUsed: int, *ServerOrHoursLeft):
        starsUsedTable = await GetStarsUsedOutput(epPerSong, begRank, begEP, targetEP, flamesUsed, *ServerOrHoursLeft)
        await ctx.send(starsUsedTable)

    @commands.command(name='epgain',
                      description="Provides EP gain given user-provided inputs",
                      help="BPPercent should be between 1 and 150 and in intervals of 10 e.g. 10, 20, 30\n\nNormal Event = 1\nLive Trial = 2\nChallenge = 3\nBand Battle* = 4\n*For Band Battles, specify placement between 1-5.\n\n.epgain 1500000 7500000 150 3 1\n.epgain 1000000 6000000 130 2 4 5",
                      enabled=False)
    async def epgain(self, ctx, yourScore: int, multiScore: int, bpPercent: int, flamesUsed: int, eventType: int, bbPlace: int = 0):
        ep = GetEPGainOutput(yourScore, multiScore, bpPercent, flamesUsed, eventType, bbPlace)
        await ctx.send("EP Gain: " + str(math.floor(ep)))

    @commands.command(name='event',
                      description='Posts event info',
                      help='event\n.event jp\n.event en 12\n.event en Lisa\n.event jp 一閃')
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
                    beginsString = datetime.fromtimestamp(beginsString).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' UTC'
                    endsString = datetime.fromtimestamp(endsString).strftime("%Y-%m-%d %H:%M:%S %Z%z") + ' UTC'

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
                embed=discord.Embed(title=f"{EventName} [{EventID}]", url=eventUrl, color=embedColor)
                embed.set_thumbnail(url=thumbnail)
                embed.add_field(name='Attribute', value=str(attribute).capitalize(), inline=True)
                embed.add_field(name='Event Type', value=str(eventType).capitalize(), inline=True)
                if(currentTime > int(endTime)):
                    archiveAPI = await GetBestdoriEventArchivesAPI()
                    if str(EventID) in archiveAPI.keys():
                        cutoffs = []
                        CutoffKey = await GetServerAPIKey(server)
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
                      help='If there are special characters in the song name, provide the song name EXACTLY as it appears in game e.g. B.O.F not BOF, b.o.f, etc.\n\n.songinfo Sunkissed')
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
                      description='Shows song meta info (fever). By default, it will show the top 20 songs. Given a list of songs (EX and SP dif only), it will sort them based off efficiency. Assumes SL5 and 100% Perfects. I recommend using Bestdori for finer tuning',
                      help='.songmeta\n.sm\n.meta\n.songmeta unite guren jumpin')
    async def songmeta(self, ctx, *songs):
        if songs:
            output = await GetSongMetaOutput(True, songs)
        else:
            output = await GetSongMetaOutput(True)
        await ctx.send(output)

    @commands.command(name='songmetanofever',
                      aliases=['smnf','metanf'],
                      description='Shows song meta info (no fever). By default, it will show the top 20 songs. Given a list of songs (EX and SP dif only), it will sort them based off efficiency. Assumes SL5 and 100% Perfects. I recommend using Bestdori for finer tuning',
                      help='.songmeta\n.sm\n.meta\n.songmeta unite guren jumpin')
    async def songmetanf(self, ctx, *songs):
        if songs:
            output = await GetSongMetaOutput(False, list(songs))
        else:
            output = await GetSongMetaOutput(False)
        await ctx.send(output)

    @commands.command(name='leaderboards',
                      aliases=['lb','lbs'],
                      description='Shows the player leaderboards from Bestdori\n\nSupports the EN/JP/TW/CN/KR Server.\n',
                      help='A valid type of leaderboard must be entered, these valid entries are: highscores/hs, fullcombo/fc, ranks/rank, and cleared\n\n.lb\n.lb en ranks\n.lb jp highscores 50')
    async def playerleaderboards(self, ctx, server: str = 'en', type: str = 'highscores', entries: int = 20):
        Output = await GetLeaderboardsOutput(server, type, entries)
        await ctx.send(Output)

    @commands.command(name='card',
                      aliases=['cards', 'ci', 'cardinfo'],
                      description="Provides embedded image of card with specified filters",
                      help="There are several filters one can use to search. Rarity goes bEnter the character with optional filters to see card information\n\n.card lisa - Most recent Lisa 4* Card\n.card lisa df - Lisa Dreamfes Card\n.card lisa last - Last released Lisa 4*\n.card lisa last sr happy - Last released happy 3* Lisa\n.card title maritime detective - Lookup card with title \"Maritime Detective\"")
    async def card(self, ctx: discord.abc.Messageable, *args):
        from discord import File
        if not args:
            await ctx.send('No filters were entered. For help please use `.help card`')
        else:
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
            enRelease = card.enRelease
            jpRelase = card.jpRelease
            DiscordFileObject = File(imagePath[0],filename=imagePath[1])
            embed = discord.Embed(title=f'{card.cardName}',color=discord.Color.blue(),url=f'https://bestdori.com/info/cards/{card.cardId}')
            embed.add_field(name='EN Release',value=enRelease,inline=True)
            embed.add_field(name='\u200b',value='\u200b',inline=True)
            embed.add_field(name='\u200b',value='\u200b',inline=True)
            embed.add_field(name='JP Release',value=jpRelase,inline=True)
            embed.add_field(name='\u200b',value='\u200b',inline=True)
            embed.add_field(name='\u200b',value='\u200b',inline=True)
            embed.set_image(url=f'attachment://{imagePath[1]}')
            await ctx.send(embed=embed,file=DiscordFileObject)

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
