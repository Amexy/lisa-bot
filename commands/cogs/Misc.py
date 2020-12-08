from discord.ext import commands
from tabulate import tabulate
from googletrans import Translator
from discord import File
from main import ctime
import discord, os, shutil, requests, asyncio

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='premium')
    async def premium(self, ctx):
        await ctx.send("As a way to recoup hosting costs, 2 minute tracking/archive data will become a premium feature of Lisabot. **Current pricing is $10/event**. Hourly will remain free for now.\n\nIf you'd like to purchase 2 minute tracking for your event, please send your payment through ko-fi and DM Josh#1373 your server ID and channel ID that will be used for 2 minute tracking. Developer mode must be enabled in Discord under your settings, right click the server and channel and select the `Copy ID` option.\n\nIf you have any questions, please let Josh#1373 know.\n\nhttps://ko-fi.com/lisabot")
    
    @commands.command(name='servericon',
                    aliases=['sp','si','serverpic'],
                    description="Uploads the server's icon")
    #@ctime
    async def servericon(self, ctx):
        GuildInfo = self.bot.get_guild(ctx.message.guild.id)
        GuildPicURL = GuildInfo.icon_url.BASE + GuildInfo.icon_url._url
        if '.gif' in GuildInfo.icon_url._url:
            FileExtension = '.gif'
        else:
            FileExtension = '.png'
        SavedPicPath = 'data/img/imgTmp/' + str(GuildInfo.id) + FileExtension
        response = requests.get(GuildPicURL, stream=True)
        if os.path.exists(SavedPicPath):
            os.remove(SavedPicPath)
        with open(SavedPicPath, 'ab') as Out_file:
            shutil.copyfileobj(response.raw, Out_file)
            DiscordFileObject = File(SavedPicPath)
        embed = discord.Embed(title=f"{GuildInfo.name}'s Avatar",color=discord.Color.blue())
        embed.set_image(url=f"attachment://{GuildInfo.id}{FileExtension}")
        embed.add_field(name='Link', value=GuildPicURL)
        await ctx.send(embed=embed,file=DiscordFileObject)
        del response

    @commands.command(name='reload',
                     description='In the event that the loops (in particular 2 minute/1hr t10 posting) stop working, run this command to restart that process. If you want access to this command, please use the .notify command')
    async def reload(self, ctx, cog: str = ''):
        if not cog: #By default, it will reload the Loops command since this is the most common one that fails and users need access to
            ValidUsers = [384333652344963074,117394661886263302,119252023395876864,485843748647993375, 99640840929943552, 202289392394436609, 102201838752784384, 358733607151599636, 229933911717707776, 181690542730641408, 154997108603224064]
            from commands.cogs.Updates import Updates
            u = Updates
            if ctx.message.author.id not in ValidUsers and ctx.message.guild.id not in u.premium_guilds:
                await ctx.send("You are not authorized to use this command. If you'd like access, please use the .notify command requesting access")
            else: 
                for task in asyncio.Task.all_tasks():
                    if 'post' in str(task):
                        task.cancel()
                        print('Cancelled task ' + str(task._coro))
                try:
                    from commands.cogs.Loops import Loops
                    Loops(self.bot)
                    c = self.bot.get_cog("Loops")
                    self.bot.remove_cog(c)
                    self.bot.add_cog(c)
                    await ctx.send("Successfully reloaded the Loops cog")
                except:
                    await ctx.send("Failed reloading the Loops cog. Please use the `.notify` command to let Josh know")
        else:
            ValidUsers = [158699060893581313]
            if ctx.message.author.id not in ValidUsers:
                await ctx.send("You are not authorized to use this command. If you'd like access, please use the .notify command requesting access")
            else:
                try:
                    cog = f"commands.cogs.{cog.capitalize()}"
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
                    await ctx.send(f"Successfully reloaded the {cog} cog")
                except:
                    await ctx.send(f"Failed reloading the {cog} cog.")

            
    @commands.command(name='gt',
                    hidden=True)
    async def gettasks(self, ctx):
        ValidUsers = [158699060893581313]
        if ctx.message.author.id not in ValidUsers:
            await ctx.send("You are not authorized to use this command. If you'd like access, please use the .notify command requesting access")
        else: 
            for task in asyncio.Task.all_tasks():
                if 'post' in str(task):
                    print(str(task._coro))

    @commands.command(name='notify',
                      aliases=['n'],
                      description='Sends a notification about the bot to Josh#1373 (use this for things like 2min/1hr t10 tracking failing, or a command repeatedly fails',
                      help='.notify the bot is failing to get t10 data for en')
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
                    description="Uploads the mentioned user's avatar",
                    help='.avatar @Lisa#4081\n.a Lisa#4081\n.a 523337807847227402\n.a Lisa (ths one may not always work if multiple users have the same name)')
    #@ctime
    async def getavatar(self, ctx, user: discord.Member = None):
        if not user:
            user = self.bot.get_user(ctx.message.author.id)
        UserPicUrl = user.avatar_url.BASE + user.avatar_url._url
        if '.gif' in user.avatar_url._url:
            FileExtension = '.gif'
        else:
            FileExtension = '.png'
        SavedPicPath = 'data/img/imgTmp/' + str(user.id) + FileExtension
        response = requests.get(UserPicUrl, stream=True)
        if os.path.exists(SavedPicPath):
            os.remove(SavedPicPath)
        with open(SavedPicPath, 'ab') as Out_file:
            shutil.copyfileobj(response.raw, Out_file)
            DiscordFileObject = File(SavedPicPath)
        embed = discord.Embed(title=f"{user.display_name}'s Avatar",color=discord.Color.blue())
        embed.set_image(url=f"attachment://{user.id}{FileExtension}")
        embed.add_field(name='Link', value=UserPicUrl)
        await ctx.send(embed=embed,file=DiscordFileObject)
        del response

    @getavatar.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'No user found with that name. Names are case sensitive')
    @commands.command(name='about',
                      aliases=['info'],
                      description="Posts info about the bot")
    async def about(self, ctx):
        await ctx.send("```" + "Developed by: Josh#1373 (with help from many others)\nDiscord:      discord.gg/wDu5CAA\nPlease DM or @ Josh if you have any feedback/suggestions!" + "```")
    
    @commands.command(name='translate',
                      aliases=['t'],
                      description='Translates the message given. Autodetects language',
                      help='.translate 今井リサ')
    async def translate(self, ctx,  *message):
        if not message:
            output = 'Please enter a message to translate'
        else:
            try:
                FullMessage = message[0]
                for x in message:
                    if x == FullMessage:
                        continue
                    FullMessage += " %s" % x
                translator = Translator()
                TranslatedMessage = translator.translate(FullMessage)
                output = TranslatedMessage.text
            except:
                output = 'Failed translating message. Please use the `notify` command if this keeps happening'
        await ctx.send(output)
 
    @commands.command(name='invite',
                      description='Posts the invite link for Lisabot')
    async def invite(self, ctx):
        await ctx.send('Step 1: Open https://discordapp.com/oauth2/authorize?client_id=523337807847227402&scope=bot&permissions=268437504\nStep 2: Login to Discord if prompted\nStep 3: Select the server you wish to invite the bot to from the dropdown (required Admin privileges on the server)\nStep 4: Continue through the prompts as needed')
    
    @commands.command(name='support',
                      description='Posts kofi link')
    async def kofi(self, ctx):
        await ctx.send("If you'd like to support the hosting costs for Lisabot, you can do so by visiting https://ko-fi.com/lisabot")

    @commands.command(name='github',
                      description='Posts github repo')
    async def github(self, ctx):
        await ctx.send("If you'd like to contribue to Lisabot or just learn more about the code, please visit https://github.com/Amexy/lisa-bot")

    @commands.command(name='suggest',
                      description='Sends a suggestion for Lisabot to Josh#1373',
                      help='.suggest this is a suggestion')
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
