from discord.ext import commands
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
    
    @commands.command(name='updatecards',
                      hidden=True,
                      enabled=False)
    async def GetIcons(self, ctx):        
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
                                           
                if Rarity != '1':
            
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
                    else:
                        bandPng = "img/band_5.png"
                    bandBg = Image.open(bandPng)
                    im.paste(bandBg, (1, 2), mask=bandBg)

                    im.save(IconsPath)
            except:
                print(f"Failed adding card with ID {x}")
                pass

    @commands.command(name='roll',
                      description='Simulates a 10 roll')
    async def gacharoll(self, ctx):
        try:
            import random
            from PIL import Image
            from PIL.ImageDraw import Draw
            from PIL.ImageFont import truetype

            CardsRolled = []
            Rolled = []
            for _ in range(0,10):
                value = random.random()
                if value > .97:
                    Rolled.append(4)
                elif .97 >= value > .885:
                    Rolled.append(3)
                else:
                    Rolled.append(2)
            if all(x==Rolled[0] for x in Rolled):
                Rolled.pop()
                value = random.random()
                if value > .97:
                    Rolled.append(4)
                else:
                    Rolled.append(3)
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
                
            import uuid
            from discord import File
            SavedFile = "rolls/" + str(uuid.uuid4()) + '.png'
            new_im.save(SavedFile)

            DiscordFileObject = File(SavedFile)
            await ctx.send(file=DiscordFileObject)
        except:
            await ctx.send('Failed generating a roll. If this keeps happening, please use the `notify` command to let Josh know')
            pass


def setup(bot):
    bot.add_cog(Fun(bot))