from tinydb import TinyDB, where, Query
from tabulate import tabulate
from discord.channel import TextChannel
from discord.guild import Guild
from discord.user import User
from discord import RawReactionActionEvent

# Databases
eventCheckDb2min = 'databases/eventCheckDb2min.json'
songUpdates1Min = 'databases/songUpdates1Min.json'
eventCheckDb1hr = 'databases/eventCheckDb1hr.json'
eventCheckDb1min = 'databases/eventCheckDb1min.json'
enEventUpdatesDB = 'databases/enEventUpdatesDB.json'
jpEventUpdatesDB = 'databases/jpEventUpdatesDB.json'
bestdoriENNewsDB = 'databases/enNewsDB.json'
bestdoriJPNewsDB = 'databases/jpNewsDB.json'
bestdoriCNNewsDB = 'databases/cnNewsDB.json'
bestdoriAllNewsDB = 'databases/allNewsDB.json'
prefixDb = 'databases/prefixdb.json'
t100DB = 'databases/t100DB.json'
t1000DB = 'databases/t1000DB.json'
t2500DB = 'databases/t2500DB.json'
jp2MinuteTracking = 'databases/jp2MinuteTrackingDB.json'
jp1HourTracking = 'databases/jp1HourTrackingDB.json'
botupdatesDB = 'databases/botupdates.json'
premium_db = 'databases/premium_users.json'
rolls_db = 'databases/rolls/rolls_new.json'

from main import ctime
@ctime
async def update_rolls_db(roll_info):
    from commands.database_handler import create_connection
    conn = create_connection()            
    update_user_info_query =    '''
                                INSERT OR IGNORE INTO users(discord_id, discord_name) VALUES (?, ?) 
                                '''
    update_users_rolls_info_query = '''
                                INSERT OR IGNORE INTO user_roll_stats(discord_id, two_stars_count, three_stars_count, four_stars_count) VALUES (?, ?, ?, ?)
                                    '''
    update_users_rolls_stats_query = '''
                                UPDATE user_roll_stats
                                SET two_stars_count = two_stars_count + ?,
                                    three_stars_count = three_stars_count + ?,
                                    four_stars_count = four_stars_count + ?
                                WHERE discord_id = ?
                               '''
    c = conn.cursor()
    c.execute(update_user_info_query, (roll_info['user_id'], roll_info['user_name']))
    c.execute(update_users_rolls_info_query, (roll_info['user_id'], 0, 0, 0))
    c.execute(update_users_rolls_stats_query, (roll_info['two_stars'], roll_info['three_stars'], roll_info['four_stars'], roll_info['user_id']))
    for chara in roll_info['chara']:
        # have to use format here because sqlite doesn't let you use ? for table names
        c.execute("INSERT OR IGNORE INTO {}(discord_id, two_stars_count, three_stars_count, four_stars_count) VALUES (?, ?, ?, ?)".format(chara), (roll_info['user_id'], 0, 0, 0)) 
        c.execute('''
                  UPDATE {} 
                  SET 
                  two_stars_count = two_stars_count + ?, 
                  three_stars_count = three_stars_count + ?, 
                  four_stars_count = four_stars_count + ? 
                  WHERE discord_id = ?
                  '''.format(chara), (roll_info['chara'][chara]['2'], roll_info['chara'][chara]['3'], roll_info['chara'][chara]['4'], roll_info['user_id']))
    conn.commit()

async def get_roll_info(user, *character):
    from commands.database_handler import create_connection
    conn = create_connection()           
    c = conn.cursor()
    table = "user_roll_stats" if not character else character[0]
    if user == 523337807847227402: # Bot
        query = f"SELECT SUM(two_stars_count), SUM(three_stars_count), SUM(four_stars_count) FROM user_roll_stats"
    else:
        query = f"SELECT * FROM {table} WHERE discord_id = {user}"
    r = c.execute(query)
    return r.fetchall()

