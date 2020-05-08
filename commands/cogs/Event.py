from discord.ext import commands
from commands.formatting.GameCommands import GetCoastingOutput
from commands.formatting.EventCommands import GetCutoffFormatting, GetCurrentEventID
from commands.formatting.T10Commands import t10formatting, t10songsformatting, t10membersformatting, GetT10ArchiveFile
from commands.formatting.TimeCommands import GetTimeLeftCommandOutput, GetEventProgress
from commands.apiFunctions import GetBestdoriAllEventsAPI, GetBestdoriBannersAPI, GetBestdoriPlayerLeaderboardsAPI
from protodefs.ranks import t10ranks
from startup.login import enICEObject, jpICEObject
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from pytz import timezone
from tabulate import tabulate
import asyncio
import discord
import json
import selenium

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ValidT10Servers = ['en','jp']

        with open("config.json") as file:
            config_json = json.load(file)
            load_t10events = config_json["load_t10events"]
        if load_t10events == 'true':
            print("Loading valid T10 Events")
            self.ValidT10EventsEN = asyncio.run(self.GetT10Events('en'))
            self.ValidT10EventsJP = asyncio.run(self.GetT10Events('jp'))
        else:
            print("Not loading Valid T10 Events")

    async def GetT10Events(self, server):
        from commands.apiFunctions import GetBestdoriAllEventsAPI
        from protodefs.ranks import t10ranks
        api = await GetBestdoriAllEventsAPI()
        print(f'Grabbing events for {server}')
        ValidEvents = []
        if server == 'en':
            ice = enICEObject
        else:
            ice = jpICEObject
        for x in range(1, (len(api) + 1)):
            ret = await t10ranks(ice, server, x)
            if ret.top_10.contents:
                print(f'Adding {x}')
                ValidEvents.append(x)
        return ValidEvents


    @commands.command(name='t10events',
                    aliases=['t10e'],
                    help='Returns a list of events that can be checked for T10 data\n\nExamples:\n\n.t10events\n.t10e jp')
    async def t10events(self, ctx, server: str = 'en'):
        if server.lower() not in self.ValidT10Servers:
            await ctx.send("Only EN and JP can be checked for T10 data")
        else:
            if server.lower() == 'en':
                ValidT10Events = self.ValidT10EventsEN
            if server.lower() == 'jp':
                ValidT10Events = self.ValidT10EventsJP
            if ValidT10Events: # In case the function isn't ran at startup
                await ctx.send(f'Valid t10 events for `{server}` are: {str(ValidT10Events)[1:-1]}')
            else:
                await ctx.send('Error loading valid t10 events. Use the `notify` command to let Josh know')
    @commands.command(name='t10archives',
                aliases=["t10a"],
                help="Attaches a txt file (if found) containing 2 minute t10 updates for the specified event and server\n\nExamples:\n\n.t10a 76 (this defaults to en)\n.t10a 112 jp")
    async def t10archives(self, ctx, eventid: str, server: str = 'en'):
        if not eventid.isnumeric():
            raise commands.errors.BadArgument
        try:
            if server not in self.ValidT10Servers:
                await ctx.send('This function only works for the `EN` and `JP` servers')
            else:
                FileToAttach = await GetT10ArchiveFile(int(eventid), server)
                if FileToAttach:
                    await ctx.send('File found, uploading..')
                    await ctx.send(file=FileToAttach)
                else:
                    await ctx.send("No file found for the specified event.")

        except Exception as e:
            print(str(e))
            await ctx.send("No file found for the specified event.")

    @commands.command(name='t10',
                brief="t10 info",
                help="Provides current or specified event t10 info. Can look on a per event/server level, you can also include the songs parameter to look at song info (CL or VS only). However, a lot of the old data has been made inacessible or deleted so the bot may throw an error when checking. You can find the eventIds for any event by going to https://bestdori.com/info/events\n\nExamples\n\n.t10 en\n.t10 en 30\n.t10 jp 78 songs")
    async def t10(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.ValidT10Servers:
                await ctx.send('This function only works for the `EN` and `JP` servers')
            else:
                try:
                    server = server.lower()
                    if(eventid == 0):
                        eventid = await GetCurrentEventID(server)
                    else:
                        eventid = eventid
                    if(songs):
                        output = await t10songsformatting(server, eventid, False)
                        output = ''.join(output)
                    else:
                        output = await t10formatting(server, eventid, False)
                    await ctx.send(output)
                except:
                    await ctx.send(f"Failed getting data for event with ID `{eventid}` on the `{server}` server. Please use the `.notify` command to let Josh know")

    @commands.command(name='t10ids',
                aliases=['t10i'],
                brief="t10 info with user ids",
                help="Provides current or specified event t10 info. Can look on a per event/server level, you can also include the songs parameter to look at song info (CL or VS only). However, a lot of the old data has been made inacessible or deleted so the bot may throw an error when checking. You can find the eventIds for any event by going to https://bestdori.com/info/events\n\nExamples\n\n.t10ids en\n.t10ids en 30\n.t10ids jp 78 songs")
    async def t10ids(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.ValidT10Servers:
                await ctx.send('This function only works for the `EN` and `JP` servers')
            else:
                try:
                    if(eventid == 0):
                        eventid = await GetCurrentEventID(server)
                    else:
                        eventid = eventid
                    if(songs):
                        output = await t10songsformatting(server, eventid, True)
                        output = ''.join(output)
                    else:
                        output = await t10formatting(server, eventid, True)
                    await ctx.send(output)
                except:
                    await ctx.send(f"Failed getting data for event with ID `{eventid}` on the `{server}` server. Please use the `.notify` command to let Josh know")

    @commands.command(name='t10members',
                aliases=['t10m'],
                help="Aliases: t10m\n\nPosts t10 info with each player's team in their profile along with skill level for each member",
                brief='t10 info with member info ')
    async def t10members(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.ValidT10Servers:
                await ctx.send('This function only works for the `EN` and `JP` servers')
            else:
                try:
                    if(eventid == 0):
                        eventid = await GetCurrentEventID(server)
                    else:
                        eventid = eventid
                    if(songs):
                        output = await t10membersformatting(server, eventid, True)
                        if 'No data found for event' in output: # Very scuffed way of doing this, but I don't feel like messing with errors (if that'd even work)
                            await ctx.send(output)
                        else:
                            #doing this because on a CL, the output is very likely >2000 characters bypassing discord's limit
                            for x in output:
                                await ctx.send(x)
                    else:
                        output = await t10membersformatting(server, eventid, False)
                        await ctx.send(output)
                except:
                    await ctx.send(f"Failed getting data for event with ID `{eventid}` on the `{server}` server. Please use the `.notify` command to let Josh know")

    @commands.command(name='timeleft',
            aliases=['tl'],
                description="Provides the amount of time left (in hours) for an event",
                brief="Time Left",
                help="Specify EN or JP")
    async def timeLeftBotCommand(self, ctx, server: str = 'en'):
        EventID = await GetCurrentEventID(server)
        if EventID:
            timeLeftBotOutput = await GetTimeLeftCommandOutput(server, EventID)
            if isinstance(timeLeftBotOutput, str):
                await ctx.send(timeLeftBotOutput)
            else:
                await ctx.send(embed=timeLeftBotOutput)
        else:
            await ctx.send("The %s event hasn't started yet." %server)

    @commands.command(name='coasting',
                description="Given an input of server, ep gained per song, and beginning EP, the bot provides how much EP you'll have at the end of the event if you natural flame for the rest of the event",
                brief="EP at end of event via only natural flames")
    async def coasting(self, ctx, server: str, epPerSong: int, currentEP: int):
        ValidServers = ['en','jp','cn','tw','kr']
        if server.lower() not in ValidServers:
            await ctx.send('Please enter a valid server from one of the following: ' + str(ValidServers)[1:-1])
        else:
            coastingTable = await GetCoastingOutput(server.lower(), epPerSong, currentEP)
            await ctx.send(coastingTable)


        
        
        

    #######################
    #    Cutoff Command   #
    #######################
    
    #open website

    @commands.command(name='refresh',
                       aliases=['r'],
                       hidden=True)
    async def refresh(self, ctx, server: str = 'en'):
        try:
            if server == 'en':
                driver = self.enDriver
            elif server == 'jp':
                driver = self.jpDriver
            elif server == 'cn':
                driver = self.cnDriver
            else:
                driver = self.twkrDriver
            driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/a').click()
        except:
            await ctx.send('Failed refreshing the event tracker page for %s.' %(server))        
    

        
    @commands.command(name='cutoff',
                     aliases=['t100','t1000','t2000'],
                     brief="Cutoff estimate for t10, t100, t1000, and t2000",
                     help="Cutoff estimate for t10, t100, t1000, and t2000. Pass the tier you want and server (defaulted to en)\n\nCurrently using https://bestdori.com/tool/eventtracker/, all credit goes to Burrito\n\nExamples\n\n.cutoff 100\n.cutoff 1000 en\n.cutoff 2000 jp")
    async def cutoff(self, ctx, tier: int = 100, server: str = 'en'):
        from startup.OpenWebdrivers import enDriver, jpDriver, cnDriver, twkrDriver
        ValidTiers = [100,1000,2000]
        if tier not in ValidTiers:
            await ctx.send(f"{tier} isn't supported")
        else:
            server = server.lower()
            ValidT2000 = ['jp','cn']
            ValidT1000 = ['en','jp','cn']
            ValidT10 = ['en','jp']
            output = ''
            ctx.invoked_with = ctx.invoked_with.lower()
            if 't1000' in ctx.invoked_with:
                tier = 1000
            elif 't100' in ctx.invoked_with:
                tier = 100
            elif 't2000' in ctx.invoked_with:
                tier = 2000
            if tier == 10 and server not in ValidT10:
                output = 'T10 is only valid for EN and JP'
            if tier == 2000 and server not in ValidT2000:
                output = 'T2000 is only valid for JP and CN'
            if tier == 1000 and server not in ValidT1000:
                output = 'T1000 is only valid for EN, JP, and CN'
            if output:
                await ctx.send(output)
            else:
                if server == 'en':
                    driver = enDriver
                elif server == 'jp':
                    driver = jpDriver
                elif server == 'cn':
                    driver = cnDriver 
                else:
                    driver = twkrDriver
                try:
                    output = await GetCutoffFormatting(driver, server, tier)
                    await ctx.send(embed=output)
                except selenium.common.exceptions.ElementNotInteractableException:
                    await ctx.send("Failed getting cutoff data because Chrome likely crashed. Please wait a few seconds and run the command again")
                    from startup.OpenWebdrivers import LoadWebDrivers
                    LoadWebDrivers(server)
                except selenium.common.exceptions.WebDriverException:
                    await ctx.send("Failed getting cutoff data because Chrome likely crashed. Please wait a few seconds and run the command again")
                    from startup.OpenWebdrivers import LoadWebDrivers
                    LoadWebDrivers(server)
                except IndexError:
                    await ctx.send('Failed getting cutoff data, there is likely no data available yet on Bestdori')

    @coasting.error
    async def coasting_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`. Required arguments are enclosed in < >")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help coasting`")

    @timeLeftBotCommand.error 
    async def timeleft_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'server':
                await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
    @t10.error 
    async def t10_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'server':
                await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help t10`")
    @t10ids.error 
    async def t10ids_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help t10ids`")
    @t10members.error 
    async def t10members_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'server':
                await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help t10members`")
    @t10archives.error 
    async def t10archives_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument, please check argument positioning using `.help t10archives`")
    @cutoff.error
    async def cutoff_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Invalid argument, please check valid arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("Failed getting cutoff data. Please use the `.notify` command to let Josh know. Old events cutoff data can been seen using the `event` command")

def setup(bot):
    bot.add_cog(Event(bot))