from discord.ext import commands
from commands.formatting.GameCommands import GetCoastingOutput
from commands.formatting.EventCommands import GetCutoffFormatting, GetCurrentEventID
from commands.formatting.T10Commands import t10formatting, t10songsformatting, t10membersformatting
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

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name='t10',
                brief="t10 info",
                help="Provides current or specified event t10 info. Can look on a per event/server level, you can also include the songs parameter to look at song info (CL or VS only). However, a lot of the old data has been made inacessible or deleted so the bot may throw an error when checking. You can find the eventIds for any event by going to https://bestdori.com/info/events\n\nExamples\n\n.t10 en\n.t10 en 30\n.t10 jp 78 songs")
    async def t10(self, ctx, server: str = 'en', eventid: int = 0, *songs):
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
            await ctx.send("No data found for the specified event. It probably hasn't started yet. If it has but this error is still being shown, please let Josh#1373 know.")

    @commands.command(name='t10ids',
                aliases=['t10i'],
                brief="t10 info with user ids",
                help="Provides current or specified event t10 info. Can look on a per event/server level, you can also include the songs parameter to look at song info (CL or VS only). However, a lot of the old data has been made inacessible or deleted so the bot may throw an error when checking. You can find the eventIds for any event by going to https://bestdori.com/info/events\n\nExamples\n\n.t10ids en\n.t10ids en 30\n.t10ids jp 78 songs")
    async def t10ids(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        try:
            server = server.lower()
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
            await ctx.send("No data found for the specified event. It probably hasn't started yet. If it has but this error is still being shown, please let Josh#1373 know.")

    @commands.command(name='t10members',
                aliases=['t10m'],
                help="Aliases: t10m\n\nPosts t10 info with each player's team in their profile along with skill level for each member",
                brief='t10 info with member info ')
    async def t10members(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if(eventid == 0):
            eventid = await GetCurrentEventID(server)
        else:
            eventid = eventid
        if(songs):
            output = await t10membersformatting(server, eventid, True)
            #doing this because on a CL, the output is very likely >2000 characters bypassing discord's limit
            for x in output:
                await ctx.send(x)
        else:
            output = await t10membersformatting(server, eventid, False)
            await ctx.send(output)

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
        coastingTable = await GetCoastingOutput(server, epPerSong, currentEP)
        await ctx.send(coastingTable)


        
        
        

    #######################
    #    Cutoff Command   #
    #######################
    
    #open website
    with open("config.json") as file:
        config_json = json.load(file)
        driverPath = config_json["chromeDriverPath"]
        
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    enDriver = webdriver.Chrome(options=options,executable_path=driverPath)
    enDriver.get('https://bestdori.com/tool/eventtracker/en/t100')
    enDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
    jpDriver = webdriver.Chrome(options=options,executable_path=driverPath)
    jpDriver.get('https://bestdori.com/tool/eventtracker/jp/t100')
    jpDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
    
    @commands.command(name='refresh',
                       aliases=['r'],
                       hidden=True)
    async def refresh(self, ctx, server: str = 'en'):
        try:
            if server == 'en':
                driver = self.enDriver
            else:
                driver = self.jpDriver
            driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/a').click()
        except:
            await ctx.send('Failed refreshing the event tracker page.')        
    

        
    @commands.command(name='cutoff',
                     aliases=['t100','t1000','t2000'],
                     brief="Cutoff estimate for t100 and t1000 (and t2000 if jp)",
                     help="Cutoff estimate for t100 and t1000 (and t2000 if jp). Pass the cutoff you want and server (defaulted to en)\n\nCurrently using https://bestdoribeta.animepie.to/tool/eventtracker, all credit goes to Burrito\n\nExamples\n\n.cutoff 100\n.cutoff 1000 en\n.cutoff 2000 jp")
    async def cutoff(self, ctx, tier: int = 100, server: str = 'en'):
        if 't1000' in ctx.invoked_with:
            tier = 1000
        elif 't100' in ctx.invoked_with:
            tier = 100
        elif 't2000' in ctx.invoked_with:
            tier = 2000
            server = 'jp'
        if(tier == 2000):
            server = 'jp'
        else:
            server = server
        if server == 'en':
            driver = self.enDriver
        else:
            driver = self.jpDriver
        output = await GetCutoffFormatting(driver, server, tier)
        await ctx.send(embed=output)


    @coasting.error
    async def coasting_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")

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

    @cutoff.error
    async def cutoff_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`! Required arguments are enclosed in < >")
        if isinstance(error, commands.errors.CommandInvokeError):
            print(str(error))
            await ctx.send("Failed getting cutoff data. Please let Josh#1373 know if this keeps happening. Old events cutoff data can been seen using the `event` command")

def setup(bot):
    bot.add_cog(Event(bot))