async def get_roll_leaderboards_info(*character):
    from commands.database_handler import create_connection
    conn = create_connection()           
    c = conn.cursor()
    table = "user_roll_stats" if not character else character[0]
    r = c.execute(f"SELECT * FROM {table} INNER JOIN users ON users.discord_id = {table}.discord_id ORDER BY two_stars_count DESC LIMIT 20")
    return r.fetchall()

@ctime
async def update_roll_album_db(roll_info):
    album_db = 'data/databases/albums.json'
    db = TinyDB(album_db)
    success = True
    q = Query()
    user_check = db.search(q.user_id == roll_info['user_id'])
    if not user_check:
        try:
            db.upsert({'user_id': roll_info['user_id'],
                       'two_star_ids': (roll_info['card_ids']['two_star_ids']),
                       'three_star_ids': (roll_info['card_ids']['three_star_ids']),
                       'four_star_ids': (roll_info['card_ids']['four_star_ids'])
                      }, where('user_id') == roll_info['user_id']) 
        except Exception as e:
            print(e)
            success = False
    else:
        user_info = user_check[0]
        # Sets are supposedly faster than lists at checking if a value exists, so use that
        for rarity in roll_info['card_ids']:
            u = set(user_info[rarity])
            u.update(set(roll_info['card_ids'][rarity]))
            user_info[rarity] = list(u)
        try:
            db.upsert({'user_id': user_info['user_id'],
                       'two_star_ids': user_info['two_star_ids'],
                       'three_star_ids': user_info['three_star_ids'],
                       'four_star_ids': user_info['four_star_ids']
                      }, where('user_id') == user_info['user_id']) 
        except Exception as e:
            print(e)
            success = False
 
@ctime
async def get_album_card_ids(user):
    album_db = 'data/databases/albums.json'
    db = TinyDB(album_db)
    success = True
    q = Query()
    album_card_ids = db.search(q.user_id == user)
    return album_card_ids

@ctime
def add_user_to_premium_db(user: User, guild: Guild, event_id, server: str):
    db = TinyDB(premium_db)
    success = True
    try:
        db.upsert({'user': user,
                   'guild': guild,
                   'event_id': event_id,
                   'server': server
                   }, where('guild') == guild)
    except Exception as e:
        print(e)
        success = False
    if success:
        text = f'User {user} has been added as a premium user for event id {event_id}'
    else:
        text = f'Failed adding user {user} as a premium user for event id {event_id}'
    return text    
    
#######################
#     Bot Updates     #
#######################


