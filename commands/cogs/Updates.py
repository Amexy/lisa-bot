from discord.ext import commands
from discord import TextChannel
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from commands.formatting.DatabaseFormatting import removelChannelFromNewsDatabase, addChannelToNewsDatabase, addUpdatesToDatabase, removeUpdatesFromDatabase, addChannelToDatabase, removeChannelFromDatabase, addChannelToCutoffDatabase, getChannelsToPost, rmChannelFromCutoffDatabase, removeChannelFromDatabaseSongs, addChannelToDatabaseSongs
from commands.formatting.TimeCommands import GetEventTimeLeftSeconds
from commands.formatting.T10Commands import t10formatting
from commands.formatting.EventCommands import GetCurrentEventID
import asyncio

class Updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='addpremiumuser',
                      aliases=['apu'])
    async def add_premium_user(self, ctx, user_id: int, server_id: int, event_id: int, server: str):
        if ctx.author.id != 158699060893581313:
            await ctx.send('Unauthorized to use this command')
        else:
            from commands.formatting.DatabaseFormatting import add_user_to_premium_db
            # May use these later
            # user = self.bot.get_user(user_id)
            # server = self.bot.get_guild(server_id)
            # user = user_id if not user else user 
            # server = server_id if not server else server
            await ctx.send(add_user_to_premium_db(user_id, server_id, event_id, server))
    #################
    #  Bot Updates  #
    #################
    @commands.command(name='addbotupdates',
                      aliases=['abu'],
                      description="(Requires Admin Privileges) Given a channel input, this channel will receive bot updates/notifications",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #lisabot-updates\n\n.addbotupdates (defaults to channel the command was ran in\n.abu #lisabot-updates")
    async def addbotupdates(self, ctx, channel: TextChannel = None):
        from commands.formatting.DatabaseFormatting import AddChannelToBotUpdatesDatabase
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(AddChannelToBotUpdatesDatabase(channel))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @commands.command(name='removebotupdates',
                      aliases=['rbu'],
                      description="(Requires Admin Privileges) Given a channel input, this channel will receive bot updates/notifications",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #lisabot-updates\n\n.addbotupdates (defaults to channel the command was ran in\n.abu #lisabot-updates")
    async def removebotupdates(self, ctx, channel: TextChannel = None):
        from commands.formatting.DatabaseFormatting import RemoveChannelFromBotUpdatesDatabase
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(RemoveChannelFromBotUpdatesDatabase(channel))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(
                ctx.message)
            await ctx.send(msg)

    #################
    #  Patch Notes  #
    #################
    @commands.command(name='addpatchupdates',
                      description="(Requires Admin Privileges) Given a server and channel input, this channel will receive updates patch notes from Bestdori",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #bestdori-updates)\n\n.addpatchupdates (defaults to all servers and thechannel command was ran in)\n.addpatchupdates en\n.addpatchupdates en #bestdori-updates\n.addpatchupdates jp 523339468229312555")
    async def addpatchtracking(self, ctx, server: str = 'all', channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(addChannelToNewsDatabase(channel, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    
    @commands.command(name='removepatchupdates',
                      description="(Requires Admin Privileges) Given a server and channel input, this channel will stop receiving updates patch notes from Bestdori",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #bestdori-updates)\n\n.removepatchupdates (defaults to all servers and  thechannel command was ran in)\n.removepatchupdates en\n.removepatchupdates en #bestdori-updates\n.removepatchupdates jp 523339468229312555")
    async def removepatchtracking(self, ctx, server: str = 'all', channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(removelChannelFromNewsDatabase(channel, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    ###################
    #  Event Updates  #
    ###################
    @commands.command(name='addupdates',
                      description="(Requires Admin Privileges) Given a channel input and server input (EN, JP, or empty), this channel will receive event time left and start reminders",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #updates)\n\n.addupdates (this defaults to EN and the channel the command is ran in)\n.addupdates en\n.addupdates en #updates\n.addupdates jp 523339468229312555")
    async def addupdates(self, ctx, server: str = 'en',channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(addUpdatesToDatabase(channel, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @commands.command(name='removeupdates',
                      description="Given a channel input and server input (EN, JP, or empty), this channel will stop receiving event time left and start reminders",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #updates)\n\n.removeupdates (this defaults to 1 hour and channel the command is ran in)\n.removeupdates en #updates\n.removeupdates jp 551119118976286730")
    async def removeupdates(self, ctx,server: str = 'en',channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(removeUpdatesFromDatabase(channel, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)
            
    @commands.command(name='addcutoffupdates',
                      aliases=['acu'],
                      description="(Requires Admin Privileges) Given a server, tier, and channel input, this channel will receive updated cutoff values from Bestdori for the specified server\n\nCurrently supports all EN and JP tiers (100 / 1000 / 2500 and 100 / 1000 / 2000 / 5000 / 10000)",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #cutoffs)\n\n.addcutoffupdates (defaults to EN t100, t1000, and t2500 updates + the channel command was sent in)\n.acu en 100\n.acu jp 5000 #cutoffs")
    async def addcutoffupdates(self, ctx, server: str = 'en', tier: int = 0, channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            ValidServers = {'jp', 'en'}
            ValidServersByTier = {
                100: ['en', 'jp'],
                1000: ['en', 'jp'],
                2000: ['jp'],
                2500: ['en'],
                5000: ['jp'],
                10000: ['jp']
            }
            if server not in ValidServers:
                output = f"The `{server}` server doesn't currently have cutoff update notifications enabled or it is not a valid server"
            elif tier not in ValidServersByTier.keys() and tier != 0:
                output = f"That tier isn't being tracked by Bestdori"
            else:
                if(channel == None):
                    channel = ctx.channel
                if tier == 0:
                    try:
                        for tier in ValidServersByTier:
                            if server in ValidServersByTier[tier]:
                                addChannelToCutoffDatabase(channel, tier, server)
                        output = f"Channel `{channel.name}` will now receive all cutoff updates for `{server}`"
                    except:
                        output = f"Failed adding {channel.name} to the cutoff updates database"
                else:
                    output = addChannelToCutoffDatabase(channel, tier, server)
        else:
            output = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
        await ctx.send(output)
            
    @commands.command(name='removecutoffupdates',
                      aliases=['rmcu','rmcutoffupdates'],
                      description="Given a channel and tier input, this channel will stop receiving updated cutoff values from Bestdori",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #cutoffs)\n\n.removecutoffupdates (defaults to T100 and T1000 updates + channel command was sent in)\n.rmcu en \n.rmcu jp 1000 #cutoffs")
    async def rmt100updates(self, ctx, server: str = 'en', tier: int = None, channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            ValidServers = {'jp', 'en'}
            ValidServersByTier = {
                100: ['en', 'jp'],
                1000: ['en', 'jp'],
                2000: ['jp'],
                2500: ['en'],
                5000: ['jp'],
                10000: ['jp']
            }
            if server not in ValidServers:
                output = f"The `{server}` server doesn't currently have cutoff update notifications enabled or it is not a valid server"
            elif tier not in ValidServersByTier.keys() and tier != 0:
                output = f"That tier isn't being tracked by Bestdori"
            else:
                if(channel == None):
                    channel = ctx.channel
                if tier == 0:
                    try:
                        for tier in ValidServersByTier:
                            if server in ValidServersByTier[tier]:
                                rmChannelFromCutoffDatabase(channel, tier, server)
                        output = f"Channel `{channel.name}` will stop receiving all cutoff updates for `{server}`"
                    except:
                        output = f"Failed removing {channel.name} from the cutoff updates database"
                else:
                    output = rmChannelFromCutoffDatabase(channel, tier, server)
        else:
            output = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
        await ctx.send(output)

    #######################
    #     T10 Commands    #
    #######################
    @commands.command(name='addtracking',
                      description="Given a channel, interval (2min or 1hour), and server input (en or jp), this channel will receive t10 updates in regular intervals",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #2min)\n\n.addtracking #2min-updates 2\n.addtracking 523339468229312555 3600 en\n.addtracking (this defaults to 1 hour and channel the command is ran in)")
    async def addTracking(self, ctx, channel: TextChannel = None, interval: int = 3600, server: str = 'en'):
        if interval == 2:
            from tinydb import TinyDB, where, Query
            db = TinyDB('databases/premium_users.json')
            q = Query()
            is_guild_premium = False
            event_id = int(await GetCurrentEventID(server))
            premium_check = db.get(q.guild == ctx.message.guild.id)
            valid_event_check = db.get(q.event_id == event_id)
            is_guild_premium = True if premium_check else False
            valid_event_check = True if valid_event_check else False
            if is_guild_premium:
                if valid_event_check:
                    await ctx.send(f"{addChannelToDatabase(channel, interval, server)} for event with id `{event_id}`")
                else:
                    registered_event_id = premium_check['event_id']
                    await ctx.send(f"Your server is registered for 2 minute tracking, but the event it's registered for isn't active yet. Please rerun this command at event start\n\n```Registered Event ID: {registered_event_id}\nCurrent Event ID:    {event_id}```")
            else:
                await ctx.send('2 minute tracking is now a premium feature. Please use `.premium` for more information')
        else:
            if ctx.message.author.guild_permissions.administrator:
                valid_intervals = [60,3600]
                if interval not in valid_intervals:
                    await ctx.send('Please enter a value of 2 for 2 minute updates or 60/3600 for hourly updates')
                else:
                    if interval == 60:
                        interval = 3600
                    if channel == None:
                        channel = ctx.channel
                    await ctx.send(addChannelToDatabase(channel, interval, server))
            else:
                await ctx.send("You must have administrator rights to run this command, {0.author.mention}".format(ctx.message))
    
    @commands.command(name='removetracking',
                      description="Given a channel, interval (2min or 1hour), and server input, this channel will be removed from t10 tracking updates",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #2min)\n\n.removetracking #2min-updates 2\n.removetracking 523339468229312555 60 en\n.removetracking (this defaults to 1 hour and channel the command is ran in")
    async def removeTracking(self, ctx, channel: TextChannel = None, interval: int = 3600, server: str = 'en'):
        if ctx.message.author.guild_permissions.administrator:
            if interval == 2:
                await ctx.send('2 minute tracking is now a premium feature. Please use `.premium` for more information')
            else:
                valid_intervals = [60,3600]
                if interval not in valid_intervals:
                    await ctx.send('Please enter a value of 2 for 2 minute updates or 60/3600 for hourly updates')
                else:
                    if interval == 60:
                        interval = 3600
                    if channel == None:
                        channel = ctx.channel
                await ctx.send(removeChannelFromDatabase(channel, interval, server))
        else:
            await ctx.send("You must have administrator rights to run this command, {0.author.mention}".format(ctx.message))

    @commands.command(name='addsongupdates',
                      aliases=['asu'],
                      description="Given a channel input, this channel will receive t10 song + member info updates in a 1 mintue interval for the EN server",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #2min)\n\n.addsongupdates (this defaults to the channel the command is ran in)\n.addsongupdates #song-updates)\n.asu 523339468229312555")
    async def addsongupdates(self, ctx, channel: TextChannel = None,):
        if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 158699060893581313:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(addChannelToDatabaseSongs(channel))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)
            
    @commands.command(name='removesongupdates',
                      aliases=['rmsu','rmsongupdates'],
                      description="Given a channel input, this channel will be removed from t10 song + member info updates",
                      help="You can specify either the channel's id, or by using the full channel name (e.g. #2min)\n\n.removesongupdates (this defaults to the channel the command is ran in)\n.removesongupdates #song-updates\n.rmsu 523339468229312555")
    async def rmsongupdates(self, ctx, channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(removeChannelFromDatabaseSongs(channel))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @addTracking.error
    async def addtracking_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid or unsupported argument. Please include a channel id (right click the channel, copy id), an interval (2 for 2 minutes, 3600 for hourly), and the desired server (en or jp)")


    @removeTracking.error
    async def removetracking_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument, please check required arguments using `.help <command>`.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid or unsupported argument. Please include a channel id (right click the channel, copy id), an interval (2 for 2 minutes, 3600 for hourly), and the desired server (en or jp)")


def setup(bot):
    bot.add_cog(Updates(bot))
