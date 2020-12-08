from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_permissions(embed_links=True)
    async def help(self,ctx,*commands):
        try:
            bot_icon_url = f"{self.bot.user.avatar_url.BASE}{self.bot.user.avatar_url._url}"
            if not commands:
                help=discord.Embed(title='Available Commands',color=discord.Color.blue(),description='Run this command again followed by a command or list of commands to receive further help (e.g. `.help cutoff`)')
                help.set_thumbnail(url=bot_icon_url)
                for x in self.bot.cogs:
                    cog_commands = (self.bot.get_cog(x)).get_commands()
                    if cog_commands and x not in ['Help','Admin']:
                        commands = []
                        for y in cog_commands:
                            if y.hidden == False:
                                commands.append(y.name)
                        commands = ('\n'.join(map(str, sorted(commands))))
                        help.add_field(name=x,value=commands,inline=True)
                await ctx.send(embed=help)
            else:
                for command in commands:
                    found = False
                    for x in self.bot.cogs:
                        cog_commands = (self.bot.get_cog(x)).get_commands()
                        for y in cog_commands:
                            if command == y.name or command in y.aliases:
                                if y.aliases:
                                    help=discord.Embed(title=f"{y.name.capitalize()} ({(', '.join(map(str, sorted(y.aliases))))})",color=discord.Color.blue())
                                else:
                                    help=discord.Embed(title=y.name.capitalize(),color=discord.Color.blue())
                                for c in self.bot.get_cog(y.cog_name).get_commands():
                                    if command == c.name or command in c.aliases:
                                        help.add_field(name='Description',value=c.description, inline=False)
                                        help.add_field(name='Inputs',value=f".{c.name} {c.signature}", inline=False)
                                        if c.help:
                                            help.add_field(name='Examples / Further Help',value=c.help, inline=False)
                                found = True
                    if not found:
                        """Reminds you if that cog doesn't exist."""
                        help = discord.Embed(title=f'No command with name {command} found',color=discord.Color.red())
                        help.set_thumbnail(url=bot_icon_url)
                    else:
                        help.set_thumbnail(url=bot_icon_url)
                        await ctx.send(embed=help)                     
        except Exception as e:
            await ctx.send(str(e))
            
            
def setup(bot):
    bot.add_cog(Help(bot))