def AddChannelToBotUpdatesDatabase(channel: TextChannel):
    db = TinyDB(botupdatesDB)
    success = True
    try:
        db.upsert({'name': channel.name,
                   'guild': channel.guild.id,
                   'guildName': channel.guild.name,
                   'id': channel.id
                   }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + \
            " will receive bot updates" 
    else:
        text = "Failed adding " + channel.name + \
            " to the bot updates list" 
    return text


def RemoveChannelFromBotUpdatesDatabase(channel: TextChannel):
    db = TinyDB(botupdatesDB)
    success = True
    try:
        db.remove((where('id') == channel.id) & (
            where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + \
            " removed from receiving bot updates" 
    else:
        text = "Failed removing " + channel.name + \
            " from receiving bot updates" 
    return text


def GetBotChannelsToPost():
    db = TinyDB(botupdatesDB)
    ids = list()
    try:
        saved = db.all()
        for i in saved:
            ids.append(i['id'])
    except Exception as e:
        print(e)
    return ids

#######################
#     T10 Updates     #
#######################
def addChannelToDatabase(channel: TextChannel, interval: int, server: str):
    success = True
    if server == 'en':
        if(interval == 2):
            db = TinyDB(eventCheckDb2min)
            interval = '2 minute'
        if(interval == 1):
            db = TinyDB(eventCheckDb1min)
            interval = '1 minute'
        if(interval == 3600):
            db = TinyDB(eventCheckDb1hr)
            interval = '1 hour'
    else:
        if(interval == 2):
            db = TinyDB(jp2MinuteTracking)
            interval = '2 minute'
        if(interval == 3600):
            db = TinyDB(jp1HourTracking)
            interval = '1 hour'
        
    try:
        db.upsert({'name': channel.name,
                   'guild': channel.guild.id,
                   'guildName': channel.guild.name,
                   'id': channel.id
                  }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " will receive %s updates for the %s server" %(interval,server)
    else:
        text = "Failed adding " + channel.name + " to the %s %s tracking list" %(server, interval)
    return text

def removeChannelFromDatabase(channel: TextChannel, interval: int, server: str):
    success = True
    if server == 'en':
        if(interval == 2):
                db = TinyDB(eventCheckDb2min)
                interval = '2 minute'
        if(interval == 1):
                db = TinyDB(eventCheckDb1min)
                interval = '1 minute'
        if(interval == 3600):
                db = TinyDB(eventCheckDb1hr)
                interval = '1 hour'
    else:
        if(interval == 2):
                db = TinyDB(jp2MinuteTracking)
                interval = '2 minute'
        if(interval == 3600):
                db = TinyDB(jp1HourTracking)
                interval = '1 hour'
    try:
        db.remove((where('id') == channel.id) & (where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " removed from receiving %s %s t10 updates" %(interval,server)
    else:
        text = "Failed removing " + channel.name + " from receiving %s %s t10 updates" %(interval,server)
    return text

def removeChannelFromDatabaseSongs(channel: TextChannel):
    success = True
    db = TinyDB(songUpdates1Min)
    try:
        db.remove((where('id') == channel.id) & (where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " removed from receiving 1 minute song updates" 
    else:
        text = "Failed removing " + channel.name + " from receiving 1 minute song updates" 
    return text


def addChannelToDatabaseSongs(channel: TextChannel):
    success = True
    db = TinyDB(songUpdates1Min)
    try:
        db.upsert({'name': channel.name,
                'guild': channel.guild.id,
                'guildName': channel.guild.name,
                'id': channel.id
                }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " will receive 1 minute song updates" 
    else:
        text = "Failed adding " + channel.name + " to the song update list" 
    return text

#######################
#    Event Updates    #
#######################
def addChannelToCutoffDatabase(channel: TextChannel, tier: int, server: str):
    success = True
    db = f"databases/cutoff_updates/{server}_t{tier}.json"
    db = TinyDB(db)
    try:
        db.upsert({'name': channel.name,
                'guild': channel.guild.id,
                'guildName': channel.guild.name,
                'id': channel.id
                }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False
    if success:
        text = "Channel " + channel.name + " will receive t%s updates" %str(tier)
    else:
        text = "Failed adding " + channel.name + " to the t%s updates list" %str(tier)
    return text

def rmChannelFromCutoffDatabase(channel: TextChannel, tier: int, server: str):
    success = True
    db = f"databases/cutoff_updates/{server}_t{tier}.json"
    db = TinyDB(db)
    try:
        db.remove((where('id') == channel.id) & (where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False
    if success:
        text = "Channel " + channel.name + " removed from receiving t%s updates" %str(tier)
    else:
        text = "Failed removing " + channel.name + " from receiving t%s updates"%str(tier)
    return text

def getCutoffChannels(tier: int, server: str):
    ids = list()
    db = f"databases/cutoff_updates/{server}_t{tier}.json"
    db = TinyDB(db)
    try:
        saved = db.all()
        for i in saved:
            ids.append(i['id'])
    except Exception as e:
        print(e)
    return ids

def addUpdatesToDatabase(channel: TextChannel, server: str):
    success = True
    if(server == 'en'):
        db = TinyDB(enEventUpdatesDB)
    elif(server == 'jp'):
        db = TinyDB(jpEventUpdatesDB)
    try:
        db.upsert({'name': channel.name,
                'guild': channel.guild.id,
                'guildName': channel.guild.name,
                'id': channel.id
                }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " will receive %s event updates." %server.upper()
    else:
        text = "Failed adding " + channel.name + " to the %s event updates list." %server.upper()

    return text

def removeUpdatesFromDatabase(channel: TextChannel, server: str):
    success = True
    if(server == 'en'):
        db = TinyDB(enEventUpdatesDB)
    elif(server == 'jp'):
        db = TinyDB(jpEventUpdatesDB)
    try:
        db.remove((where('id') == channel.id) & (where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False
    if success:
        text = "Channel " + channel.name + " removed from receiving %s event updates" %server.upper()
    else:
        text = "Failed removing " + channel.name + " from receiving %s event updates" %server.upper()
    return text

def getChannelsToPost(interval: int, server: str):
    ids = list()
    if server == 'en':
        if(interval == 2):
            db = TinyDB(eventCheckDb2min)
        if(interval == 1):
            db = TinyDB(songUpdates1Min)
        if(interval == 3600):
            db = TinyDB(eventCheckDb1hr)
            interval = '1 hour'
    else:
        if(interval == 2):
            db = TinyDB(jp2MinuteTracking)
        if(interval == 3600):
            db = TinyDB(jp1HourTracking)
    try:
        saved = db.all()
        for i in saved:
            ids.append(i['id'])
    except Exception as e:
        print(e)
    return ids

def updatesDB(server: str):
    ids = list()
    if(server == 'en'):
        db = TinyDB(enEventUpdatesDB)
    elif(server == 'jp'):
        db = TinyDB(jpEventUpdatesDB)

    try:
        saved = db.all()
        for i in saved:
            ids.append(i['id'])
    except Exception as e:
        print(e)
    return ids

def dumpWholeDb(interval: int):
    ids = list()
    if(interval == 1):
        db = TinyDB(songUpdates1Min)
    if(interval == 2):
        db = TinyDB(eventCheckDb2min)
    elif interval == 3600:
        db = TinyDB(eventCheckDb1hr)
    elif interval == 100:
        db = TinyDB(t100DB)
    elif interval == 1000:
        db = TinyDB(t1000DB)
    saved = db.all()
    for i in saved:
        ids.append(i['guildName'])
    return ids


#######################
#     News Updates    #
#######################
def addChannelToNewsDatabase(channel: TextChannel, server: str):
    success = True
    if(server == 'en'):
        db = TinyDB(bestdoriENNewsDB)
    elif(server == 'jp'):
        db = TinyDB(bestdoriJPNewsDB)
    elif(server == 'cn'):
        db = TinyDB(bestdoriCNNewsDB)
    else:
        db = TinyDB(bestdoriAllNewsDB)
    try:
        db.upsert({'name': channel.name,
                'guild': channel.guild.id,
                'guildName': channel.guild.name,
                'id': channel.id
                }, where('id') == channel.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Channel " + channel.name + " will receive %s server patch updates from Bestdori." % server.upper()
    else:
        text = "Failed adding " + channel.name + " to the %s server patch updates list." % server.upper()
    return text

def removelChannelFromNewsDatabase(channel: TextChannel, server: str):
    success = True
    if(server == 'en'):
        db = TinyDB(bestdoriENNewsDB)
    elif(server == 'jp'):
        db = TinyDB(bestdoriJPNewsDB)
    elif(server == 'cn'):
        db = TinyDB(bestdoriCNNewsDB)
    else:
        db = TinyDB(bestdoriAllNewsDB)

    try:
        db.remove((where('id') == channel.id) & (where('guild') == channel.guild.id))
    except Exception as e:
        print(e)
        success = False
    if success:
        text = "Channel " + channel.name + " removed from receiving %s server patch updates" % server.upper()
    else:
        text = "Failed removing " + channel.name + " from receiving %s server patch updates" % server.upper()
    return text

def getNewsChannelsToPost(server: str):
    ids = list()
    if(server == 'en'):
        db = TinyDB(bestdoriENNewsDB)
    elif(server == 'jp'):
        db = TinyDB(bestdoriJPNewsDB)
    elif(server ==  'cn'):
        db = TinyDB(bestdoriCNNewsDB)
    else:
        db = TinyDB (bestdoriAllNewsDB)
    try:
        saved = db.all()
        for i in saved:
            ids.append(i['id'])
    except Exception as e:
        print(e)
    return ids


##################
#     Roles      #
##################
def CheckMessageForReactAssignment(msgID: int):
    db = TinyDB('databases/reactbasedroles.json')
    queryBuilder = Query()
    if db.contains(queryBuilder.msgID == msgID):
        return True
    else:
        return False

def GetReactAssignmentList(msgID: int):
    db = TinyDB('databases/reactbasedroles.json')
    queryBuilder = Query()
    document = db.get(queryBuilder.msgID == msgID)
    return document['reactList']

def CheckRoleForAssignability(RoleName: str, GuildID: int):
    db = TinyDB('databases/selfassignableroles.json')
    QueryBuilder = Query()
    AllServerRoles = db.search(QueryBuilder.GuildID == GuildID)
    RoleFound = bool

    for x in AllServerRoles: 
        if RoleFound == True:
            break
        if RoleName in x.values():
            RoleFound = True
        else:
            RoleFound = False
    return RoleFound

def RemoveRoleFromAssingability(RoleName: str, GuildID: int):
    db = TinyDB('databases/selfassignableroles.json')
    QueryBuilder = Query()
    AllServerRoles = db.search(QueryBuilder.GuildID == GuildID)
    RoleFound = bool
    for x in AllServerRoles: 
        if RoleFound == True:
            break
        if RoleName in x.values():
            from tinydb.operations import delete
            RoleFound = True
            db.remove((QueryBuilder.RoleName == RoleName) & (QueryBuilder.GuildID == GuildID))
        else:
            RoleFound = False
    return RoleFound

def GetAllRoles(GuildID: int):
    db = TinyDB('databases/selfassignableroles.json')
    Roles = []
    QueryBuilder = Query()
    AllServerRoles = db.search(QueryBuilder.GuildID == GuildID)
    for x in AllServerRoles:
        Roles.append([x['RoleName']])
    return Roles

def AddRoleToDatabase(channel: TextChannel, role: str):
    success = True
    db = TinyDB('databases/selfassignableroles.json') 
    try:
        db.upsert({'GuildID': channel.guild.id,
                'GuildName': channel.guild.name,
                'RoleName' : role
                }, where('id') == channel.guild.id)

    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Role %s successfully added to the self assignable roles for %s" % (
            role, channel.guild.name)
    else:
        text = "Failed adding role %s to the self assignable roles for %s" % (
            role, channel.guild.name)
    return text

def AddReactToDatabase(msgID: int, data: dict):
    success = True
    db = TinyDB('databases/reactbasedroles.json')
    try:
        db.upsert({'msgID': msgID,
                'reactList': data
                }, where('msgID') == msgID)

    except Exception as e:
        print(e)
        success = False

    if success:
        text = f"Updated values for valid roles and emoji for message {msgID}."
    else:
        text = f"Failed to update/enable message {msgID} for reaction based role assignment."
    return text

def RemoveReactFromDatabase(msgID: int):
    success = True
    db = TinyDB('databases/reactbasedroles.json')
    try:
        db.remove(where('msgID') == msgID)

    except Exception as e:
        print(e)
        success = False

    if success:
        text = f"Message {msgID} disabled for reaction based role assignment. Stored values for valid roles and emoji."
    else:
        text = f"Failed to remove message {msgID} for reaction based role assignment."
    return text

##################
#     Misc       #
##################
def addPrefixToDatabase(guild: Guild, prefix: str):
    success = True

    try:
        db = TinyDB(prefixDb)
        db.upsert({'id': guild.id,
                   'prefix': prefix
        }, where('id') == guild.id)
    except Exception as e:
        print(e)
        success = False

    if success:
        text = "Prefix " + prefix + " set for server " + str(guild.name)
    else:
        text = "Failed adding " + prefix + " to the prefix list"

    return text
