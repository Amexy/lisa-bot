from datetime import timedelta, datetime
from commands.formatting.T10Commands import t10formatting, t10membersformatting
from commands.formatting.EventCommands import GetCurrentEventID, GetCutoffFormatting, GetEventName
from commands.formatting.GameCommands import GetEventTimeLeftSeconds
from commands.formatting.DatabaseFormatting import getChannelsToPost, removeChannelFromDatabase, updatesDB, getNewsChannelsToPost, getCutoffChannels, rmChannelFromCutoffDatabase, removeChannelFromDatabaseSongs
from commands.apiFunctions import GetBestdoriCutoffAPI
from discord.ext import commands
from tabulate import tabulate
from pytz import timezone
from jsondiff import diff
import asyncio, json, requests, discord

class Loops(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        with open("config.json") as file:
            config_json = json.load(file)
            loops_enabled = config_json['loops_enabled']
        self.initialENT100Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=1&event=87&tier=0').json()
        self.initialENT1000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=1&event=87&tier=1').json()
        self.initialENT2500Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=1&event=87&tier=2').json()        
        self.initialJPT100Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=0&event=123&tier=0').json()
        self.initialJPT1000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=0&event=123&tier=1').json()
        self.initialJPT2000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=0&event=123&tier=2').json()
        self.initialJPT5000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=0&event=123&tier=3').json()
        self.initialJPT10000Cutoffs = requests.get('https://bestdori.com/api/tracker/data?server=0&event=123&tier=4').json()
        self.initialCardsAPI = requests.get('https://bestdori.com/api/cards/all.5.json').json()
        self.firstAPI = requests.get('https://bestdori.com/api/news/all.5.json').json()
        self.ENCutoffs = {100: self.initialENT100Cutoffs, 1000: self.initialENT1000Cutoffs, 2500: self.initialENT2500Cutoffs}
        self.JPCutoffs = {100: self.initialJPT100Cutoffs, 1000: self.initialJPT1000Cutoffs, 2000: self.initialJPT2000Cutoffs, 5000: self.initialJPT5000Cutoffs, 10000: self.initialJPT10000Cutoffs}
        if loops_enabled == 'true':
            self.StartLoops()            
        else:
            print('Not loading loops')
        print('Successfully loaded Loops cog')
        
    async def UpdateAvatar(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            from os import listdir
            import os, random
            path = "data/img/pfps/"
            files = []
            for file in os.listdir(path):
                files.append('data/img/pfps/' + file)
            pic = random.choice(files)
            try:
                with open(pic, 'rb') as f:
                    await self.bot.user.edit(avatar=f.read())
            except:
                print('Failed updating avatar.')
            await asyncio.sleep(1200)
            
    def StartLoops(self):
        #self.bot.loop.create_task(self.PostYukiLisa())
        self.bot.loop.create_task(self.post_t10_updates('en', 2))
        self.bot.loop.create_task(self.post_t10_updates('en', 3600))
        self.bot.loop.create_task(self.post_t10_updates('jp', 2))
        self.bot.loop.create_task(self.post_t10_updates('jp', 3600))
        self.bot.loop.create_task(self.postSongUpdates1min())
        self.bot.loop.create_task(self.postEventNotif('en'))
        self.bot.loop.create_task(self.postEventNotif('jp'))
        self.bot.loop.create_task(self.postBestdoriNews())
        self.bot.loop.create_task(self.UpdateAvatar())
        self.bot.loop.create_task(self.UpdateCardIcons())
        self.bot.loop.create_task(self.postCutoffUpdates())

    async def UpdateCardIcons(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            from commands.apiFunctions import get_bestdori_all_cards_api5
            initialCardsAPI = self.initialCardsAPI
            CardsAPI = await get_bestdori_all_cards_api5()
            if(sorted(initialCardsAPI.items()) != sorted(CardsAPI.items())):
                from commands.cogs.Fun import UpdateCardIcons
                await UpdateCardIcons
                self.initialCardsAPI = CardsAPI
            await asyncio.sleep(300)
            
    # This was for NR1 server, but I'll leave it for now incase I feel like reusing it
    async def PostYukiLisa(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            import os, random
            from discord import File
            newquery = 'リサゆき'
            CharaImageURLs = ('https://bestdori.com/res/icon/chara_icon_23.png')
            charaId = '23'
            db = f'databases/{newquery}.json'
            with open(db, 'r') as file:
                db = json.load(file)
            pic = random.choice(db[newquery]['pics'])
            PicID = pic['id']
            PicURL = pic['image_urls']['large']
            if charaId == '23':
                SaveImage = True
                SavedPicPath = f'data/img/pfps/{PicID}_p0.jpg'
            else:
                SaveImage = False
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
            
            if SaveImage:
                from PIL import Image
                # Since the original image is saved as corrupt, save it this way
                SavedPFP = Image.open(SavedPicPath)
                SavedPFP.save(SavedPicPath)

            channel: discord.TextChannel = self.bot.get_channel(712732064381927515)  # Change this channel to the channel you want the bot to send images to so it can grab a URL for the embed
            fileSend: discord.Message = await channel.send(file=DiscordFileObject)

            TitleURL = f"https://www.pixiv.net/en/artworks/{PicID}"


            embed=discord.Embed(title=pic['title'],url=TitleURL,color=discord.Color.blue())
            embed.set_thumbnail(url=CharaImageURLs)
            embed.set_image(url=fileSend.attachments[0].url)
            embed.add_field(name='Artist',value=pic['user']['name'],inline=True)
            embed.add_field(name='Date',value=pic['create_date'],inline=True)
            channel = self.bot.get_channel(523339468229312555)
            await channel.send(embed=embed)
            await asyncio.sleep(180)

    async def post_t10_updates(self, server: str, interval: int):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                event_id = await GetCurrentEventID(server)
            except Exception as e:
                print(f'Failed posting {interval} minute data for {server}.\nException: ' + {e})            
            if event_id:
                time_left = await GetEventTimeLeftSeconds(server, event_id)
                if(time_left > 0):
                    message = await t10formatting(server, event_id, True)
                    ids = getChannelsToPost(interval, server)
                    for i in ids:
                        channel = self.bot.get_channel(i)
                        if channel != None:
                            try:
                                await channel.send(message)
                            except (commands.BotMissingPermissions, discord.errors.NotFound, discord.errors.Forbidden): 
                                LoopRemovalUpdates = self.bot.get_channel(523339468229312555)
                                await LoopRemovalUpdates.send(f'Removing {interval} updates from channel: {channel.name} in server: {channel.guild.name}')
                                removeChannelFromDatabase(channel, interval, server)
            timeStart = datetime.now()
            if interval == 2:
                if (timeStart.minute % 2) != 0: 
                    timeFinish = (timeStart + timedelta(minutes=1)).replace(second=0, microsecond=0).timestamp()
                else:
                    timeFinish = (timeStart + timedelta(minutes=2)).replace(second=0, microsecond=0).timestamp()
            else:
                timeFinish = (timeStart + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).timestamp()
            timeStart = timeStart.timestamp()
            await asyncio.sleep(timeFinish - timeStart)
                            
    async def postSongUpdates1min(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                EnEventID = await GetCurrentEventID('en')
            except Exception as e:
                print('Failed posting 1 minute song data. Exception: ' + str(e))            
            if EnEventID:
                timeLeft = await GetEventTimeLeftSeconds('en', EnEventID)
                if(timeLeft > 0):
                    message = await t10membersformatting('en', EnEventID, True, 158699060893581313)
                    if message != "This event doesn't have a song ranking.":
                        #await t10logging('en', eventid, True)
                        ids = getChannelsToPost(1, 'en')
                        for i in ids:
                            channel = self.bot.get_channel(i)
                            if channel != None:
                                try:
                                    for x in message:
                                        await channel.send(x)
                                except (commands.BotMissingPermissions, discord.errors.NotFound, discord.errors.Forbidden): 
                                    LoopRemovalUpdates = self.bot.get_channel(523339468229312555)
                                    await LoopRemovalUpdates.send('Removing 1 minute updates from channel: ' + str(channel.name) + " in server: " + str(channel.guild.name))
                                    removeChannelFromDatabaseSongs(channel)
            timeStart = datetime.now()
            timeFinish = (timeStart + timedelta(minutes=1)).replace(second=0, microsecond=0).timestamp()
            timeStart = timeStart.timestamp()
            await asyncio.sleep(timeFinish - timeStart)

    async def CutoffUpdatesFormatting(self, server: str, tier):
        UpdateCheck = False
        CurrentCutoffs = await GetBestdoriCutoffAPI(server, tier)
        if server == 'en':
            CachedCutoffs = self.ENCutoffs
        else:
            CachedCutoffs = self.JPCutoffs
        if sorted(CurrentCutoffs.items()) != sorted(CachedCutoffs[tier].items()):
            output = await GetCutoffFormatting(server, tier, False)
            ids = getCutoffChannels(tier, server)
            for i in ids:
                channel = self.bot.get_channel(i)
                if channel != None:
                    try:
                        await channel.send(f't{tier} update found!')
                        await channel.send(embed=output)
                        UpdateCheck = True                                
                    except (commands.BotMissingPermissions, discord.errors.NotFound): 
                        rmChannelFromCutoffDatabase(channel, tier, 'en')
        return UpdateCheck, CurrentCutoffs

    async def postCutoffUpdates(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                ENEventID = await GetCurrentEventID('en')
                JPEventID = await GetCurrentEventID('jp')
            except Exception as e:
                print('Error getting current event ids. Exception: ' + str(e))      
            if ENEventID:
                timeLeft = await GetEventTimeLeftSeconds('en', ENEventID)
                if(timeLeft > 0):
                    for tier in self.ENCutoffs:
                        UpdateCheck = await self.CutoffUpdatesFormatting('en', tier)
                        if UpdateCheck:
                            self.ENCutoffs[tier] = UpdateCheck[1]
            if JPEventID:
                timeLeft = await GetEventTimeLeftSeconds('jp', JPEventID)
                if(timeLeft > 0):
                    for tier in self.JPCutoffs:
                        UpdateCheck = await self.CutoffUpdatesFormatting('jp', tier)
                        if UpdateCheck:
                            self.JPCutoffs[tier] = UpdateCheck[1]
            await asyncio.sleep(120)
    
    # async def postT100CutoffUpdates(self):
    #     await self.bot.wait_until_ready()
    #     while not self.bot.is_closed():
    #         try:
    #             EventID = await GetCurrentEventID('en')
    #         except Exception as e:
    #             print('Failed posting t100 update. Exception: ' + str(e))            
    #         if EventID:
    #             timeLeft = await GetEventTimeLeftSeconds('en', EventID)
    #             if(timeLeft > 0):
    #                 ids = getCutoffChannels(100)
    #                 initialT100Cutoffs = self.initialT100Cutoffs
    #                 cutoffAPI = await GetBestdoriCutoffAPI('en', 100)
    #                 if(sorted(initialT100Cutoffs.items()) != sorted(cutoffAPI.items())):
    #                     output = await GetCutoffFormatting('en', 100, False)
    #                     ids = getCutoffChannels(100)
    #                     for i in ids:
    #                         channel = self.bot.get_channel(i)
    #                         if channel != None:
    #                             try:
    #                                 await channel.send('t100 update found!')
    #                                 await channel.send(embed=output)                                
    #                             except (commands.BotMissingPermissions, discord.errors.NotFound): 
    #                                 LoopRemovalUpdates = self.bot.get_channel(523339468229312555)
    #                                 await LoopRemovalUpdates.send('Removing t100 updates from channel: ' + str(channel.name) + " in server: " + str(channel.guild.name))
    #                                 rmChannelFromCutoffDatabase(channel, 100)
    #                     self.initialT100Cutoffs = cutoffAPI
    #             await asyncio.sleep(60)

    # async def postT1000CutoffUpdates(self):
    #     await self.bot.wait_until_ready()
    #     while not self.bot.is_closed():
    #         try:
    #             EventID = await GetCurrentEventID('en')
    #         except Exception as e:
    #             print('Failed posting t1000 update. Exception: ' + str(e))   
    #         if EventID:
    #             timeLeft = await GetEventTimeLeftSeconds('en', EventID)
    #             if(timeLeft > 0):
    #                 ids = getCutoffChannels(1000)
    #                 initialT1000Cutoffs = self.initialT1000Cutoffs  
    #                 cutoffAPI = await GetBestdoriCutoffAPI('en', 1000)
    #                 if(sorted(initialT1000Cutoffs.items()) != sorted(cutoffAPI.items())):
    #                     output = await GetCutoffFormatting('en', 1000, False)
    #                     ids = getCutoffChannels(1000)
    #                     for i in ids:
    #                         channel = self.bot.get_channel(i)
    #                         if channel != None:
    #                             try:
    #                                 await channel.send('t1000 update found!')
    #                                 await channel.send(embed=output)                                
    #                             except (commands.BotMissingPermissions, discord.errors.NotFound): 
    #                                 LoopRemovalUpdates = self.bot.get_channel(523339468229312555)
    #                                 await LoopRemovalUpdates.send('Removing t1000 updates from channel: ' + str(channel.name) + " in server: " + str(channel.guild.name))
    #                                 rmChannelFromCutoffDatabase(channel, 1000)
    #                     self.initialT1000Cutoffs = cutoffAPI
    #             await asyncio.sleep(60)
                
    # async def postT2500CutoffUpdates(self):
    #     await self.bot.wait_until_ready()
    #     while not self.bot.is_closed():
    #         try:
    #             EventID = await GetCurrentEventID('en')
    #         except Exception as e:
    #             print('Failed posting t2500 update. Exception: ' + str(e))   
    #         if EventID:
    #             timeLeft = await GetEventTimeLeftSeconds('en', EventID)
    #             if(timeLeft > 0):
    #                 ids = getCutoffChannels(2500)
    #                 initialT2500Cutoffs = self.initialT2500Cutoffs  
    #                 cutoffAPI = await GetBestdoriCutoffAPI('en', 2500)
    #                 if(sorted(initialT2500Cutoffs.items()) != sorted(cutoffAPI.items())):
    #                     output = await GetCutoffFormatting('en', 2500, False)
    #                     ids = getCutoffChannels(2500)
    #                     for i in ids:
    #                         channel = self.bot.get_channel(i)
    #                         if channel != None:
    #                             try:
    #                                 await channel.send('t2500 update found!')
    #                                 await channel.send(embed=output)                                
    #                             except (commands.BotMissingPermissions, discord.errors.NotFound): 
    #                                 LoopRemovalUpdates = self.bot.get_channel(523339468229312555)
    #                                 await LoopRemovalUpdates.send('Removing t2500 updates from channel: ' + str(channel.name) + " in server: " + str(channel.guild.name))
    #                                 rmChannelFromCutoffDatabase(channel, 2500)
    #                     self.initialT2500Cutoffs = cutoffAPI
    #             await asyncio.sleep(60)

    async def postBestdoriNews(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            firstAPI = self.firstAPI
            updatedAPI = requests.get('https://bestdori.com/api/news/all.5.json').json()
            embed=discord.Embed(color=0x09d9fd)
            if(sorted(firstAPI.items()) != sorted(updatedAPI.items())):
                fmt = "%Y-%m-%d %H:%M:%S %Z%z"
                now_time = datetime.now(timezone('US/Eastern'))
                
                jsonDif = diff(firstAPI,updatedAPI)
                for x in jsonDif:
                    if "Patch Note" in jsonDif[x]['tags']:
                        if "EN" in jsonDif[x]['tags']:
                            ids = getNewsChannelsToPost('en')
                        elif "JP" in jsonDif[x]['tags']:
                            ids = getNewsChannelsToPost('jp')
                        elif "CN" in jsonDif[x]['tags']:
                            ids = getNewsChannelsToPost('cn')
                        
                        #post to channels that want all server patch updates as well
                        allids = getNewsChannelsToPost('all')
                        server = jsonDif[x]['tags'][2]
                        embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1126155698117562368/mW6W89Gg_200x200.png')
                        embed.add_field(name='New %s Patch Note Available!' % server.upper(), value='https://bestdori.com/home/news/' + str(x), inline=False)
                        embed.set_footer(text=now_time.strftime(fmt))               
                        for i in ids:
                            channel = self.bot.get_channel(i)
                            if channel != None:
                                await channel.send(embed=embed)
                        for i in allids:
                            channel = self.bot.get_channel(i)
                            if channel != None:
                                await channel.send(embed=embed)

                        embed=discord.Embed(color=0x09d9fd)
                self.firstAPI = updatedAPI
            await asyncio.sleep(300)

    async def sendEventUpdates(self, message: str, server: str):
        ids = updatesDB(server)
        if(message):
            for i in ids:
                channel = self.bot.get_channel(i)
                if channel != None:
                    await channel.send(message)

    async def postEventNotif(self, server: str):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
            from commands.formatting.EventCommands import GetCurrentEventID, IsEventActive, GetEventName
            from commands.formatting.TimeCommands import GetEventStartTime
            import aiohttp
            EventID = await GetCurrentEventID(server)
            try:
                if not await IsEventActive(server, EventID):
                    EventID = int(EventID) + 1                   
                    EventName = await GetEventName(server, EventID)
                    import time
                    CurrentTime = time.time() * 1000
                    TimeTilNextEventStarts = (int(await GetEventStartTime(server, int(EventID)) - CurrentTime ))/ 1000
                    if TimeTilNextEventStarts > 86400:
                        await asyncio.sleep(TimeTilNextEventStarts - 86400)
                        Message = f"{EventName} on `{server.upper()}` begins in 1 day!"
                        await self.sendEventUpdates(Message, server)               
                    elif TimeTilNextEventStarts > 3600:
                        await asyncio.sleep(TimeTilNextEventStarts - 3600)
                        Message = f"{EventName} on `{server.upper()}` begins in 1 hour!"
                        await self.sendEventUpdates(Message, server)
                    else:
                        await asyncio.sleep(TimeTilNextEventStarts)
                        Message = f"{EventName} on `{server.upper()}` has begun!"
                        await self.sendEventUpdates(Message, server)
                else:
                    EventName = await GetEventName(server, EventID)
                    TimeLeftSeconds = await GetEventTimeLeftSeconds(server, EventID)
                    if TimeLeftSeconds > 86400:
                        await asyncio.sleep(TimeLeftSeconds - 86400)
                        Message = f"{EventName} on `{server.upper()}` ends in 1 day!"
                        await self.sendEventUpdates(Message, server)
                    elif TimeLeftSeconds > 3600:
                        await asyncio.sleep(TimeLeftSeconds - 3600)
                        Message = f"{EventName} on `{server.upper()}` ends in 1 hour!"
                        await self.sendEventUpdates(Message, server)
                    else:
                        await asyncio.sleep(TimeLeftSeconds)
                        Message = f"{EventName} on `{server.upper()}` has ended!"
                        from tinydb import TinyDB, Query, where
                        q = Query()
                        guilds_db = TinyDB('databases/premium_users.json')
                        guilds = guilds_db.search(q.event_id == EventID and q.server == server)
                        if guilds:
                            if server == 'en':
                                two_min_db = 'databases/eventCheckDb2min.json' 
                            elif server == 'jp':
                                two_min_db = 'databases/jp2MinuteTrackingDB.json'
                            if two_min_db:
                                db = TinyDB(two_min_db)
                                for guild in guilds:
                                    db.remove((where('guild') == guild['guild']))
                        await self.sendEventUpdates(Message, server)
                        await asyncio.sleep(60)
            except aiohttp.client_exceptions.ContentTypeError: # This will typically happen on JP since Bestdori doesn't always have the next event's information available until ~24 hours before event start
                await asyncio.sleep(60)
def setup(bot):
    bot.add_cog(Loops(bot))
