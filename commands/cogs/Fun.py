from discord.ext import commands
from typing import Union
import discord, shutil, time, requests, math, asyncio, os, json
from pixivpy3 import *

class Fun(commands.Cog):
    def __init__(self, bot):
        with open("config.json") as file:
            config_json = json.load(file)
            pixiv_username = config_json["pixiv_username"]
            pixiv_pw = config_json["pixiv_pw"]

        self.bot = bot
        self.AllCards = self.GetCards()
        self.AllTwoStarCards = self.AllCards[0]
        self.AllThreeStarCards = self.AllCards[1]
        self.AllFourStarCards = self.AllCards[2]
        self.api = AppPixivAPI()
        self.api.login(pixiv_username,pixiv_pw)
        # Uncomment this to load new images
        # asyncio.run(self.GetImages())
        
    async def GetImages(self):
        import json
        from commands.apiFunctions import GetBestdoriAllCharasAPI
        api = self.api
        r = await GetBestdoriAllCharasAPI()
        AllCharacters = []
        for x in r:
            charalist = r[x]['characterName']
            if charalist[1]:
                name = "".join(charalist[0].split())
                AllCharacters.append(name)
        #AllCharacters = AllCharacters[0:25] # Because the API has a lot more than the 25 main characters
        for chara in AllCharacters:
            AllPics = {}
            
            print(f'Grabbing pictures for {chara}')
            Pics = []
            pics = api.search_illust(chara)
            for pic in pics.illusts:
                if pic['total_bookmarks'] > 100 and pic['sanity_level'] < 3 and pic['page_count'] == 1 and pic['type'] == 'illust':
                    Pics.append(pic)
            ContinueSearching = True
            while ContinueSearching:
                next_page = api.parse_qs(pics.next_url)
                pics = api.search_illust(**next_page)
                if 'illusts' in pics.keys():
                    for pic in pics.illusts:
                        if pic['total_bookmarks'] > 100 and pic['sanity_level'] < 3 and pic['page_count'] == 1 and pic['type'] == 'illust':
                            Pics.append(pic)
                    if pics.next_url:
                        ContinueSearching = True
                    else:
                        ContinueSearching = False
                else:
                    ContinueSearching = False
            data = {chara: {
            "pics" : Pics}}
            AllPics.update(data)
            newfile = json.dumps(AllPics)
            f = open(f"{chara}.json","a")
            f.write(newfile)
            f.close()
            await asyncio.sleep(300)
        return AllPics

    def GetCards(self):
        AllFourStarCards = []
        AllThreeStarCards = []
        AllTwoStarCards = []

        for folder in os.listdir("icons/"):
            if folder != '.DS_Store':
                    for subfolder in os.listdir(f"icons/{folder}"):
                        if subfolder == '2':
                            for file in os.listdir(f"icons/{folder}/{subfolder}"):
                                AllTwoStarCards.append(f"icons/{folder}/{subfolder}/" + file)
                        elif subfolder == '3':
                            for file in os.listdir(f"icons/{folder}/{subfolder}"):
                                AllThreeStarCards.append(f"icons/{folder}/{subfolder}/" + file)
                        elif subfolder == '4':
                            for file in os.listdir(f"icons/{folder}/{subfolder}"):
                                AllFourStarCards.append(f"icons/{folder}/{subfolder}/" + file)
                        else:
                            pass

        return AllTwoStarCards, AllThreeStarCards, AllFourStarCards

    def GetRollStats(self, user, *Chara):
        import json
        try:
            if Chara:
                Chara = Chara[0] 
                FileName = f'databases/rolls/{Chara}.json'
            else:
                FileName = 'databases/rolls/rolls.json'
            with open(FileName) as file:
                api = json.load(file)
            user = self.bot.get_user(user)
            Rolled = []
            # Character specific roll databases store the amount of cards rolled for that character, not how many rolls have been done total, hence this logic below
            TotalRolls = api[str(user.id)]['TotalRolls'] * 10 if not Chara else api[str(user.id)]['TotalRolls']
            Rolled.append(TotalRolls)
            Rolled.append(api[str(user.id)]['TwoStars'])
            Rolled.append(api[str(user.id)]['ThreeStars'])
            Rolled.append(api[str(user.id)]['FourStars'])
            Rolled.append(str(round(((Rolled[3] / Rolled[0]) * 100), 2)) + '%')
            Rolled.append(user.avatar_url.BASE + user.avatar_url._url)
            return Rolled
        except KeyError:
            return 'No stats found for that user'
        except:
            return 'Unknown error. If this keeps happening please use the `notify` command to let Josh know'

    def UpdateCharaRollsJSON(self, UserIDOrOverall, Name, Chara, CardType):
        import json
        FileName = f'databases/rolls/{Chara}.json'
        try:
            with open(FileName) as file:
                api = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            # Create the file and add an empty dict to it so we can load the json file
            with open(FileName, 'a+') as file:
                data = {}
                json.dump(data, file, indent=2)
            
            # Load the newly created file
            with open(FileName) as file:
                api = json.load(file)
        if str(UserIDOrOverall) in api:
            if CardType == '2':
                Key = 'TwoStars'
            elif CardType == '3':
                Key = 'ThreeStars'
            elif CardType == '4':
                Key = 'FourStars'
            api[str(UserIDOrOverall)][Key] += 1  
            api[str(UserIDOrOverall)]['TotalRolls'] += 1

            if 'Name' not in api[str(UserIDOrOverall)]:
                api[str(UserIDOrOverall)].update({'Name' : Name})
            with open(FileName, 'w') as f:
                json.dump(api, f)
        # This adds a new key to the dictionary
        else:
            TwoStars = 0
            ThreeStars = 0
            FourStars = 0
            if CardType == '2':
                TwoStars += 1
            elif CardType == '3':
                ThreeStars += 1
            elif CardType == '4':
                FourStars += 1
  
            data = {UserIDOrOverall: {
                            "TotalRolls" : 1,
                            "TwoStars" : TwoStars,
                            "ThreeStars" : ThreeStars,
                            "FourStars" : FourStars,
                            "Name" : Name
                            }
                    }
            with open(FileName, 'w') as f:
                api.update(data)
                json.dump(api, f)

    def UpdateRollsJSON(self, UserIDOrOverall, Name, TwoStars, ThreeStars, FourStars):
        import json
        FileName = 'databases/rolls/rolls.json'
        try:
            with open(FileName) as file:
                api = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            # Create the file and add an empty dict to it so we can load the json file
            with open(FileName, 'a+') as file:
                data = {}
                json.dump(data, file, indent=2)
            
            # Load the newly created file
            with open(FileName) as file:
                api = json.load(file)

        # Check if there's an entry for the EventID in the json file 
        if str(UserIDOrOverall) in api:
            api[str(UserIDOrOverall)]['TwoStars'] += TwoStars        
            api[str(UserIDOrOverall)]['ThreeStars'] += ThreeStars
            api[str(UserIDOrOverall)]['FourStars'] += FourStars
            api[str(UserIDOrOverall)]['TotalRolls'] += 1
            if 'Name' not in api[str(UserIDOrOverall)]:
                api[str(UserIDOrOverall)].update({'Name' : Name})
            with open(FileName, 'w') as f:
                json.dump(api, f)
        # This adds a new key to the dictionary
        else:
            data = {UserIDOrOverall: {
                            "TotalRolls" : 1,
                            "TwoStars" : TwoStars,
                            "ThreeStars" : ThreeStars,
                            "FourStars" : FourStars,
                            "Name" : Name
                            }
                    }
            with open(FileName, 'w') as f:
                api.update(data)
                json.dump(api, f)

    
    @commands.command(name='updatecards',
                      hidden=True,
                      enabled=True)
    async def GetIcons(self, ctx):
        from commands.apiFunctions import GetBestdoriAllCardsAPI, GetBestdoriAllCharactersAPI        
        from PIL import Image
        from PIL.ImageDraw import Draw
        from PIL.ImageFont import truetype
        from io import BytesIO
        from os import path
        CardAPI = await GetBestdoriAllCardsAPI()
        CharaAPI = await GetBestdoriAllCharactersAPI()
        for x in CardAPI:
            try:
                im = Image.new("RGBA", (180, 180))
                Folder = str(math.floor(int(x) / 50)).zfill(2)
                ResourceSetName = CardAPI[x]['resourceSetName']
                Rarity = str(CardAPI[x]['rarity'])  
                Attribute = str(CardAPI[x]['attribute'])      
                CharacterID = str(CardAPI[x]['characterId'])
                BandID = CharaAPI[CharacterID]['bandId']
                CharaName = CharaAPI[CharacterID]['characterName'][1]
                SplitList = CharaName.split(' ', 1)
                CharaName = SplitList[0].lower()
                IconsPath = f"icons/full_icons/{x}.png"
                AllowedTypes = ['limited','permanent','initial','event']
                if int(Rarity) > 2:
                    if not path.exists(IconsPath):
                        if CardAPI[x]['type'] in AllowedTypes:
                            if CardAPI[x]['type'] == 'others':
                                    IconURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_after_training.png'    
                            elif CardAPI[x]['type'] == 'campaign': 
                                IconURL = f'https://bestdori.com/assets/cn/thumb/chara/card000{Folder}_rip/{ResourceSetName}_normal.png'    
                            else:
                                IconURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_normal.png'    
                            image = requests.get(IconURL)
                            image = Image.open(BytesIO(image.content))
                            im.paste(image)
                            
                            if Rarity == '1':
                                rarityPng = "img/2star.png"
                                starPng = "img/star1.png"
                            elif Rarity == '2':
                                rarityPng = "img/2star.png"
                                starPng = "img/star2.png"
                            elif Rarity == '3':
                                rarityPng = "img/3star.png"
                                starPng = "img/star3.png"
                            else:
                                rarityPng = "img/4star.png"
                                starPng = "img/star4.png"
                            rarityBg = Image.open(rarityPng)
                            starBg = Image.open(starPng)
                            if Rarity == '1':
                                im.paste(starBg, (5,20), mask=starBg)
                            else:
                                im.paste(starBg, (5,50), mask=starBg)
                            im.paste(rarityBg, mask=rarityBg)
                        
                            if Attribute == 'powerful':
                                attrPng = "img/power2.png"
                            elif Attribute == 'cool':
                                attrPng = "img/cool2.png"
                            elif Attribute == 'pure':
                                attrPng = "img/pure2.png"
                            else:
                                attrPng = "img/happy2.png"
                            attrBg = Image.open(attrPng)
                            im.paste(attrBg, (132, 2), mask=attrBg)
                            
                            bandPng = f"img/band_{BandID}.png"
                            bandBg = Image.open(bandPng)
                            im.paste(bandBg, (1, 2), mask=bandBg)

                            im.save(IconsPath)
            except:
                print(f"Failed adding card with ID {x}")
                pass


    @commands.command(name='rollstats',
                     aliases=['rs'],
                     description='Returns the stats from the roll command for a particular user',
                     help='.rollstats (this defaults to the user running the command)\n.rollstats @Lisa#4081\n.rollstats Lisa (this searches all the users with Lisa as their Discord name and returns the first user found)\n.rs Lisa Rinko (returns the stats for user Lisa and character Rinko)\n.rs total (returns ALL stats accumulated so far)')
    async def rollstats(self, ctx, user: Union[discord.Member, str, int]=None, *Chara):
        import json
        if user:
            if not isinstance(user, discord.Member):
                if user.isnumeric():
                    id = user
                    user = self.bot.get_user(523337807847227402)
                    Title = "Roll Stats"

                elif user == 'total':
                    user = self.bot.get_user(523337807847227402)   
                    id = user.id
                    Title = "Total Roll Stats" if not Chara else f"{Chara[0].capitalize()} Total Roll Stats"
            else:
                id = user.id
                Title = f"{user.display_name}#{user.discriminator}'s Roll Stats" if not Chara else f"{user.display_name}#{user.discriminator}'s {Chara[0].capitalize()} Roll Stats"

        elif user is None:
            user = self.bot.get_user(ctx.message.author.id)   
            id = ctx.message.author.id
            Title = f"{user.display_name}#{user.discriminator}'s Roll Stats"
     
        try:
            if Chara:
                RolledStats = self.GetRollStats(ctx.message.author.id, Chara[0])
            else:
                RolledStats = self.GetRollStats(id)
                
            TotalRolled = RolledStats[0]
            TwoStarsRolled = RolledStats[1]
            ThreeStarsRolled = RolledStats[2]
            FourStarsRolled = RolledStats[3]
            FourStarRate = RolledStats[4]
            Icon = RolledStats[5]
            embed=discord.Embed(title=Title,color=discord.Color.blue())
            embed.set_thumbnail(url=Icon)
            embed.add_field(name='Total Cards Rolled',value="{:,}".format(TotalRolled),inline=True)
            embed.add_field(name='4* Rate',value=FourStarRate,inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            embed.add_field(name='2* Rolled',value="{:,}".format(TwoStarsRolled),inline=True)
            embed.add_field(name='3* Rolled',value="{:,}".format(ThreeStarsRolled),inline=True)
            embed.add_field(name='4* Rolled',value="{:,}".format(FourStarsRolled),inline=True)
            await ctx.send(embed=embed)
        except discord.errors.HTTPException:
            await ctx.send('No stats found for that user and character')
        except KeyError:
            await ctx.send('No stats found for that user')
        except:
            await ctx.send('Unknown error. If this keeps happening please use the `notify` command to let Josh know')
        
    @commands.command(name='roll',
                      description='Simulates a 10 roll using the default rates and all the permanent/limited cards that have been released in JP so far. Event cards are not included. Add df and/or the bands/characters names to the input to simulate increased rates/only roll those cards.',
                      help='For bands, the values below are valid, if an invalid value is entered, the command will fail\n\nRoselia\nAfterglow\nPopipa\nPasupare\nHHW\nMorfonica\n\n.roll\n.roll df\n.roll lisa\n.roll df yukina lisa\n.roll roselia\n.roll roselia popipa')
    async def gacharoll(self, ctx, *args):
        try:
            import re
            import random
            from PIL import Image
            from PIL.ImageDraw import Draw
            from PIL.ImageFont import truetype
            Rates = [.97,.885]
            CardsRolled = []
            Rolled = []
            if args:
                args = list(args)
                for x in args:
                    if '/' in x: # /\\
                        args.remove(x)
                        x = re.sub('[^A-Za-z0-9]+', ' ', x)
                        SplitAmount = 0
                        for y in x:
                            if y == ' ':
                                SplitAmount += 1
                        SplitList = x.split(' ', SplitAmount)
                        for x in SplitList:
                            if x:
                                args.append(x)
                if 'df' in [x.lower() for x in args]:
                    Rates = [.94,.855]
                    args.remove('df')
                if args: # Check again since the value may not exist anymore after removing df from the step above
                    AllTwoStarCards = []
                    AllThreeStarCards = []
                    AllFourStarCards = []
                    Characters = []

                    for x in args:
                        if x.lower() not in Characters:                  
                            if x.lower() in ['roselia','popipa','hhw','pasupare','afterglow','morfonica','ras']:
                                if x.lower() == 'roselia':
                                    Characters.extend(('lisa','yukina','sayo','ako','rinko'))
                                elif x.lower() == 'popipa':
                                    Characters.extend(('kasumi', 'rimi', 'saya', 'tae', 'arisa'))
                                elif x.lower() == 'hhw':
                                    Characters.extend(('kokoro', 'kaoru', 'kanon', 'hagumi', 'misaki'))
                                elif x.lower() == 'pasupare':
                                    Characters.extend(('aya', 'eve', 'maya', 'chisato', 'hina'))
                                elif x.lower() == 'afterglow':
                                    Characters.extend(('ran', 'moca', 'himari', 'tsugumi', 'tomoe'))
                                elif x.lower() == 'morfonica':
                                    Characters.extend(('mashiro', 'nanami', 'toko', 'rui', 'tsukushi'))
                                elif x.lower() == 'ras':
                                    Characters.extend(('chiyu', 'reona', 'masuki', 'rokka', 'rei'))
                            else:
                                if x.lower() in ['rinboi','rin boi']:
                                    Characters.append('hagumi')
                                elif x.lower() in ['rock','rokku','lock','rokka','locku']:
                                    Characters.append('rokka')
                                elif x.lower() in ['chu','chu2']:
                                    Characters.append('chiyu')
                                elif x.lower() in ['npc','tsugu']:
                                    Characters.append('tsugumi')
                                elif x.lower() in ['saaya']:
                                    Characters.append('saya')
                                elif x.lower() in ['josh', 'john']: #for you qwewqa
                                    Characters.append('lisa')
                                else:
                                    Characters.append(x)
                    for chara in Characters:
                        for x in os.listdir(f"icons/{chara}/2"):
                            AllTwoStarCards.append(f"icons/{chara}/2/" + x)
                        for x in os.listdir(f"icons/{chara}/3"):
                            AllThreeStarCards.append(f"icons/{chara}/3/" + x)
                        for x in os.listdir(f"icons/{chara}/4"):
                            AllFourStarCards.append(f"icons/{chara}/4/" + x),
                else:
                    AllTwoStarCards = self.AllTwoStarCards
                    AllThreeStarCards = self.AllThreeStarCards
                    AllFourStarCards = self.AllFourStarCards
            else:
                AllTwoStarCards = self.AllTwoStarCards
                AllThreeStarCards = self.AllThreeStarCards
                AllFourStarCards = self.AllFourStarCards
            
            for _ in range(0,9):
                value = random.random()
                if value > Rates[0]:
                    Rolled.append(4)
                elif Rates[0] >= value > Rates[1]:
                    Rolled.append(3)
                else:
                    Rolled.append(2)
            # For guaranteed 3*
            value = random.random()
            if value > Rates[0]:
                Rolled.append(4)
            else:
                Rolled.append(3)
            TwoStarsRolled = Rolled.count(2)
            ThreeStarsRolled = Rolled.count(3)
            FourStarsRolled = Rolled.count(4)

            for x in Rolled:
                if x == 2:
                    random.shuffle(AllTwoStarCards)
                    CardsRolled.append(str(AllTwoStarCards[0]))
                elif x == 3:
                    random.shuffle(AllThreeStarCards)
                    CardsRolled.append(str(AllThreeStarCards[0]))
                else:
                    random.shuffle(AllFourStarCards)
                    CardsRolled.append(str(AllFourStarCards[0]))
        
        
        

            FirstHalfCardsRolled = CardsRolled[:len(CardsRolled)//2]        
            SecondtHalfCardsRolled = CardsRolled[len(CardsRolled)//2:]

            images = [Image.open(x) for x in CardsRolled]
            widths, heights = zip(*(i.size for i in images))
            total_width = sum(widths) / 2
            max_height = 2 * max(heights)
            new_im = Image.new('RGB', (int(total_width), max_height))
            FirstHalfImages = [Image.open(x) for x in FirstHalfCardsRolled]
            SecondHalfImages = [Image.open(x) for x in SecondtHalfCardsRolled]
            x_offset = 0
            for im in FirstHalfImages:
                new_im.paste(im, (x_offset,0))
                x_offset += im.size[0]        
            x_offset = 0

            for im in SecondHalfImages:
                new_im.paste(im, (x_offset,180))
                x_offset += im.size[0]        
            
            
            
            # Update roll database
            user = self.bot.get_user(ctx.message.author.id)
            user = user.name + '#' + user.discriminator

            for chara in CardsRolled:
                search = re.search('/([a-zA-Z]*)\/([0-9]*)', chara)
                name = search[1]
                cardtype = search[2]
                self.UpdateCharaRollsJSON(523337807847227402, 'self', name, cardtype)
                self.UpdateCharaRollsJSON(ctx.message.author.id, user, name, cardtype)

            self.UpdateRollsJSON(523337807847227402, 'self', TwoStarsRolled, ThreeStarsRolled, FourStarsRolled)
            self.UpdateRollsJSON(ctx.message.author.id, user, TwoStarsRolled, ThreeStarsRolled, FourStarsRolled)

            if 4 not in Rolled:
                Title = "Haha no 4*"
            else:
                Title = "mbn getting a 4*"

            import uuid
            from discord import File
            FileName = str(ctx.message.author.id) + '_' + str(uuid.uuid4()) + '.png'
            SavedFile = "rolls/" + FileName
            new_im.save(SavedFile)
            DiscordFileObject = File(SavedFile,filename=FileName)
            RolledStats = self.GetRollStats(ctx.message.author.id)
            
            await asyncio.sleep(.5)
            embed=discord.Embed(title=Title,color=discord.Color.blue())
            embed.set_thumbnail(url=RolledStats[5])
            embed.add_field(name='Total Cards Rolled',value="{:,}".format(RolledStats[0]),inline=True)
            embed.add_field(name='Total 4* Rolled',
                            value=RolledStats[3], inline=True)
            embed.add_field(name='4* Rate', value=RolledStats[4], inline=True)
            embed.add_field(name='2* Rolled',value=TwoStarsRolled,inline=True)
            embed.add_field(name='3* Rolled',value=ThreeStarsRolled,inline=True)
            embed.add_field(name='4* Rolled',value=FourStarsRolled,inline=True) 
            embed.set_image(url=f"attachment://{FileName}")
            embed.set_footer(text="Want to see all your stats? Use the rollstats command\nWant to check the leaderboards? Use the rolllb command")
            await ctx.send(file=DiscordFileObject, embed=embed)
        except IndexError:
            await ctx.send("Failed generating a roll. This is likely because the bot rolled a card that doesn't exist (e.g. 3* rokka)")
        except Exception as e:
            print(str(e))
            await ctx.send('Failed generating a roll. If this keeps happening, please use the `notify` command to let Josh know')
            pass

    @commands.command(name='lisafeet',
                    description='Possi and Aura told me to make this so here it is')
    async def forpossiandaura(self, ctx):
        # Pubcord
        if ctx.message.guild.id != 432379300684103699:
            await ctx.send('<:lisafoot_0_0:712737613060243476><:lisafoot_1_0:712737613081083945><:lisafoot_2_0:712737613295124550>\n<:lisafoot_0_1:712737613043204117><:lisafoot_1_1:712737612913180673><:lisafoot_2_1:712737613181878353>\n<:lisafoot_0_2:712737613064437810><:lisafoot_1_2:712737613026426962><:lisafoot_2_2:712737613257244682>')
        else:
            print('This command is disabled in this server.')

    @commands.command(name='lisaxodia',
                    description='lol')
    async def lisaxodia(self, ctx):
        # Pubcord
        if ctx.message.guild.id != 432379300684103699:
            from discord import File
            SavedFile = "img/lisaxodia.png"
            DiscordFileObject = File(SavedFile)
            await ctx.send(file=DiscordFileObject)
        else:
            print('This command is disabled in this server.')
        
    @commands.command(name='picture',
                      aliases=['p'],
                      description='Note: THIS MAY RETURN NSFW IMAGES\n\nReturns an image (or images if multiple names/bands are entered) with > 100 bookmarks on Pixiv for the specified character/band/or defaults to Bang Dream tag and returns one random image from that list.',
                      help='For bands, the values below are valid, if an invalid value is entered, the command will fail\n\nRoselia\nAfterglow\nPopipa\nPasupare\nHHW\n\n.picture\n.picture lisa\n.p roselia arisa himari')
    async def picture(self, ctx, *queries):
        try:
            from commands.apiFunctions import GetBestdoriAllCharasAPI
            from discord import File
            import random, json       
            
            AllQueries = []
            CharaImageURLs = []
            if not queries:
                AllQueries.append('バンドリ')
                CharaImageURLs.append(
                    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/BanG_Dream%21_logo.svg/1200px-BanG_Dream%21_logo.svg.png')
            elif queries[0] == 'yukilisa':
                newquery = 'リサゆき'
                AllQueries.append('リサゆき')
                CharaImageURLs.append('https://bestdori.com/res/icon/chara_icon_23.png')
                charaId = '23'

            else:
                for query in queries:
                    if query.lower() in ['roselia','afterglow','pasupare','popipa','hhw']:
                        newquery = query.lower()
                        if query.lower() == 'popipa':
                            AllQueries.append("Poppin'Party")
                            CharaImageURLs.append('https://vignette.wikia.nocookie.net/bandori/images/d/d2/Band_1.svg/revision/latest/scale-to-width-down/40?cb=20191102143957')
                        elif query.lower() == 'afterglow':
                            AllQueries.append("afterglow")
                            CharaImageURLs.append('https://vignette.wikia.nocookie.net/bandori/images/2/21/Band_2.svg/revision/latest/scale-to-width-down/40?cb=20191102143958')
                        elif query.lower() == 'hhw':
                            AllQueries.append("ハロー、ハッピーワールド!")
                            CharaImageURLs.append('https://vignette.wikia.nocookie.net/bandori/images/8/82/Band_3.svg/revision/latest/scale-to-width-down/40?cb=20191102143958')
                        elif query.lower() == 'pasupare':
                            AllQueries.append("PastelPalettes")
                            CharaImageURLs.append('https://vignette.wikia.nocookie.net/bandori/images/3/3e/Band_4.svg/revision/latest/scale-to-width-down/40?cb=20191102143958')
                        elif query.lower() == 'roselia':
                            AllQueries.append("roselia")
                            CharaImageURLs.append('https://vignette.wikia.nocookie.net/bandori/images/e/ee/Icon_roselia.png/revision/latest/scale-to-width-down/40?cb=20190316121700')
                    else:
                        r = await GetBestdoriAllCharasAPI()
                        charaId = False
                        for x in r:
                            if charaId:
                                break
                            charalist = r[x]['characterName']
                            if query.capitalize() in charalist[1]:
                                charaId = x
                                AllQueries.append("".join(charalist[0].split()))
                                CharaImageURLs.append('https://bestdori.com/res/icon/chara_icon_%s.png' % charaId)
            for newquery, charaImageURL in zip(AllQueries, CharaImageURLs):
                db = f'databases/{newquery}.json'
                with open(db, 'r') as file:
                    db = json.load(file)
                pic = random.choice(db[newquery]['pics'])
                PicID = pic['id']
                PicURL = pic['image_urls']['large']
                if charaId == '23':
                    SaveImage = True
                    SavedPicPath = f'pfps/{PicID}_p0.jpg'
                else:
                    SaveImage = False
                    SavedPicPath = f'imgTmp/{PicID}_p0.jpg'
                response = requests.get(PicURL, 
                                        headers={
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 
                                            'referer' : PicURL,
                                            'scheme' : 'https',
                                            'accept' : 'image/webp,image/apng,image/*,*/*;q=0.8'
                                            },
                                        stream=True)
                if os.path.exists(SavedPicPath):
                    os.remove(SavedPicPath)
                with open(SavedPicPath, 'ab') as Out_file:
                    response.raw.decode_content = True
                    Out_file.write(response.content)   
                    DiscordFileObject = File(SavedPicPath)
                
                if SaveImage:
                    from PIL import Image
                    # Since the original image is saved as corrupt, save it this way
                    SavedPFP = Image.open(SavedPicPath)
                    SavedPFP.save(SavedPicPath)

                channel: discord.TextChannel = self.bot.get_channel(712732064381927515)  # Change this channel to the channel you want the bot to send images to so it can grab a URL for the embed
                fileSend: discord.Message = await channel.send(file=DiscordFileObject)

                TitleURL = f"https://www.pixiv.net/en/artworks/{PicID}"


                embed=discord.Embed(title=pic['title'],url=TitleURL,color=discord.Color.blue())
                embed.set_thumbnail(url=charaImageURL)
                embed.set_image(url=fileSend.attachments[0].url)
                embed.add_field(name='Artist',value=pic['user']['name'],inline=True)
                embed.add_field(name='Date',value=pic['create_date'],inline=True)
                await ctx.send(embed=embed)
        except:
            await ctx.send('Failed posting image. Please use the `notify` command if this keeps happening')
                   
    @commands.command(name='rolllb',
                      aliases=['rlb'],
                      description='Shows the top 20 leaderboards for the roll command',
                      help='You can specify which leaderboard you want to check by including the character name at the end, if omitted, it will return the overall leaderboards\n\n.rolllb\n.rlb lisa')
    async def rolllb(self, ctx, *Chara):
        try:
            from operator import itemgetter
            from tabulate import tabulate
            if Chara:
                Chara = Chara[0] 
                FileName = f'databases/rolls/{Chara}.json'
            else:
                FileName = 'databases/rolls/rolls.json'
            with open(FileName) as file:
                api = json.load(file)
            Rolls = []
            for key in api:
                if key != '523337807847227402' and key != 'overall':
                    if 'Name' in api[key]:
                        Name = api[key]['Name']
                    else:
                        Name = key
                    TotalRolled = int(api[key]['TotalRolls']) * 10 if not Chara else int(api[key]['TotalRolls'])
                    #FourStarPercent = str(round((((int(api[key]['FourStars']) / TotalRolled ) * 100), 2)) + '%')
                    FourStarPercent = str(round(((int(api[key]['FourStars']) / TotalRolled) * 100), 2)) + '%'
                    Rolls.append([Name,api[key]['TotalRolls'],api[key]['FourStars'],FourStarPercent])
                    Rolls = sorted(Rolls,key=itemgetter(1),reverse=True)
            Rolls = Rolls[0:20]
            RollsHeader = 'Total Rolls' if not Chara else f"Total {Chara.capitalize()}'s rolled"
            output = "```" + tabulate(Rolls,headers=['User',RollsHeader,'Total 4*','4* %'],tablefmt='plain') + "```"
        except FileNotFoundError:
            output = 'No rolls have been generated for that character yet'
        except Exception as e:
            output = 'Failed getting the roll leaderboards. Please use the `notify` command if this keeps happening'
        await ctx.send(output)
        
    @commands.command(name='birthdays',
                      aliases=['bdays','bday'],
                      description="Note: This data may be publicly accessible\n\nIf you're like me and easily forget birthdays, you can use this command to add birthday entries and grab them as needed. Entries are server specific",
                      help='.birthdays (this returns all birthdays for the server the command was ran in\n.bdays add Aug 25 (adds an entry to the list for the user running the command\n.bdays del (removes the user running the command from the database)' )
    async def bdays(self,ctx,*add):
        if add and add[0] == 'add':
            user = self.bot.get_user(ctx.message.author.id)
            Name = user.name + '#' + user.discriminator
            ServerID = ctx.message.guild.id
            Date = add[1].capitalize() + ' ' + add[2]
            try:
                self.UpdateBirthdaysJSON(ServerID, Name, Date, False)
                output = f"Successfully added user `{Name}` to the birthdays list with date `{Date}`"
            except:
                output = "Failed adding user to the birthdays list. Please use the `notify` command if this keeps happening"
        elif add and add[0] == 'del':
            user = self.bot.get_user(ctx.message.author.id)
            Name = user.name + '#' + user.discriminator
            ServerID = ctx.message.guild.id
            Date = '0 0'
            try:
                self.UpdateBirthdaysJSON(ServerID, Name, Date, True)
                output = f"Successfully removed user `{Name}` from the birthdays list"
            except:
                output = "Failed removing user from the birthdays list. Please use the `notify` command if this keeps happening"
            
        else:
            from tabulate import tabulate
            from datetime import datetime          
            FileName = 'databases/birthdays.json'
            with open(FileName) as file:
                api = json.load(file)
            entries = []
            OrderedDates = api[str(ctx.message.guild.id)]
            OrderedDates = ({k:v for k, v in sorted(OrderedDates.items(), key = lambda x : datetime.strptime(x[1]['Date'], "%B %d"))})
            for key in OrderedDates:
                entries.append([key,api[str(ctx.message.guild.id)][key]['Date']])
            output = "```" + tabulate(entries,headers=['Name','Date'],tablefmt='plain') + "```"
        await ctx.send(output)
        
    def UpdateBirthdaysJSON(self, Server, User, Date, Delete: bool = False):
        import json
        FileName = 'databases/birthdays.json'
        try:
            with open(FileName) as file:
                api = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            # Create the file and add an empty dict to it so we can load the json file
            with open(FileName, 'a+') as file:
                data = {}
                json.dump(data, file, indent=2)
            
            # Load the newly created file
            with open(FileName) as file:
                api = json.load(file)

        # Check if there's an entry for the Server and User in the json file 
        if not Delete:
            if str(Server) in api:
                if str(User) not in api[str(Server)]:
                    api[str(Server)].update({User: {'Date' : Date}})
                else:
                    api[str(Server)][User]['Date'] = Date
                with open(FileName, 'w') as f:
                    json.dump(api, f)
                    
            # This adds a new key to the dictionary
            else:
                data = {
                        Server:
                                    {
                                        User: {
                                            'Date' : Date                                       
                                        }
                                    }
                }
                with open(FileName, 'w') as f:
                    api.update(data)
                    json.dump(api, f)
        else:
            api[str(Server)].pop(User, None)
            with open(FileName, 'w') as f:
                json.dump(api, f)

def setup(bot):
    bot.add_cog(Fun(bot))
