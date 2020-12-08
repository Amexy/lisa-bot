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
from main import ctime
import asyncio
import discord
import json
import selenium
import math
import re

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.valid_t10_servers = ['en','jp']

        with open("config.json") as file:
            config_json = json.load(file)
            en_event_id = int(config_json["en_event_id"])
            jp_event_id = int(config_json["jp_event_id"])
            self.valid_t10_events_en = [en_event_id, en_event_id-1, en_event_id -
                       2, en_event_id-3, en_event_id-4, en_event_id-5]
            self.valid_t10_events_jp = [jp_event_id, jp_event_id-1, jp_event_id -
                       2, jp_event_id-3, jp_event_id-4, jp_event_id-5]

    @commands.command(name='t10events',
                    aliases=['t10e'],
                    description="Returns a list of events that can be checked for T10 data",
                    help='Examples:\n\n.t10events\n.t10e jp')
    async def t10events(self, ctx, server: str = 'en'):
        if server.lower() not in self.valid_t10_servers:
            await ctx.send("Only EN and JP can be checked for T10 data")
        else:
            if server.lower() == 'en':
                valid_t10_events = self.valid_t10_events_en
            if server.lower() == 'jp':
                valid_t10_events = self.valid_t10_events_jp
            if valid_t10_events: # In case the function isn't ran at startup
                await ctx.send(f'Valid t10 events for `{server}` are: {str(valid_t10_events)[1:-1]}')
            else:
                await ctx.send('Error loading valid t10 events. Use the `notify` command to let Josh know')

    @commands.command(name='t10archives',
                aliases=["t10a"],
                description="This is a premium function. Use `.premium`. for more information\n\nAttaches a txt file (if found) containing 2 minute t10 updates for the specified event and server",
                help=".t10a 76 (this defaults to en)\n.t10a 112 jp")
    async def t10archives(self, ctx, eventid: str, server: str = 'en'):
        valid_users = [158699060893581313,202289392394436609,384333652344963074]
        if ctx.author.id in valid_users:
            if not eventid.isnumeric():
                raise commands.errors.BadArgument
            try:
                if server not in self.valid_t10_servers:
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
        else:
            await ctx.send('Event archive access is now a premium feature. Please use `.premium` for more information')

    @commands.command(name='t10',
                brief="t10 info",
                description="Posts t10 info. You can also include the songs parameter at the end to look at song info (given the event is CL or VS)",
                help=".t10 en 30\n.t10 jp 78 songs\n.t10 (defaults to en and the current event id, no songs")
    #@ctime
    async def t10(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.valid_t10_servers:
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
                    description="Posts t10 info with each player's id. You can also include the songs parameter at the end to look at song info (given the event is CL or VS)",
                    help=".t10ids en 30\n.t10ids jp 78 songs\n.t10i (defaults to en and the current event id, no songs)")
    #@ctime
    async def t10ids(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.valid_t10_servers:
                output = 'This function only works for the `EN` and `JP` servers'
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
                except:
                    output = f"Failed getting data for event with ID `{eventid}` on the `{server}` server. Please use the `.notify` command to let Josh know"
            await ctx.send(output)
    @commands.command(name='t10members',
                    aliases=['t10m'],
                    description="Posts t10 info with each player's team in their profile along with skill level for each member. You can also include the songs parameter at the end to look at song info (given the event is CL or VS)",
                    help=".t10members en 50\n.t10members jp 100 songs\n.t10m (defaults to en and the current event id, no songs)")
    #@ctime
    async def t10members(self, ctx, server: str = 'en', eventid: int = 0, *songs):
        if server.isnumeric():
            raise commands.errors.BadArgument
        else:
            server = server.lower()
            if server not in self.valid_t10_servers:
                await ctx.send('This function only works for the `EN` and `JP` servers')
            else:
                try:
                    UserID = ctx.message.author.id
                    if(eventid == 0):
                        eventid = await GetCurrentEventID(server)
                    else:
                        eventid = eventid
                    if(songs):
                        output = await t10membersformatting(server, eventid, True, UserID)
                        if 'No data found for event' in output: # Very scuffed way of doing this, but I don't feel like messing with errors (if that'd even work)
                            await ctx.send(output)
                        else:
                            #doing this because on a CL, the output is very likely >2000 characters bypassing discord's limit
                            for x in output:
                                await ctx.send(x)
                    else:
                        output = await t10membersformatting(server, eventid, False,)
                        await ctx.send(output)
                except:
                    await ctx.send(f"Failed getting data for event with ID `{eventid}` on the `{server}` server. Please use the `.notify` command to let Josh know")
    @commands.command(name='timeleft',
                    aliases=['tl'],
                    description="Provides the amount of time left (in hours) for an event",
                    help=".timeleft (defaults to en)\n.timeleft jp")
    #@ctime
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
                help=".coasting en 5000 200000")
    async def coasting(self, ctx, server: str, epPerSong: int, currentEP: int):
        ValidServers = ['en','jp','cn','tw','kr']
        if server.lower() not in ValidServers:
            await ctx.send('Please enter a valid server from one of the following: ' + str(ValidServers)[1:-1])
        else:
            coastingTable = await GetCoastingOutput(server.lower(), epPerSong, currentEP)
            await ctx.send(coastingTable)

    #######################
    #    Cutoff Commands   #
    #######################

    @commands.command(name='cutoffhistory',
                    aliases=['cutoffarchives','ch','ca'],
                    description="Gets the highest cutoff value for a given server and tier\n\nNote: This is based off Bestdori's data, so it's possible data could be incorrect because that value isn't known",
                    help = ".cutoffhistory en 100\n.ch jp 1")
    #@ctime
    async def cutoffhistory(self, ctx, server: str = 'en', tier: str = '10'):
        from commands.formatting.EventCommands import GetCutoffHistory
        try:
            embed = await GetCutoffHistory(server, tier)
            await ctx.send(embed=embed)
        except:
            await ctx.send(f"Couldn't find cutoff history for server `{server}` tier `{tier}`")

    @commands.command(name='cutoff',
                      aliases=['t100','t500','t1000', 't2000','t2500','t5000','t10000','t1k','t2k','t2.5k','t5k','t10k','co'],
                      description="Cutoff estimate for t100, t1000, and t2000 (experimental support for t2500, t5000, and t10000). Input the tier and server (defaulted to en and 100). Add graph as an argument to see a graph",
                      help=".cutoff 100\n.cutoff 1000 en\n.cutoff 2000 jp graph\n.cutoff en t1000\n.t100\n.t100 jp graph")
    #@ctime
    async def cutoff(self, ctx, *args):
        valid_servers = {'jp', 'cn', 'en', 'tw', 'kr'}
        valid_servers_by_tier = {
            100: ['en', 'jp', 'cn', 'tw', 'kr'],
            500: ['tw'],
            1000: ['en', 'jp', 'cn'],
            2000: ['jp', 'cn'],
            2500: ['en'],
            5000: ['jp'],
            10000: ['jp']
        }

        ctx.invoked_with = ctx.invoked_with.lower()
        tier_regex = re.compile(r't?([0-9]+k?|[0-9]+\.[0-9]+k)')

        tier = None
        server = None
        graph = None

        def parse_tier_arg(tier_arg):
            if tier_arg[0] == 't':
                tier_arg = tier_arg[1:]
            if tier_arg[-1] == 'k':
                return round(1000 * float(tier_arg[:-1]))
            return int(tier_arg)

        for arg in args:
            arg = arg.lower()
            if tier_regex.fullmatch(arg):
                if tier is not None:
                    await ctx.send('Only one tier argument is allowed.')
                    return
                tier = parse_tier_arg(arg)
            elif arg in valid_servers:
                if server is not None:
                    await ctx.send('Only one server argument is allowed.')
                    return
                server = arg
            elif arg == 'graph':
                graph = True
            else:
                await ctx.send(f'Unknown argument: "{arg}".')
                return

        # set tier if using an alias (.t100, .t1000, etc.)
        if tier_regex.fullmatch(ctx.invoked_with):
            if tier is not None:
                await ctx.send('Tier already specified by alias.')
                return
            tier = parse_tier_arg(ctx.invoked_with)

        tier = tier or 100
        if tier not in valid_servers_by_tier:
            await ctx.send(f'Invalid tier: {tier}.')
            return

        server = server or valid_servers_by_tier[tier][0]

        if server not in valid_servers_by_tier[tier]:
            tier_server_list = [server.upper() for server in valid_servers_by_tier[tier]]
            if len(tier_server_list) < 3:
                readable_list = ' and '.join(tier_server_list)
            else:
                readable_list = ', '.join(tier_server_list[:-1]) + ', and ' + tier_server_list[-1]
            await ctx.send(f'T{tier} is only valid for {readable_list}.')
            return
        try:
            if graph:
                output = await GetCutoffFormatting(server, tier, True)
                await ctx.send(file=output[1], embed=output[0])
            else:
                output = await GetCutoffFormatting(server, tier, False)
                await ctx.send(embed=output)
        except IndexError:
            await ctx.send('Failed getting cutoff data')

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
