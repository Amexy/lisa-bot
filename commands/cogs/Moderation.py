from discord.ext import commands
from discord.guild import Guild
from discord.member import Member
from discord.channel import TextChannel
from discord.utils import get
from commands.formatting.DatabaseFormatting import GetAllRoles, CheckRoleForAssignability, AddRoleToDatabase, RemoveRoleFromAssingability, GetReactAssignmentList, CheckMessageForReactAssignment, AddReactToDatabase, RemoveReactFromDatabase
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
            msg = "You must have administrator rights to run this command, {0.author.mention}".format(
                ctx.message)
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
                    await Channel.send(AddRoleToDatabase(ctx.channel, rolename))                
        
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

    @commands.command(name='rroleconfig',
                      aliases=['rrc'],
                      description= 'Configures reaction-based role assignment.',
                      help = '.rroleconfig [disable/add/edit/remove] <message ID> "<role name>, <emoji>" "<role name>, <emoji>" ...\nExamples:\n\n.rrc add 76504 "@role, :apple:" "testRole2, :cat:"\n.rrc remove 76504 "testRole, :apple:"\n.rrc disable 76504')
    async def rroleconfig(self, ctx, *args):
        try:
            if ctx.message.author.guild_permissions.manage_roles:
                validOptions = ['disable', 'add', 'edit', 'remove']
                args = list(args)
                output = ''
                msgid = ''
                try:
                    option = args.pop(0)
                except IndexError:
                    output = "Oops! No parameters found. Did you forget to add them?"
                if option:
                    option = option.lower()
                    post = {}
                    if option in validOptions:
                        # Check for message ID parameter. 
                        # IndexError means nothing else was supplied, ValueError means order is incorrect or an invalid message ID
                        try:
                            msgid = int(args.pop(0))
                        except IndexError:
                            output = "No message ID detected. Perhaps you forgot to specify a message ID?"
                        except ValueError:
                            output = "Did not recognize the message ID. Perhaps your parameters are in the wrong order, or you forgot to specify a message ID."
                        
                        if msgid:
                            if option == 'add' or option == 'edit':
                                # If the value isn't in the database already, then it's a new entry.
                                # Check to see if the bot has proper permissions to track reacts from the message, and that the message exists
                                if CheckMessageForReactAssignment(msgid) == False:
                                    try:
                                        msg = await ctx.channel.fetch_message(int(msgid))
                                        msgid = msg.id

                                    except discord.Forbidden:
                                        output = "I don't have permissions to read message history in that channel."

                                    except discord.NotFound:
                                        output = "Message not found. The command must be ran in the same channel the message you're enabling was sent."

                                else:
                                    post = GetReactAssignmentList(msgid)
                                    msg = await ctx.channel.fetch_message(int(msgid))

                                # Check that there isg at least one pair supplied
                                if len(args) > 0:
                                    for arg in args:
                                        # Separate role name and emoji
                                        # The comma is needed due to role names being able to have a space in them, so we can't use it as a delimiter
                                        arg = arg.split(", ")
                                        # Check for proper formatting
                                        if len(arg) == 2:
                                            role = discord.utils.find(lambda r: r.name == arg[0], ctx.guild.roles)
                                            if not role:
                                                role = discord.utils.find(lambda r: r.mention == arg[0], ctx.guild.roles)
                                            if role:
                                                post[role.name] = arg[1]
                                                await msg.add_reaction(arg[1])
                                            else:
                                                output = (f"Role {arg[0]} not found! Did you spell it wrong?")
                                        else:
                                            output = ('Incorrect command formatting. Make sure role/emoji pairs are entered like `"<rolename>, <emoji>"`')
                                    
                                    if not output:
                                        output = AddReactToDatabase(msgid, post)
                                else:
                                    output = "No role/emoji pairs were given. Please specify the role you want to add."

                            elif option == 'remove':
                                if CheckMessageForReactAssignment(msgid):
                                    post = GetReactAssignmentList(msgid)
                                    
                                    if len(args) > 0:
                                        for arg in args:
                                            arg = arg.split(", ")
                                            if len(arg) == 2:
                                                role = discord.utils.find(lambda r: r.name == arg[0], ctx.guild.roles)
                                                if not role:
                                                    role = discord.utils.find(lambda r: r.mention == arg[0], ctx.guild.roles)
                                                if role:
                                                    post.pop(role.name)
                                                else:
                                                    output = f"Role {arg[0]} not found! Did you spell it wrong?"
                                            else:
                                                output = 'Incorrect command formatting. Make sure role/emoji pairs are entered like `"<rolename>, <emoji>"`'
                                
                                        if not output:
                                            output = AddReactToDatabase(msgid, post)
                                    else:
                                        output = "No role/emoji pairs were given. Please specify the role you want to remove."
                                else:
                                    output = "Message has not been enabled for reaction-based role assignment. Use option 'enable'"
                            
                            # Option must be 'disable', let's delete the entry from the DB
                            else:
                                if CheckMessageForReactAssignment(msgid):
                                    output = RemoveReactFromDatabase(msgid)
                                else:
                                    output = "Message was not enabled for reaction-based role assignment!"
                        else:
                            output = "Message not found. The command must be ran in the same channel the message you're enabling was sent."
                    else:
                        output = "Please supply a valid option."
            else:
                output = f"You must have `manage_roles` rights to run this command, {ctx.author}"
        except discord.errors.HTTPException:
            output = f"Failed finding the emoji entered. Check if there's extra spaces before or after the emoji."
        await ctx.send(output)
    
    @commands.command(name='sendupdate',
                      aliases=['update'],
                      hidden=True)
    async def sendupdate(self,ctx,*message):
        ValidUsers = [158699060893581313]
        if ctx.message.author.id not in ValidUsers:
            await ctx.send('You are not authorized to use this command')
        else:
            from commands.formatting.DatabaseFormatting import GetBotChannelsToPost, RemoveChannelFromBotUpdatesDatabase
            MessageToSend = ''
            for x in message:
                MessageToSend += " %s" % x
            ids = GetBotChannelsToPost()
            for i in ids:
                channel = self.bot.get_channel(i)
                if channel != None:
                    try:
                        await channel.send(MessageToSend)
                    except (commands.BotMissingPermissions, discord.errors.NotFound):
                        LoopRemovalUpdates = self.bot.get_channel(
                            523339468229312555)
                        await LoopRemovalUpdates.send('Removing bot upates from channel: ' + str(channel.name) + " in server: " + str(channel.guild.name))
                        RemoveChannelFromBotUpdatesDatabase(channel)

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
