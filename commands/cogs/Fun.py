from discord.ext import commands
from typing import Union
import discord, shutil, time, requests, math, asyncio, os

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AllCards = asyncio.run(self.GetCards())
        self.AllTwoStarCards = self.AllCards[0]
        self.AllThreeStarCards = self.AllCards[1]
        self.AllFourStarCards = self.AllCards[2]

    async def GetCards(self):
        AllFourStarCards = []
        AllThreeStarCards = []
        AllTwoStarCards = []
        TwoPath = "icons/2/"
        ThreePath = "icons/3/"
        FourPath = "icons/4/"
        for file in os.listdir(TwoPath):
            AllTwoStarCards.append(file)
        for file in os.listdir(ThreePath):
            AllThreeStarCards.append(file)
        for file in os.listdir(FourPath):
            AllFourStarCards.append(file)
        return AllTwoStarCards, AllThreeStarCards, AllFourStarCards

    def GetRollStats(self, user):
        import json
        try:
            with open('databases/rolls.json') as file:
                api = json.load(file)
            user = self.bot.get_user(user)
            Rolled = []
            Rolled.append(str(api[str(user.id)]['TotalRolls'] * 10))
            Rolled.append(api[str(user.id)]['TwoStars'])
            Rolled.append(api[str(user.id)]['ThreeStars'])
            Rolled.append(api[str(user.id)]['FourStars'])
            Rolled.append(str(round(((int(api[str(user.id)]['FourStars']) / (int(str(api[str(user.id)]['TotalRolls'] * 10)))) * 100), 2)) + '%')
            Rolled.append(user.avatar_url.BASE + user.avatar_url._url)
            return Rolled
        except KeyError:
            return 'No stats found for that user'
        except:
            return 'Unknown error. If this keeps happening please use the `notify` command to let Josh know'

    def UpdateRollsJSON(self, UserIDOrOverall, TwoStars, ThreeStars, FourStars):
        import json
        FileName = 'databases/rolls.json'
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
            with open(FileName, 'w') as f:
                json.dump(api, f)
        # This adds a new key to the dictionary
        else:
            data = {UserIDOrOverall: {
                            "TotalRolls" : 1,
                            "TwoStars" : TwoStars,
                            "ThreeStars" : ThreeStars,
                            "FourStars" : FourStars
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
        CardAPI = await GetBestdoriAllCardsAPI()
        CharaAPI = await GetBestdoriAllCharactersAPI()
        for x in CardAPI:
            try:
                im = Image.new("RGBA", (180, 180))
                Folder = str(math.floor(int(x) / 50)).zfill(2)
                ResourceSetName = CardAPI[x]['resourceSetName']
                Rarity = str(CardAPI[x]['rarity'])  
                Attribute = str(CardAPI[x]['attribute'])      
                IconsPath = f"icons/{Rarity}/{x}.png"
                CharacterID = str(CardAPI[x]['characterId'])
                BandID = CharaAPI[CharacterID]['bandId']
                AllowedTypes = ['limited','permanent']     
                if Rarity != '1':
                    
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

                        if Rarity == '2':
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
                        
                        if BandID == 1:
                            bandPng = "img/band_1.png"
                        elif BandID == 2:
                            bandPng = "img/band_2.png"
                        elif BandID == 3:
                            bandPng = "img/band_3.png"
                        elif BandID == 4:
                            bandPng = "img/band_4.png"
                        elif BandID == 21:
                            bandPng = "img/band_21.png"
                        else:
                            bandPng = "img/band_5.png"
                        bandBg = Image.open(bandPng)
                        im.paste(bandBg, (1, 2), mask=bandBg)

                        im.save(IconsPath)
            except:
                print(f"Failed adding card with ID {x}")
                pass

    @commands.command(name='rollstats',
                     aliases=['rs'],
                     description='Returns the stats from the roll command for a particular user',
                     help='.rollstats (this defaults to the user running the command)\n\n.rollstats @Lisa#4081\n\n.rollstats Lisa (this searches all the users with Lisa as their Discord name and returns the first user found)\n\n.rs 158699060893581313\n\n.rs total (returns ALL stats accumulated so far)')
    async def rollstats(self, ctx, user: Union[discord.Member, str, int]=None):
        import json
        if user:
            if not isinstance(user, discord.Member):
                if user.isnumeric():
                    id = user
                    user = self.bot.get_user(523337807847227402)
                    Title = "Roll Stats"

                elif user == 'total':
                    user = self.bot.get_user(523337807847227402)   
                    id = 'overall'
                    Title = "Total Roll Stats"
            else:
                id = user.id
                Title = f"{user.display_name}#{user.discriminator}'s Roll Stats"

        elif user is None:
            user = self.bot.get_user(ctx.message.author.id)   
            id = ctx.message.author.id
            Title = f"{user.display_name}#{user.discriminator}'s Roll Stats"
     
        try:
            with open('databases/rolls.json') as file:
                api = json.load(file)
            TotalRolled = str(api[str(id)]['TotalRolls'] * 10)
            TwoStarsRolled = api[str(id)]['TwoStars']
            ThreeStarsRolled = api[str(id)]['ThreeStars']
            FourStarRate = str(round(((int(FourStarsRolled) / (int(TotalRolled))) * 100), 2)) + '%'
            Icon = user.avatar_url.BASE + user.avatar_url._url
            embed=discord.Embed(title=Title,color=discord.Color.blue())
            embed.set_thumbnail(url=Icon)
            embed.add_field(name='Total Cards Rolled',value=TotalRolled,inline=True)
            embed.add_field(name='4* Rate',value=FourStarRate,inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            embed.add_field(name='2* Rolled',value=TwoStarsRolled,inline=True)
            embed.add_field(name='3* Rolled',value=ThreeStarsRolled,inline=True)
            embed.add_field(name='4* Rolled',value=FourStarsRolled,inline=True)
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send('No stats found for that user')
        except:
            await ctx.send('Unknown error. If this keeps happening please use the `notify` command to let Josh know')
        

    @commands.command(name='roll',
                      description='Simulates a 10 roll using the default rates. Add df to the input to simulate increased rates.',
                      help='.roll\n.roll df')
    async def gacharoll(self, ctx, *args):
        try:

            import random
            from PIL import Image
            from PIL.ImageDraw import Draw
            from PIL.ImageFont import truetype

            CardsRolled = []
            Rolled = []
            if args and 'df' in [x.lower() for x in args]:
                Rates = [.94,.855]
            else:
                Rates = [.97,.885]

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
                    random.shuffle(self.AllTwoStarCards)
                    CardsRolled.append("icons/2/" + str(self.AllTwoStarCards[0]))
                elif x == 3:
                    random.shuffle(self.AllThreeStarCards)
                    CardsRolled.append("icons/3/" + str(self.AllThreeStarCards[0]))
                else:
                    random.shuffle(self.AllFourStarCards)
                    CardsRolled.append("icons/4/" + str(self.AllFourStarCards[0]))
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
            

            self.UpdateRollsJSON('overall', TwoStarsRolled, ThreeStarsRolled, FourStarsRolled)
            self.UpdateRollsJSON(ctx.message.author.id, TwoStarsRolled, ThreeStarsRolled, FourStarsRolled)

            if 4 not in Rolled:
                Title = "Haha no 4*"
            else:
                Title = "You spent $25 for a png"

            import uuid
            from discord import File
            SavedFile = "rolls/" + str(ctx.message.author.id) + '_' + str(uuid.uuid4()) + '.png'
            new_im.save(SavedFile)
            DiscordFileObject = File(SavedFile)
            RolledStats = self.GetRollStats(ctx.message.author.id)

            channel: discord.TextChannel = self.bot.get_channel(712732064381927515)  # Change this channel to the channel you want the bot to send images to so it can grab a URL for the embed
            fileSend: discord.Message = await channel.send(file=DiscordFileObject)
            embed=discord.Embed(title=Title,color=discord.Color.blue())
            embed.set_image(url=fileSend.attachments[0].url)
            embed.set_thumbnail(url=RolledStats[5])
            embed.add_field(name='4* Rate',value=RolledStats[4],inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            embed.add_field(name='2* Rolled',value=RolledStats[1],inline=True)
            embed.add_field(name='3* Rolled',value=RolledStats[2],inline=True)
            embed.add_field(name='4* Rolled',value=RolledStats[3],inline=True) 

            await ctx.send(embed=embed)
        except Exception as e:
            print(str(e))
            await ctx.send('Failed generating a roll. If this keeps happening, please use the `notify` command to let Josh know')
            pass

    @commands.command(name='lisafeet',
                    description='Possi and Aura told me to make this so here it is')
    async def forpossiandaura(self, ctx):
        await ctx.send('<:lisafoot_0_0:712737613060243476><:lisafoot_1_0:712737613081083945><:lisafoot_2_0:712737613295124550>\n<:lisafoot_0_1:712737613043204117><:lisafoot_1_1:712737612913180673><:lisafoot_2_1:712737613181878353>\n<:lisafoot_0_2:712737613064437810><:lisafoot_1_2:712737613026426962><:lisafoot_2_2:712737613257244682>')

def setup(bot):
    bot.add_cog(Fun(bot))