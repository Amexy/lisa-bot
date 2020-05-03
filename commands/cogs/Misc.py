from discord.ext import commands
from tabulate import tabulate
from googletrans import Translator
import discord, os, shutil, requests
from discord import File

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='servericon',
                    aliases=['sp','si','serverpic'],
                    help="Uploads the server's icon")
    async def servericon(self, ctx):
        GuildInfo = self.bot.get_guild(ctx.message.guild.id)
        GuildPicURL = GuildInfo.icon_url.BASE + GuildInfo.icon_url._url
        if '.gif' in GuildInfo.icon_url._url:
            FileExtension = '.gif'
        else:
            FileExtension = '.png'
        SavedPicPath = 'imgTmp/' + str(ctx.message.guild.id) + FileExtension
        response = requests.get(GuildPicURL, stream=True)
        if os.path.exists(SavedPicPath):
            os.remove(SavedPicPath)
        with open(SavedPicPath, 'ab') as Out_file:
            shutil.copyfileobj(response.raw, Out_file)
            DiscordFileObject = File(SavedPicPath)
        await ctx.send(file=DiscordFileObject)
        del response
    
    @commands.command(name='reload',
                    help='In the event that the loops (in particular 2 minute/1hr t10 posting) stop working, run this command to restart that process. If you want access to this command, please use the .notify command')
    async def reload(self, ctx):
        ValidUsers = [158699060893581313, 202289392394436609, 102201838752784384, 358733607151599636, 229933911717707776, 181690542730641408, 154997108603224064]
        if ctx.message.author.id not in ValidUsers:
            await ctx.send("You are not authorized to use this command. If you'd like access, please use the .notify command requesting access")
        else:
            try:
                self.bot.reload_extension("commands.cogs.Loops")
                await ctx.send("Successfully reloaded the Loops cog")
            except:
                await ctx.send("Failed reloading the Loops cog. Please use the `.notify` command to let me know") 
    

    @commands.command(name='notify',
                      aliases=['n'],
                      help='Sends a notification about the bot to Josh#1373 (use this for things like 2min/1hr t10 tracking failing, or a command repeatedly fails\n\nExamples:\n\n.notify the bot is failing to get t10 data for en')
    async def notify(self, ctx, *notification):
        if notification:
            notificationString = notification[0]
            for x in notification:
                if x == notificationString:
                    continue
                notificationString += " %s" % x
            channel = self.bot.get_channel(705596502277357620)
            await channel.send(str(ctx.message.author.name) + "#" + str(ctx.message.author.discriminator) + " | " + str(ctx.message.guild.name) + ": " + notificationString)
            await ctx.send("Notification sent")
        else:
            await ctx.send('Please enter your notification')

    @commands.command(name='avatar',
                    aliases=['a'],
                    help="Uploads the mentioned user's avatar\n\n.Examples:\n\n.avatar @Lisa#4081\n.a Lisa#4081\n.a 523337807847227402\n.a Lisa (ths one may not always work)")
    async def getavatar(self, ctx, user: discord.Member):
        UserPicUrl = user.avatar_url.BASE + user.avatar_url._url
        if '.gif' in user.avatar_url._url:
            FileExtension = '.gif'
        else:
            FileExtension = '.png'
        SavedPicPath = 'imgTmp/' + str(user.id) + FileExtension
        response = requests.get(UserPicUrl, stream=True)
        if os.path.exists(SavedPicPath):
            os.remove(SavedPicPath)
        with open(SavedPicPath, 'ab') as Out_file:
            shutil.copyfileobj(response.raw, Out_file)
            DiscordFileObject = File(SavedPicPath)
        await ctx.send(file=DiscordFileObject)
        del response

    @commands.command(name='about',
                      aliases=['info'],
                      description="Posts info about the bot",
                      brief="Posts info about the bot",
                      help="Posts info about the bot")
    async def about(self, ctx):
        await ctx.send("```" + "Developed by: Josh#1373 (with help from many others)\nDiscord:      discord.gg/wDu5CAA\nPlease DM or @ Josh if you have any feedback/suggestions!" + "```")
    
    @commands.command(name='translate',
                      aliases=['trans'],
                      help='Translates the message given (source language is autodetected)')
    async def translate(self, ctx, language, *message):
        FullMessage = message[0]
        for x in message:
            if x == FullMessage:
                continue
            FullMessage += " %s" % x
        translator = Translator()
        TranslatedMessage = translator.translate(FullMessage)
        await ctx.send(TranslatedMessage.text)

    
    @commands.command(name='invite',
                      help='Posts the invite link for Lisabot',
                      brief='Posts the invite link for Lisabot',
                      description='Posts the invite link for Lisabot')
    async def invite(self, ctx):
        await ctx.send('LisaBot: https://lisabot.bandori.app')
    @commands.command(name='support',
                      brief='Posts kofi link')
    async def kofi(self, ctx):
        await ctx.send("If you'd like to support the hosting costs for Lisabot, you can do so by visiting https://ko-fi.com/lisabot")

    @commands.command(name='github',
                      brief='Posts github repo')
    async def github(self, ctx):
        await ctx.send("If you'd like to contribue to Lisabot or just learn more about the code, please visit https://github.com/Amexy/lisa-bot")

    @commands.command(name='suggest',
                      brief='Make a suggestion for Lisabot',
                      help='Sends a suggestion for Lisabot to Josh#1373')
    async def suggest(self, ctx, *suggestion):
        if suggestion:
            suggestionString = suggestion[0]
            for x in suggestion:
                if x == suggestionString:
                    continue
                suggestionString += " %s" % x
            channel = self.bot.get_channel(624799117213958144)
            await channel.send(str(ctx.message.author.name) + "#" + str(ctx.message.author.discriminator) + " | " + str(ctx.message.guild.name) + ": " + suggestionString)
            await ctx.send("Thanks for the suggestion {0.author.mention}!".format(ctx.message))
        else:
            await ctx.send('Please enter your suggestion')

def setup(bot):
    bot.add_cog(Misc(bot))