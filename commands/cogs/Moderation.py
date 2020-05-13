from discord.ext import commands
from discord.guild import Guild
from discord.member import Member
from discord.channel import TextChannel
from discord.utils import get
from commands.formatting.DatabaseFormatting import GetAllRoles, CheckRoleForAssignability, AddRoleToDatabase, RemoveRoleFromAssingability
import discord
from tinydb import TinyDB, where, Query
from tabulate import tabulate
class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setprefix',
                      description='Sets the command prefix the bot will use',
                      help='Example: .setprefix !')
    async def setprefix(self, ctx, prefix: str):
        from commands.formatting.DatabaseFormatting import addPrefixToDatabase
        if ctx.message.author.guild_permissions.administrator:
            guild = ctx.message.guild
            await ctx.send(addPrefixToDatabase(guild, prefix))
        else:
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)


    @commands.command(name='newrole',
                      aliases=['nr','addrole'],
                      description='(Manage Roles) Adds a mentionable role (self assignable or not) to the server',
                      help='Inputs are name, color, and selfassignable (just True or False). Color must be in hex format (# not needed) or a value from the list below. SelfAssignable requires a value of True or False.\n\nValid Premade Colors:\n\nTeal\nDark Teal\nGreen\nDark Green\nBlue\nDark Blue\nPurple\nDark Purple\nMagenta\nDark Magenta\nGold\nDark Gold\nOrange\nDark Orange\nRed\nDark Red\nLighter Grey\nDark Grey\nLight Grey\nDarker Grey\nBlurple\nGreyple\n\nExamples: \n\n.newrole RoleName\n.nr RoleName True\n.nr RoleName True ffe2b0\n.newrole RoleName False blue')
    async def newrole(self, ctx, rolename: str, selfassignable: bool = False, rolecolor: str = ''):
        if ctx.message.author.guild_permissions.manage_roles:
            try:
                guild = ctx.guild
                if rolecolor:
                    rolecolor = rolecolor.lower()
                    PremadeColors = ['teal','dark teal','green','gark green','blue','dark blue','purple','dark purple','magenta','dark magenta','gold','dark gold','orange','dark orange','red','dark red','lighter grey','dark grey','light grey','darker grey','blurple','greyple']
                    if rolecolor in PremadeColors:
                        rolecolor = getattr(discord.Colour,rolecolor)()
                    else:
                        rolecolor = discord.Colour(int(rolecolor, 16))
                    await guild.create_role(name=rolename,color=rolecolor,mentionable=True)
                else:
                    await guild.create_role(name=rolename,mentionable=True)
                await ctx.send('Role `%s` created' %(rolename))
                if selfassignable:
                    Channel = self.bot.get_channel(523339468229312555)
                    await Channel.send(AddRoleToDatabase(ctx.channel, ctx.guild.name, rolename))                
        
            except Exception:
                pass
        else:
            msg = "You must have `manage_roles` rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @commands.command(name='deleterole',
                      aliases=['dr','removerole','rmr'],
                      description='(Manage Roles) Remove a role from the server',
                      help='.removerole RoleName')
    async def deleterole(self, ctx, rolename: str):
        if ctx.message.author.guild_permissions.manage_roles:
                guild = ctx.guild
                try:
                    from discord.role import Role
                    role = get(guild.roles, name=rolename)
                    role = guild.get_role(role.id)
                    
                    await role.delete()
                    if (CheckRoleForAssignability(rolename, guild.id)):
                        RemoveRoleFromAssingability(rolename,guild.id)
                    await ctx.send("Role `%s` has been deleted" %(rolename))
                except Exception:
                    await ctx.send("Role `%s` wasn't found. If the role exists and still isn't deletable, please delete it manually and use the `.notify` command to let Josh know." %(rolename))
        else:
            msg = "You must have `manage_roles` rights to run this command, {0.author.mention}".format(ctx.message)  
            await ctx.send(msg)

    @commands.command(name='assignrole',
                      aliases=['asnr','assign','ar'],
                      description='Assigns the user running the command the role mentioned')
    async def assignrole(self,ctx,rolename: str):
        try:
            GuildID = ctx.guild.id
            IsRoleAssignable = CheckRoleForAssignability(rolename, GuildID)
            if IsRoleAssignable:
                user = ctx.message.author
                role = get(user.guild.roles, name=rolename)
                try:
                    await Member.add_roles(user, role)
                    await ctx.send('Role `%s` has been assigned to %s#%s' %(rolename,user.display_name,user.discriminator))
                except Exception:
                    await ctx.send("Role `%s` wasn't found. If the role exists and still isn't assignable, please use the `.notify` command to let Josh know." %(rolename))
            else:
                await ctx.send("Role not found or isn't assignable")
        except Exception:
            pass
        
    @commands.command(name='getroles',
                      aliases=['gr'],
                      description='Lists all self assignable roles in the server')
    async def getroles(self, ctx):
        try:
            GuildID = ctx.guild.id
            Roles = GetAllRoles(GuildID)
            RolesAvailable = tabulate(Roles,tablefmt="plain")
            await ctx.send("```Assignable Roles:\n\n" + RolesAvailable + "```")
        except Exception as e:
            pass

    @setprefix.error 
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You must have administrator rights on the servers to run this command.")

def setup(bot):
    bot.add_cog(Servers(bot))