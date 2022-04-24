from discord.ext import commands
from typing import Union
import discord, shutil, time, requests, math, asyncio, os, json

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AllCards = asyncio.run(self.GetCards())
        self.AllTwoStarCards = self.AllCards[0]
        self.AllThreeStarCards = self.AllCards[1]
        self.AllFourStarCards = self.AllCards[2]

    async def GetCardRarityCount(self, rarity: int):
        from timeit import default_timer
        time = default_timer()
        from commands.apiFunctions import get_bestdori_all_cards_api5
        all_cards_api = await get_bestdori_all_cards_api5()
        count = 0
        for card in all_cards_api:
            if all_cards_api[card]['rarity'] == rarity and all_cards_api[card]['type'] in ['permanent', 'limited']:
                count += 1
        #count = sum(map(lambda value: value["rarity"] == rarity, all_cards_api.values()))
        print(f"{default_timer() - time}")
        return count
    
    async def get_titles(self, server):
        import requests, shutil, os
        from tqdm import tqdm
        from commands.apiFunctions import get_bestdori_title_names_api
        titles = await get_bestdori_title_names_api(server)
        for title in tqdm(titles, "Extracting titles.."):
            if not os.path.isfile(f'data/img/titles/{server}/{title}'):
                r = requests.get(f'https://bestdori.com/assets/{server}/thumb/degree_rip/{title}',stream=True)
                with open(f'data/img/titles/{server}/{title}', 'wb') as out_file:
                    shutil.copyfileobj(r.raw, out_file)
                del r  
        print('Finished extracting titles')
    
    async def GetCards(self):
        AllFourStarCards = []
        AllThreeStarCards = []
        AllTwoStarCards = []

        for folder in os.listdir("data/img/icons/"):
            if folder != '.DS_Store':
                for subfolder in os.listdir(f"data/img/icons/{folder}"):
                    if subfolder == '2':
                        for file in os.listdir(f"data/img/icons/{folder}/{subfolder}"):
                            AllTwoStarCards.append(f"data/img/icons/{folder}/{subfolder}/" + file)
                    elif subfolder == '3':
                        for file in os.listdir(f"data/img/icons/{folder}/{subfolder}"):
                            AllThreeStarCards.append(f"data/img/icons/{folder}/{subfolder}/" + file)
                    elif subfolder == '4':
                        for file in os.listdir(f"data/img/icons/{folder}/{subfolder}"):
                            AllFourStarCards.append(f"data/img/icons/{folder}/{subfolder}/" + file)
                    else:
                        pass

        return AllTwoStarCards, AllThreeStarCards, AllFourStarCards


    @commands.command(name='updatecards',
                      hidden=True,
                      enabled=True)
    async def GetIcons(self, ctx, gachacards: bool = True):
        try:
            await UpdateCardIcons()
            await ctx.send('Updated icons successfully')
            print('Updated icons successfully')
        except:
            print('Failed updating icons')
         
    @commands.command(name='updatetitles',
                      hidden=True)
    async def update_titles(self, ctx, server: str):
        if ctx.author.id == 158699060893581313:
            try:
                await self.get_titles(server)
                await ctx.send('Successfully updated titles')
            except Exception as e:
                await ctx.send(f'Failed updating titles\n\nException: {e}')
        else:
            await ctx.send('Unauthorized to use this command')
                
    @commands.command(name='rollstats',
                     aliases=['rs'],
                     description='Returns the stats from the roll command for a particular user',
                     help='.rollstats (this defaults to the user running the command)\n.rollstats @Lisa#4081\n.rollstats Lisa (this searches all the users with Lisa as their Discord name and returns the first user found)\n.rs Lisa Rinko (returns the stats for user Lisa and character Rinko)\n.rs total (returns ALL stats accumulated so far)')
    #@ctime
    async def roll_stats(self, ctx, user: Union[discord.Member, str, int]=None, *character):
        from commands.formatting.DatabaseFormatting import get_roll_info
        if character and len(character) > 1:
            await ctx.send(f"Note: Currently only 1 character rolls stats can be pulled at a time. Grabbing stats for {character[0]}")
        if user:
            if not isinstance(user, discord.Member):
                if user.isnumeric():
                    user_id = user
                    user = self.bot.get_user(523337807847227402)
                    title = "Roll Stats"

                elif user == 'total':
                    user = self.bot.get_user(523337807847227402)
                    id = user.id
                    title = "Total Roll Stats" if not character else f"{character[0].capitalize()} Total Roll Stats"
            else:
                user_id = user.id
                title = f"{user.display_name}#{user.discriminator}'s Roll Stats" if not character else f"{user.display_name}#{user.discriminator}'s {character[0].capitalize()} Roll Stats"

        else:
            user = ctx.author
            user_id = user.id
            title = f"{user.display_name}#{user.discriminator}'s Roll Stats"

        try:
            if not character:
                roll_info = await get_roll_info(user_id)
            else:
                roll_info = await get_roll_info(user_id, character[0])
            from commands.formatting.misc_functions import get_avatar_url
            avatar = user.avatar_url.BASE + user.avatar_url._url
            if user_id != 523337807847227402: # Bot
                two_star_count = roll_info[0][1]
                three_star_count = roll_info[0][2]
                four_star_count = roll_info[0][3]
            else:
                two_star_count = roll_info[0][0]
                three_star_count = roll_info[0][1]
                four_star_count = roll_info[0][2]
            total_count = two_star_count + three_star_count + four_star_count
            four_star_rate = f"{round(((four_star_count / total_count) * 100), 2)}%"
            embed = discord.Embed(title=title, color=discord.Color.blue())
            embed.set_thumbnail(url=avatar)
            embed.add_field(name='Total Cards Rolled',value="{:,}".format(total_count),inline=True)
            embed.add_field(name='4* Rate',value=four_star_rate, inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            embed.add_field(name='2* Rolled',value="{:,}".format(two_star_count),inline=True)
            embed.add_field(name='3* Rolled',value="{:,}".format(three_star_count),inline=True)
            embed.add_field(name='4* Rolled',value="{:,}".format(four_star_count),inline=True)
            await ctx.send(embed=embed)
        except UnboundLocalError:
           await ctx.send('No user found. They must be in this server and their names must match (e.g. lisa will not work for the bot since its name is Lisa') 
        except IndexError:
            await ctx.send('No stats found for that user')
        except:
            await ctx.send('Unknown error. If this keeps happening please use the `notify` command to let Josh know')
    
    @commands.command(name='album',
                      aliases=['al'],
                      description='Shows a picture containing all the 4* (3* and specific characters if requested) one has rolled using the `roll` command as well as how many total has been obtained from the current pool',
                      help='By default, the album only shows 4 stars and uploads a PNG image. To show 3 stars or characters, add 3 or the character/band names to the command. For a JPG image (use this if you receive an error about file size) add JPG to the command\n\nExamples:\n\n.album\n.al 3\n.al 3 lisa rinko popipa jpg')
    async def get_roll_album(self, ctx, *args):
        try:
            from PIL import Image
            from PIL.ImageDraw import Draw
            from PIL.ImageFont import truetype
            from discord import File
            from commands.formatting.DatabaseFormatting import get_album_card_ids
            album_card_ids = await get_album_card_ids(ctx.author.id)
            if not album_card_ids:
                await ctx.send(f"That user has no cards rolled. Use the roll command to start generating cards")
            else:
                import uuid
                embed=discord.Embed(title=f"{ctx.message.author.name}'s Album", color=discord.Color.blue())
                embed.set_thumbnail(url=ctx.message.author.avatar_url.BASE + ctx.message.author.avatar_url._url)
                owned_four_star_ids = album_card_ids[0]['four_star_ids']
                owned_four_star_ids.sort(reverse=True)
                owned_four_star_count = []
                owned_three_star_count = []
                owned_card_ids = []
                total_four_stars = 0
                total_three_stars = 0
                trained_icons_paths = []                
                include_three_stars = False
                use_jpg = False
                if 'jpg' in [x.lower() for x in args]:
                    use_jpg = True
                    args = list(args)
                    args.remove('jpg')
                if not args:
                    total_four_stars = await self.GetCardRarityCount(4)
                    owned_card_ids += owned_four_star_ids
                else:
                    if '3' in args:
                        args = list(args)
                        args.remove('3')
                        owned_three_star_ids = album_card_ids[0]['three_star_ids']
                        owned_three_star_ids.sort(reverse=True)
                        include_three_stars = True
                    if args:  
                        characters = [] 
                        owned_four_star_count = 0 # reset original value
                        owned_three_star_count = 0
                        for x in args:                 
                            if x.lower() not in characters:                  
                                if x.lower() in ['roselia','popipa', 'hhw', 'pasupare', 'afterglow','morfonica', 'ras']:
                                    if x.lower() == 'roselia':
                                        characters.extend(('lisa', 'yukina','sayo', 'ako', 'rinko'))
                                    elif x.lower() == 'popipa':
                                        characters.extend(('kasumi', 'rimi', 'saya', 'tae', 'arisa'))
                                    elif x.lower() == 'hhw':
                                        characters.extend(('kokoro', 'kaoru', 'kanon', 'hagumi', 'misaki'))
                                    elif x.lower() == 'pasupare':
                                        characters.extend(('aya', 'eve', 'maya', 'chisato', 'hina'))
                                    elif x.lower() == 'afterglow':
                                        characters.extend(('ran', 'moca', 'himari', 'tsugumi', 'tomoe'))
                                    elif x.lower() == 'morfonica':
                                        characters.extend(('mashiro', 'nanami', 'toko', 'rui', 'tsukushi'))
                                    elif x.lower() == 'ras':
                                        characters.extend(('chiyu', 'reona', 'masuki', 'rokka', 'rei'))
                                else:
                                    if x.lower() in ['rinboi', 'rin boi']:
                                        characters.append('hagumi')
                                    elif x.lower() in ['rock', 'rokku', 'lock', 'rokka', 'locku']:
                                        characters.append('rokka')
                                    elif x.lower() in ['chu', 'chu2']:
                                        characters.append('chiyu')
                                    elif x.lower() in ['npc', 'tsugu']:
                                        characters.append('tsugumi')
                                    elif x.lower() in ['saaya']:
                                        characters.append('saya')
                                    elif x.lower() in ['josh', 'john']: #for you qwewqa
                                        characters.append('lisa')
                                    elif x.lower() in ['masking', 'mask']:
                                        characters.append('masuki')
                                    elif x.lower() in ['layer']: 
                                        characters.append('rei')
                                    else:
                                        characters.append(x)
                        from commands.formatting.GameCommands import check_album_ids, get_chara_card_count
                        owned_four_star_ids = await check_album_ids(owned_four_star_ids, characters)
                        owned_three_star_ids = await check_album_ids(owned_three_star_ids, characters) if include_three_stars else []
                        owned_card_ids = owned_four_star_ids + owned_three_star_ids
                        for chara in characters:
                            total_four_stars += await get_chara_card_count(chara, 4)
                            if include_three_stars:
                                total_three_stars += await get_chara_card_count(chara, 3)
                    else:
                        owned_three_star_count = len(owned_three_star_ids)
                        total_three_stars = await self.GetCardRarityCount(3)
                        owned_card_ids += owned_four_star_ids
                        owned_card_ids += owned_three_star_ids
                        total_four_stars = await self.GetCardRarityCount(4)
                        
                for card_id in owned_card_ids:
                    trained_icons_paths.append(f"data/img/icons/full_icons/{card_id}_trained.png")
                
                owned_four_star_count = len(owned_four_star_ids)
                embed.add_field(name='4*',value=f'{owned_four_star_count} / {total_four_stars}', inline=True)
                if include_three_stars:
                    owned_three_star_count = len(owned_three_star_ids)
                    embed.add_field(name='3*',value=f'{owned_three_star_count} / {total_three_stars}', inline=True)
                total_cards_owned = len(owned_card_ids)
                rows = math.ceil(total_cards_owned / 10)
                width = 1800 # 10 cards per row, 180px per icon
                height = rows * 180                
                if use_jpg:
                    ext = '.jpg'
                    album = Image.new('RGB', (int(width), height))
                else:
                    ext = '.png'
                    album = Image.new('RGBA', (int(width), height))
                file_name = f"{uuid.uuid4()}{ext}"    
                x_offset = 0
                y_offset = 0
                icons = [Image.open(x) for x in trained_icons_paths]
                for icon in icons:
                    album.paste(icon, (x_offset, y_offset))
                    x_offset += 180
                    if x_offset >= width: # new row
                        x_offset = 0
                        y_offset += 180
                album.save(file_name, optimize=True,qualiy=100)
                discord_file = File(file_name, filename=file_name)
                embed.set_image(url=f"attachment://{file_name}")
                message = await ctx.send('Uploading..')
                await ctx.send(file=discord_file, embed=embed)
                await message.delete()
                os.remove(file_name)
        except json.JSONDecodeError:
            await ctx.send(f'No rolls found for your user, please use the `roll` command to generate roll data')
        except SystemError:
            await ctx.send(f'No 4* were found for your user, please use the `roll` command to get more cards or add `3` to the command to check your 3* album')
        except discord.errors.HTTPException:
            os.remove(file_name)
            await ctx.send(f"Album size too large, please rerun the command but add `jpg` to it to upload a smaller sized image")
        except Exception as e:
            print(f"{e}")
            await ctx.send(f'Unknown error. Likely there is no card data for your user yet, please use the `roll` command to get more cards or add `3` to the command to check your 3* album')
        if os.path.exists(file_name):
            print('Removing file')
        else:
            print('Not removing file')
    @commands.command(name='roll',
                      description='Simulates a 10 roll using the default rates and all the permanent/limited cards that have been released in JP so far. Event cards are not included. Add df and/or the bands/characters names to the input to simulate increased rates/only roll those cards.',
                      help='For bands, the values below are valid, if an invalid value is entered, the command will fail\n\nRoselia\nAfterglow\nPopipa\nPasupare\nHHW\nMorfonica\n\n.roll\n.roll df\n.roll lisa\n.roll df yukina lisa\n.roll roselia\n.roll roselia popipa')
    async def gacha_roll(self, ctx, *args):
        from timeit import default_timer
        from functools import wraps
        user = self.bot.get_user(ctx.message.author.id)
        try:
            import re
            import random
            from PIL import Image
            from PIL.ImageDraw import Draw
            from PIL.ImageFont import truetype
            from commands.formatting.DatabaseFormatting import get_roll_info, update_rolls_db, update_roll_album_db
            rates = [.97, .885]
            cards_rolled_paths = []
            rolled_card_rarities = []
            all_two_star_cards_paths = self.AllTwoStarCards
            all_three_star_cards_paths = self.AllThreeStarCards
            all_four_star_cards_paths = self.AllFourStarCards
            if args:
                args = list(args)
                for x in args:
                    if '/' in x: # /\\
                        args.remove(x)
                        x = re.sub('[^A-Za-z0-9]+', ' ', x)
                        split_amount = 0
                        for y in x:
                            if y == ' ':
                                split_amount += 1
                        split_list = x.split(' ', split_amount)
                        for x in split_list:
                            if x:
                                args.append(x)
                if 'df' in [x.lower() for x in args]:
                    rates = [.94,.855]
                    args.remove('df')
                if args: # Check again since the value may not exist anymore after removing df from the step above
                    characters = []                    
                    all_two_star_cards_paths = []
                    all_three_star_cards_paths = []
                    all_four_star_cards_paths = []

                    for x in args:
                        if x.lower() not in characters:                  
                            if x.lower() in ['roselia','popipa', 'hhw', 'pasupare', 'afterglow','morfonica', 'ras']:
                                if x.lower() == 'roselia':
                                    characters.extend(('lisa', 'yukina','sayo', 'ako', 'rinko'))
                                elif x.lower() == 'popipa':
                                    characters.extend(('kasumi', 'rimi', 'saya', 'tae', 'arisa'))
                                elif x.lower() == 'hhw':
                                    characters.extend(('kokoro', 'kaoru', 'kanon', 'hagumi', 'misaki'))
                                elif x.lower() == 'pasupare':
                                    characters.extend(('aya', 'eve', 'maya', 'chisato', 'hina'))
                                elif x.lower() == 'afterglow':
                                    characters.extend(('ran', 'moca', 'himari', 'tsugumi', 'tomoe'))
                                elif x.lower() == 'morfonica':
                                    characters.extend(('mashiro', 'nanami', 'toko', 'rui', 'tsukushi'))
                                elif x.lower() == 'ras':
                                    characters.extend(('chiyu', 'reona', 'masuki', 'rokka', 'rei'))
                            else:
                                if x.lower() in ['rinboi', 'rin boi']:
                                    characters.append('hagumi')
                                elif x.lower() in ['rock', 'rokku', 'lock', 'rokka', 'locku']:
                                    characters.append('rokka')
                                elif x.lower() in ['chu', 'chu2']:
                                    characters.append('chiyu')
                                elif x.lower() in ['npc', 'tsugu']:
                                    characters.append('tsugumi')
                                elif x.lower() in ['saaya']:
                                    characters.append('saya')
                                elif x.lower() in ['josh', 'john']: #for you qwewqa
                                    characters.append('lisa')
                                elif x.lower() in ['masking', 'mask']:
                                    characters.append('masuki')
                                elif x.lower() in ['layer']: 
                                    characters.append('rei')
                                else:
                                    characters.append(x)
                    for chara in characters:
                        for x in os.listdir(f"data/img/icons/{chara}/2"):
                            all_two_star_cards_paths.append(f"data/img/icons/{chara}/2/" + x)
                        for x in os.listdir(f"data/img/icons/{chara}/3"):
                            all_three_star_cards_paths.append(f"data/img/icons/{chara}/3/" + x)
                        for x in os.listdir(f"data/img/icons/{chara}/4"):
                            all_four_star_cards_paths.append(f"data/img/icons/{chara}/4/" + x),

            for _ in range(0,9):
                value = random.random()
                if value > rates[0]:
                    rolled_card_rarities.append(4)
                elif rates[0] >= value > rates[1]:
                    rolled_card_rarities.append(3)
                else:
                    rolled_card_rarities.append(2)
            # For guaranteed 3*
            value = random.random()
            if value > rates[0]:
                rolled_card_rarities.append(4)
            else:
                rolled_card_rarities.append(3)
            two_stars_rolled = rolled_card_rarities.count(2)
            three_stars_rolled = rolled_card_rarities.count(3)
            four_stars_rolled = rolled_card_rarities.count(4)
            roll_info = {'user_id': user.id, 'user_name' : f'{user.name}#{user.discriminator}', 'two_stars': two_stars_rolled, 'three_stars': three_stars_rolled, 'four_stars': four_stars_rolled}
            for x in rolled_card_rarities:
                if x == 2:
                    random.shuffle(all_two_star_cards_paths)
                    cards_rolled_paths.append(str(all_two_star_cards_paths[0]))
                elif x == 3:
                    random.shuffle(all_three_star_cards_paths)
                    cards_rolled_paths.append(str(all_three_star_cards_paths[0]))
                else:
                    random.shuffle(all_four_star_cards_paths)
                    cards_rolled_paths.append(str(all_four_star_cards_paths[0]))
        
            first_half_cards_rolled = cards_rolled_paths[:len(cards_rolled_paths)//2]        
            second_half_cards_rolled = cards_rolled_paths[len(cards_rolled_paths)//2:]

            images = [Image.open(x) for x in cards_rolled_paths]
            widths, heights = zip(*(i.size for i in images))
            total_width = sum(widths) / 2
            max_height = 2 * max(heights)
            new_im = Image.new('RGBA', (int(total_width), max_height))
            first_half_icons = [Image.open(x) for x in first_half_cards_rolled]
            second_half_icons = [Image.open(x) for x in second_half_cards_rolled]
            x_offset = 0
            for im in first_half_icons:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]        
            x_offset = 0

            for im in second_half_icons:
                new_im.paste(im, (x_offset, 180))
                x_offset += im.size[0]        
                   
            # Update roll database
            roll_info['chara'] = {}
            roll_info['card_ids'] = {}
            # use sets instead of lists for the IDs since they're faster at updating and we don't need to insert duplicates
            roll_info['card_ids']['two_star_ids'] = []
            roll_info['card_ids']['three_star_ids'] = []
            roll_info['card_ids']['four_star_ids'] = []
            for card in cards_rolled_paths:
                search = re.search('icons/([a-zA-Z]*)\/([0-9]*)\/([0-9]*)', card)
                name = search[1]
                rarity = search[2]
                card_id = int(search[3])
                if rarity == '2':
                    roll_info['card_ids']['two_star_ids'].append(card_id) 
                elif rarity == '3':
                    roll_info['card_ids']['three_star_ids'].append(card_id) 
                else:
                    roll_info['card_ids']['four_star_ids'].append(card_id) 
                if name not in roll_info['chara']: 
                    roll_info['chara'][name] = {'2' : 0, '3': 0, '4': 0}
                    roll_info['chara'][name][rarity] += 1
                else:
                    roll_info['chara'][name][rarity] += 1
            
            title = "mbn getting a 4*" if four_stars_rolled > 0 else "haha no 4*"
            import uuid
            from discord import File
            file_name = str(ctx.message.author.id) + '_' + str(uuid.uuid4()) + '.png'
            saved_file_path = "data/img/rolls/" + file_name
            new_im.save(saved_file_path)
            discord_file = File(saved_file_path,filename=file_name)
            await update_rolls_db(roll_info)
            roll_stats = await get_roll_info(user.id)    
            two_star_count = roll_stats[0][1]
            three_star_count = roll_stats[0][2]
            four_star_count = roll_stats[0][3]
            total_count = two_star_count + three_star_count + four_star_count
            four_star_rate = f"{round(((four_star_count / total_count) * 100), 2)}%"
            icon =  f"{ctx.author.avatar_url.BASE}{ctx.author.avatar_url._url}"
            embed=discord.Embed(title=title,color=discord.Color.blue())
            embed.set_thumbnail(url=icon)
            embed.add_field(name='Total Cards Rolled',value="{:,}".format(total_count),inline=True)
            embed.add_field(name='Total 4* Rolled',
                            value=roll_stats[0][3], inline=True)
            embed.add_field(name='4* Rate', value=four_star_rate, inline=True)
            embed.add_field(name='2* Rolled',value=two_stars_rolled,inline=True)
            embed.add_field(name='3* Rolled',value=three_stars_rolled,inline=True)
            embed.add_field(name='4* Rolled',value=four_stars_rolled,inline=True) 
            embed.set_image(url=f"attachment://{file_name}")
            embed.set_footer(text="Want to see an album with all your 4 and 3*? Use the album command\nWant to see all your stats? Use the rollstats command\nWant to check the leaderboards? Use the rolllb command")
            await ctx.send(file=discord_file, embed=embed)
            os.remove(saved_file_path)
            await update_roll_album_db(roll_info)
        except FileNotFoundError:
            await ctx.send("Failed generating a roll. This is likely because the the name for whatever entered was incorrect")
        except IndexError:
            await ctx.send("Failed generating a roll. This is likely because the bot rolled a card that doesn't exist (e.g. 3* rokka)")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            #print(str(e))
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
    #@ctime
    async def lisaxodia(self, ctx):
        # Pubcord
        if ctx.message.guild.id != 432379300684103699:
            from discord import File
            SavedFile = "data/img/lisaxodia.png"
            DiscordFileObject = File(SavedFile)
            await ctx.send(file=DiscordFileObject)
        else:
            print('This command is disabled in this server.')
        
    @commands.command(name='picture',
                      aliases=['p'],
                      description='Note: THIS MAY RETURN NSFW IMAGES\n\nReturns an image (or images if multiple names/bands are entered) with > 100 bookmarks on Pixiv for the specified character/band/or defaults to Bang Dream tag and returns one random image from that list.',
                      help='For bands, the values below are valid, if an invalid value is entered, the command will fail\n\nRoselia\nAfterglow\nPopipa\nPasupare\nHHW\n\n.picture\n.picture lisa\n.p roselia arisa himari',
                      enabled=False)
    async def picture(self, ctx, *queries):
        await ctx.send('Command temporarily disabled until I have time to fix some of its issues.')
        # i really don't want to fix this since the pixiv api is such a pain in the ass to work with
        try:
            from commands.apiFunctions import GetBestdoriAllCharasAPI
            from discord import File
            import random, json       
            
            AllQueries = []
            CharaImageURLs = []
            if not queries:
                await ctx.send("Please enter a character's name to search")
                # AllQueries.append('????')
                # CharaImageURLs.append(
                #     'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/BanG_Dream%21_logo.svg/1200px-BanG_Dream%21_logo.svg.png')
            else:
                if queries[0] == 'yukilisa':
                    newquery = '????'
                    AllQueries.append('????')
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
                                AllQueries.append("????????????!")
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
                                    AllQueries.append("".join(charalist[1]))
                                    CharaImageURLs.append('https://bestdori.com/res/icon/chara_icon_%s.png' % charaId)
                for newquery, charaImageURL in zip(AllQueries, CharaImageURLs):
                    db = f'data/databases/tinydb/{newquery}.json'
                    with open(db, 'r') as file:
                        db = json.load(file)
                    pic = random.choice(db[newquery]['pics'])
                    PicID = pic['id']
                    PicURL = pic['image_urls']['large']
                    SavedPicPath = f'data/img/imgTmp/{PicID}_p0.jpg'
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
    #@ctime
    async def roll_leaderboards(self, ctx, *character):
        character = character[0] if character else ""
        try:
            from operator import itemgetter
            from tabulate import tabulate
            from commands.formatting.DatabaseFormatting import get_roll_leaderboards_info
            stats = await get_roll_leaderboards_info(character) if character else await get_roll_leaderboards_info()
            leaderboards = []
            for stat in stats:
                total_rolls = stat[1] + stat[2] + stat[3]
                four_star_rate =f"{round(((stat[3] / total_rolls) * 100), 2)}%"
                leaderboards.append([stat[5],"{:,}".format(total_rolls),"{:,}".format(stat[3]),four_star_rate])
            header = 'Total Cards Rolled' if not character else f"Total {character.capitalize()}s Rolled"
            output = "```" + tabulate(leaderboards,headers=['User',header,'Total 4*','4* %'],tablefmt='plain') + "```"
        except FileNotFoundError:
            output = 'No rolls have been generated for that character yet'
        except Exception as e:
            output = 'Failed getting the roll leaderboards. Please use the `notify` command if this keeps happening'
        await ctx.send(output)        
        
    @commands.command(name='birthdays',
                      aliases=['bdays','bday'],
                      description="Note: This data may be publicly accessible\n\nIf you're like me and easily forget birthdays, you can use this command to add birthday entries and grab them as needed. Entries are server specific",
                      help='.birthdays (this returns all birthdays for the server the command was ran in\n.bdays add Aug 25 (adds an entry to the list for the user running the command\n.bdays del (removes the user running the command from the database)' )
    #@ctime
    async def bdays(self,ctx,*add):
        if add and add[0] == 'add':
            Name = ctx.message.author.name + '#' + ctx.message.author.discriminator
            ServerID = ctx.message.guild.id
            Date = add[1].capitalize() + ' ' + add[2]
            try:
                self.UpdateBirthdaysJSON(ServerID, Name, Date, False)
                output = f"Successfully added user `{Name}` to the birthdays list with date `{Date}`"
            except:
                output = "Failed adding user to the birthdays list. Please use the `notify` command if this keeps happening"
        elif add and add[0] == 'del':
            Name = ctx.message.author.name + '#' + ctx.message.author.discriminator
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
            FileName = 'data/databases/tinydb/birthdays.json'
            with open(FileName) as file:
                api = json.load(file)
            entries = []
            OrderedDates = api[str(ctx.message.guild.id)]
            OrderedDates = ({k:v for k, v in sorted(OrderedDates.items(), key = lambda x : datetime.strptime(x[1]['Date'], "%B %d"))})
            for key in OrderedDates:
                entries.append([key,api[str(ctx.message.guild.id)][key]['Date']])
            output = "```" + tabulate(entries,headers=['Name','Date'],tablefmt='plain') + "```"
        await ctx.send(output)
      
    #@ctime    
    def UpdateBirthdaysJSON(self, Server, User, Date, Delete: bool = False):
        import json
        FileName = 'data/databases/tinydb/birthdays.json'
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

#@ctime
async def UpdateCardIcons():
    from commands.apiFunctions import get_bestdori_all_cards_api5, GetBestdoriAllCharactersAPI2        
    from PIL import Image
    from PIL.ImageDraw import Draw
    from PIL.ImageFont import truetype
    from io import BytesIO
    from os import path
    CardAPI = await get_bestdori_all_cards_api5()
    CharaAPI = await GetBestdoriAllCharactersAPI2()
    for x in CardAPI:
        try:
            print(f'Card {x}')
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
            Type = CardAPI[x]['type']
            BaseIconsPath = f"data/img/icons/base_icons/{x}.png"
            FullIconsPath  = f"data/img/icons/full_icons/{x}.png"
            GachaIconsPath = f"data/img/icons/{CharaName}/{Rarity}/{x}.png"
            GachaTypes = ['limited','permanent','birthday']
            # DO THE GACHA ICONS IN THIS LOGIC TOO IF RARITY > 1
            if not path.exists(FullIconsPath):
                URLList = []
                if Type != 'birthday':
                    UntrainedCardURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_normal.png' 
                    URLList.append(UntrainedCardURL)
                    if int(Rarity) > 2:
                        TrainedCardURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_after_training.png'
                        URLList.append(TrainedCardURL)
                else:
                    UntrainedCardURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_after_training.png' 
                    URLList.append(UntrainedCardURL)
                    TrainedCardURL = f'https://bestdori.com/assets/jp/thumb/chara/card000{Folder}_rip/{ResourceSetName}_after_training.png'
                    URLList.append(TrainedCardURL)
                for url in URLList:
                    if path.exists(FullIconsPath):
                        FullIconsPath = f"data/img/icons/full_icons/{x}_trained.png"
                        BaseIconsPath = f"data/img/icons/base_icons/{x}_trained.png"
                    image = requests.get(url)
                    try:
                        image = Image.open(BytesIO(image.content))
                        im.paste(image)
                        im.save(BaseIconsPath)
                        if Rarity == '1':
                            rarityPng = "data/img/2star.png"
                            starPng = "data/img/star1.png"
                        elif Rarity == '2':
                            rarityPng = "data/img/2star.png"
                            starPng = "data/img/star2.png"
                        elif Rarity == '3':
                            rarityPng = "data/img/3star.png"
                            starPng = "data/img/star3.png"
                        else:
                            rarityPng = "data/img/4star.png"
                            starPng = "data/img/star4.png"
                        rarityBg = Image.open(rarityPng)
                        starBg = Image.open(starPng)
                        if Rarity == '1':
                            im.paste(starBg, (5,20), mask=starBg)
                        else:
                            im.paste(starBg, (5,50), mask=starBg)
                        im.paste(rarityBg, mask=rarityBg)
                    
                        if Attribute == 'powerful':
                            attrPng = "data/img/power2.png"
                        elif Attribute == 'cool':
                            attrPng = "data/img/cool2.png"
                        elif Attribute == 'pure':
                            attrPng = "data/img/pure2.png"
                        else:
                            attrPng = "data/img/happy2.png"
                        attrBg = Image.open(attrPng)
                        im.paste(attrBg, (132, 2), mask=attrBg)
                        
                        bandPng = f"data/img/band_{BandID}.png"
                        bandBg = Image.open(bandPng)
                        im.paste(bandBg, (1, 2), mask=bandBg)
                        # The last URL in the list will always be the trained card which isn't needed for the gacha cards
                        if Type in GachaTypes:
                            if not path.exists(GachaIconsPath):
                                if int(Rarity) == 2:
                                    im.save(GachaIconsPath)
                                elif int(Rarity) > 2:
                                    if Type == 'birthday':
                                        im.save(GachaIconsPath)
                                    elif url != URLList[-1]:
                                        im.save(GachaIconsPath)
                        im.save(FullIconsPath)
                    except:
                        print(f"Failed adding card with ID {x}")
            
                        pass
        except:
            print(f"Failed adding card with ID {x}")
            pass

def setup(bot):
    bot.add_cog(Fun(bot))
