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

    #################
    #  Patch Notes  #
    #################
    @commands.command(name='addpatchupdates',
                      description="(Requires Admin Privileges) Given a server and channel input, this channel will receive updates patch notes from Bestdori",
                      help=".addpatchupdates (defaults to all servers and  thechannel command was ran in)\n.addpatchupdates en\n.addpatchupdates jp 523339468229312555")
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
                      help=".removepatchupdates (defaults to all servers and  thechannel command was ran in)\n.removepatchupdates en\n.removepatchupdates jp 523339468229312555")
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
                      help=".addupdates (this defaults to EN and the channel the command is ran in)\n.addupdates en\n.addupdates jp 523339468229312555")
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
                      help=".removeupdates (this defaults to 1 hour and channel the command is ran in)\n.removeupdates 523339468229312555 en")
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
                      description="(Requires Admin Privileges) Given a channel and tier input, this channel will receive updated cutoff values from Bestdori\n",
                      help=".addcutoffupdates (defaults to T100 and T1000 updates + channel command was sent in)\n.addcutoffupdates 100\n.addcutoffupdates 1000 523339468229312555")
    async def addt100updates(self, ctx, tier: int = 0, channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            if tier == 0:
                await ctx.send(addChannelToCutoffDatabase(channel, 100))
                await ctx.send(addChannelToCutoffDatabase(channel, 1000))
            else:
                await ctx.send(addChannelToCutoffDatabase(channel, tier))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)
            
    @commands.command(name='removecutoffupdates',
                      aliases=['rmcu','rmcutoffupdates'],
                      description="Given a channel and tier input, this channel will stop receiving updated cutoff values from Bestdori",
                      help=".removecutoffupdates (defaults to T100 and T1000 updates + channel command was sent in)\n.rmcu 100\n.rmcu 1000 523339468229312555")
    async def rmt100updates(self, ctx, tier: int = 100, channel: TextChannel = None):
        if ctx.message.author.guild_permissions.administrator:
            if(channel == None):
                channel = ctx.channel
            await ctx.send(rmChannelFromCutoffDatabase(channel, tier))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    #######################
    #     T10 Commands    #
    #######################
    @commands.command(name='addtracking',
                      description="Given a channel, interval (2min or 1hour), and server input (en or jp), this channel will receive t10 updates in regular intervals",
                      help=".addtracking 523339468229312555 2\n.addtracking 523339468229312555 3600 en\n.addtracking (this defaults to 1 hour and channel the command is ran in)")
    async def addTracking(self, ctx, channel: TextChannel = None, interval: int = 3600, server: str = 'en'):
        if ctx.message.author.guild_permissions.administrator:
            ValidIntervals = [2,60,3600]
            if interval not in ValidIntervals:
                await ctx.send('Please enter a value of 2 for 2 minute updates or 60/3600 for hourly updates')
            else:
                if interval == 60:
                    interval = 3600
                if(channel == None):
                    channel = ctx.channel
                await ctx.send(addChannelToDatabase(channel, interval, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)
    
    @commands.command(name='removetracking',
                      description="Given a channel, interval (2min or 1hour), and server input, this channel will be removed from t10 tracking updates",
                      help=".removetracking 523339468229312555 2\n.removetracking 523339468229312555 60 en\n.removetracking (this defaults to 1 hour and channel the command is ran in")
    async def removeTracking(self, ctx, channel: TextChannel = None, interval: int = 3600, server: str = 'en'):
        if ctx.message.author.guild_permissions.administrator:
            ValidIntervals = [2,60,3600]
            if interval not in ValidIntervals:
                await ctx.send('Please enter a value of 2 for 2 minute updates or 60/3600 for hourly updates')
            else:
                if interval == 60:
                    interval = 3600
                if(channel == None):
                    channel = ctx.channel
            await ctx.send(removeChannelFromDatabase(channel, interval, server))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @commands.command(name='addsongupdates',
                      aliases=['asu'],
                      description="Given a channel input, this channel will receive t10 song + member info updates in a 1 mintue interval for the EN server",
                      help=".addsongupdates (this defaults to the channel the command is ran in)\n.addsongupdates 523339468229312555)")
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
                      help=".removetracking (this defaults to the channel the command is ran in) 2\n.removetracking 523339468229312555")
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
