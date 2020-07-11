from commands.formatting.TimeCommands import GetEventTimeLeftSeconds, GetCurrentTime
from commands.apiFunctions import GetSongMetaAPI, GetSongAPI
from tabulate import tabulate
from time import strftime
from time import gmtime
from operator import itemgetter

from discord.channel import TextChannel
from discord.guild import Guild
import math
import time
import discord
#######################
#    Game Commands    #
#######################
def findRank(rank: int):
    xpTable = xpTableFnc()
    xp = xpTable[rank]
    return xp

def xpTableFnc():
    xpTable = [0, 0, 10, 160, 1360, 2960, 3960, 7360, 10160, 13360, 16960, 20960, 25360, 30160, 35360, 40960, 46960, 53280, 59920, 66880, 74160, 81760, 89680, 97920, 106480, 115360, 124560, 134080, 143920, 154080, 164560, 175360, 186480, 197920, 209680, 221760, 234160, 246880, 259920, 273280, 286960, 300960, 315280, 329920, 344880, 360160, 375760, 391680, 407920, 424480, 441360, 458560, 476080, 493920, 512080, 530560, 549360, 568480, 587920, 607680, 627760, 648160, 668880, 689920, 711280, 732960, 754960, 777280, 799920, 822880, 846160, 869790, 893680, 917920, 942480, 967360, 992560, 1018080, 1043920, 1070080, 1096560, 1123360, 1150480, 1177920, 1205680, 1233760, 1262160, 1290880, 1319920, 1349280, 1378960, 1408960, 1439280, 1469920, 1500880, 1532160, 1563760, 1595680, 1627920, 1660480, 1693360, 1728800, 1766800, 1807360, 1850480, 1896160, 1945680, 1999040, 2056240, 2117280, 2182160, 2251520, 2325360, 2403680, 2486480, 2573760, 2665840, 2762720, 2864400, 2970880, 3082160, 3198400, 3319600, 3445760, 3576880, 3712960, 3854080, 4000240, 4151440, 4307680, 4468960, 4635320, 4806760, 4983280, 5164880, 5351560, 5543340, 5740220, 5942200, 6149280, 6361460, 6578750, 6801150, 7028660, 7261280, 7499010, 7741860, 7989830, 8242920, 8501130, 8764460, 9032910, 9306480, 9585170, 9868980, 10157910, 10451960, 10751130, 11055420, 11364830, 11679360, 11999010, 12323780, 12653670, 12988680, 13328810, 13674060, 14024430, 14379920, 14740530, 15106260, 15477110, 15853080, 16234170, 16620380, 17011710, 17408160, 17809730, 18216420, 18628230, 19045160, 19467210, 19894380, 20326670, 20764080, 21206610, 21654260, 22107030, 22564920, 23027930, 23496060, 23969310, 24447680, 24931170, 25419780, 25913510, 26412360, 26916330, 27425420, 27939630, 28458960, 28983410, 29512980, 30047670, 30587480, 31132410, 31682460, 32237630, 32797920, 33363330, 33933860, 34509510, 35090280, 35676170, 36267180, 36863310, 37464560, 38070930, 38682420, 39299030, 39920760, 40547610, 41179580, 41816670, 42458880, 43106210, 43758660, 44416230, 45078290, 45746730, 46419660, 47097710, 47780880, 48469170, 49162580, 49861110, 50564760, 51273530, 51987420, 52706430, 53430560, 54159810, 54894180, 55633670, 56378280, 57128010, 57882860, 58642830, 59407920, 60178130, 60953460, 61733910, 62519480, 63310170, 64105980, 64906910, 65712960, 66524130, 67340420, 68161830, 68988360, 68920010, 70656780, 71498670, 72345680, 73197810, 74055060, 74917430, 75784920, 76657530, 77535260, 78418110, 79306080, 80199170, 81097380, 82000710, 82909160, 83822730, 84741420, 85665230, 86594160, 87528210, 88467380, 89411670, 90361080, 91315610, 92275260, 93240030, 94209920, 95184930, 96165060, 97150310, 98140680, 99136170, 100136780, 101142510, 102153360, 103169330, 104190420, 105216630, 106247960]
    return xpTable

def getXPPerFlame(flamesUsed: int):
    if ((flamesUsed) == 1):
        xp = 2500
    elif((flamesUsed) == 2):
        xp = 3000
    elif ((flamesUsed) == 3):
        xp = 3500
    return xp

def getEPPerFlame(flamesUsed: int):
    if ((flamesUsed) == 1):
        flamesEPModifier = 5
    elif((flamesUsed) == 2):
        flamesEPModifier = 10
    else:
        flamesEPModifier = 15
    return flamesEPModifier

async def GetSongInfo(songName: str):
    songAPI = await GetSongAPI()
    for key in songAPI:
        element = songAPI[key]['musicTitle'][1]
        if(element is None):
            element = songAPI[key]['musicTitle'][0]
        if(element == 'R・I・O・T'):
            element = 'Riot'
        if(element == 'KIZUNA MUSIC♪'):
            element = 'KIZUNA MUSIC'
        if(element == songName or element.lower() == songName):
            songID = key
    songEZDif = songAPI[songID]['difficulty']['0']['playLevel']
    songEZNotes = songAPI[songID]['notes']['0']
    songNMDif = songAPI[songID]['difficulty']['1']['playLevel']
    songNMNotes = songAPI[songID]['notes']['1']
    songHDDif = songAPI[songID]['difficulty']['2']['playLevel']
    songHDNotes = songAPI[songID]['notes']['2']
    songEXDif = songAPI[songID]['difficulty']['3']['playLevel']
    songEXNotes = songAPI[songID]['notes']['3']
    songBPM = songAPI[songID]['bpm']['0'][0]['bpm']

    songLengthS = int(songAPI[songID]['length'])
    m, s = divmod(songLengthS, 60)
    songLength = ('{:02d}:{:02d}'.format(m, s))
    
    songDifString = [songEZDif,songNMDif,songHDDif,songEXDif]
    songDifString = str(songEZDif) + "  " + str(songNMDif) + "  " + str(songHDDif) + "  " + str(songEXDif)

    songNotesString = str(songEZNotes) + " " + str(songNMNotes) + " " + str(songHDNotes) + " " + str(songEXNotes)

    songInfoOutput = ("```" + tabulate([["Song Name",songName],["Song ID",songID],["Song BPM",songBPM],["Song Length",songLength],["Difficulties", songDifString],["Note Count", songNotesString]],tablefmt="plain") + "```")
    return songInfoOutput

async def GetSongMetaOutput(fever: bool, songs: tuple = []):
    songNameAPI = await GetSongAPI()
    songMetaAPI = await GetSongMetaAPI()
    songWeightList = []
    addedSongs = []

    if songs:
        # Get APIs
        
        # Find the IDs for the input
        #So 5.3.2 = [2.7628, 1.0763, 3.3251, 1.488]
        #Means that song (id = 5) on expert (difficulty = 3) on a 7 second skill (duration = 2 + 5) has those meta numbers.
        #First two = non fever, so if the skill is 60% then song score = 2.7628 + 1.0763 * 60%    
        for song in songs:
            for x in songNameAPI:
                try:
                    if song.lower() in (songNameAPI[x]['musicTitle'][1]).lower():
                        addedSongs.append([songNameAPI[x]['musicTitle'][1],x])
                        break
                except:
                    if song.lower() in (songNameAPI[x]['musicTitle'][0]).lower():
                        addedSongs.append([songNameAPI[x]['musicTitle'][0],x])
                        break
        if addedSongs:
            for song in addedSongs:
                if "4" in songMetaAPI[song[1]]:
                    songValues = songMetaAPI[song[1]]["4"]["7"] 
                    songLength = songNameAPI[song[1]]['length']
                    songLength = strftime("%H:%M:%S", gmtime(songLength))
                    if fever:
                        songWeightList.append([song[0] + '(SP)', round(((songValues[2] + songValues[3] * 2) * 1.1) * 100), songLength])
                    else:
                        songWeightList.append([song[0] + '(SP)', round(((songValues[0] + songValues[1] * 2) * 1.1) * 100), songLength])
                songValues = songMetaAPI[song[1]]["3"]["7"] 
                songLength = songNameAPI[song[1]]['length']
                songLength = strftime("%H:%M:%S", gmtime(songLength))
                if fever:
                    songWeightList.append([song[0], round(((songValues[2] + songValues[3] * 2) * 1.1) * 100), songLength])
                else:
                    songWeightList.append([song[0], round(((songValues[0] + songValues[1] * 2) * 1.1) * 100), songLength])

        if songWeightList:
            songWeightList = sorted(songWeightList,key=itemgetter(1),reverse=True)
        output = ("```" + tabulate(songWeightList,tablefmt="plain",headers=["Song","Score %","Length"]) + "```")
    else:
        for x in songMetaAPI:
            if "4" in songMetaAPI[x]:
                songValues = songMetaAPI[x]["4"]["7"] 
                try:
                    if songNameAPI[x]['musicTitle'][1] != None:
                        songName = songNameAPI[x]['musicTitle'][1]
                    else:
                        songName = songNameAPI[x]['musicTitle'][0]
                except:
                    songName = songNameAPI[x]['musicTitle'][0]
                songLength = songNameAPI[x]['length']
                songLength = strftime("%H:%M:%S", gmtime(songLength))
                if fever:
                    songWeightList.append([songName + '(SP)', round(((songValues[2] + songValues[3] * 2) * 1.1) * 100), songLength])
                else:
                    songWeightList.append([songName + '(SP)', round(((songValues[0] + songValues[1] * 2) * 1.1) * 100), songLength])
            songValues = songMetaAPI[x]["3"]["7"] 
            try:
                if songNameAPI[x]['musicTitle'][1] != None:
                    songName = songNameAPI[x]['musicTitle'][1]
                else:
                    songName = songNameAPI[x]['musicTitle'][0]
            except:
                songName = songNameAPI[x]['musicTitle'][0]
            songLength = songNameAPI[x]['length']
            songLength = strftime("%H:%M:%S", gmtime(songLength))
            if fever:
                songWeightList.append([songName, round(((songValues[2] + songValues[3] * 2) * 1.1) * 100), songLength])
            else:
                songWeightList.append([songName, round(((songValues[0] + songValues[1] * 2) * 1.1) * 100), songLength])
        if songWeightList:
            songWeightList = sorted(songWeightList,key=itemgetter(1),reverse=True)
            songWeightList = songWeightList[:20]
            output = ("```" + tabulate(songWeightList,tablefmt="plain",headers=["Song","Score %","Length"]) + "```")
    return output
    



async def GetStarsUsedOutput(epPerSong: int, begRank: int, begEP: int, targetEP: int, flamesUsed: int, *args):
    if(begRank > 300):
        starsUsedOutputString = "Beginning rank can't be over 300."
    else:
        xpPerFlame = getXPPerFlame(flamesUsed)
        #, timeleft: int = timeLeftInt('en')
        #songs played 
        songsPlayed = (targetEP - begEP) / epPerSong
        
        #beg xp
        if begRank != 300:
            beginningXP = findRank(begRank)

            #xp gained + end xp 
            xpGained = xpPerFlame * songsPlayed
            endingXP = beginningXP + xpGained
            xpTable = xpTableFnc()
            
            if endingXP > xpTable[-1]:
                endRank = 300
            else:
            
                for x in range(len(xpTable)):
                    if(endingXP < xpTable[x]):
                        endRank = x-1
                        break
                    elif(endingXP == xpTable[x]):
                        endRank = x
                        break
        else:
            endRank = 300
        #time
        from commands.formatting.EventCommands import GetCurrentEventID

        if(args):
            EventID = await GetCurrentEventID(args[0])
            if(args[0] == 'en'):
                timeLeftHrs = await GetEventTimeLeftSeconds('en', EventID) / 3600
            elif(args[0] == 'jp'):
                timeLeftHrs = await GetEventTimeLeftSeconds('jp', EventID) / 3600
            else: 
                timeLeftHrs = args[0]
        else:
            EventID = await GetCurrentEventID('en')
            timeLeftHrs = await GetEventTimeLeftSeconds('en', EventID) / 3600


        #rankups
        rankUpAmt = endRank - begRank
        if(rankUpAmt <= 0):
            rankUpAmt = 1
        
        #other stuff
        naturalFlames = (32 * (int(timeLeftHrs) / 24)) # assuming 16 hours efficient
        ptsPerRefill = ((epPerSong / flamesUsed) * 10)
        ptsFromRankup = (rankUpAmt * ((epPerSong / flamesUsed) * 10))
        ptsNaturally = (epPerSong / flamesUsed) * naturalFlames

        #time spent
        timeSpent = math.floor((songsPlayed * 150) / 3600) # seconds
        
        #gems used
        starsUsed = ((((targetEP - begEP) - ptsNaturally - ptsFromRankup) / ptsPerRefill) * 100)
        if(starsUsed < 0):
            starsUsed = 0
        else:
            starsUsed = math.ceil(starsUsed / 100.00) * 100

        starsUsedOutputString = ("```" + tabulate([['Stars Used', "{:,}".format(starsUsed)],['Target', "{:,}".format(targetEP)],['Beginning Rank', begRank],['Ending Rank', endRank],['Hours Spent', timeSpent]],tablefmt="plain") + "```")
    return starsUsedOutputString

async def GetCoastingOutput(server: str, epPerSong: int, currentEP: int):
    if epPerSong == 0:
        coastingOutputString = ("```" + tabulate([["Ending EP", "{:,}".format(currentEP)],["Hours Left", "{:,}".format(0)],["Songs Played", "{:,}".format(0)]],tablefmt="plain") + "```")
    else:
        from commands.formatting.EventCommands import GetCurrentEventID
        EventID = await GetCurrentEventID(server)
        TimeLeft = await GetEventTimeLeftSeconds(server, EventID)
        if(TimeLeft < 0):
            coastingOutputString = "The event is completed."
        else:
            hours = TimeLeft / 60 / 60
            daysofAds = math.floor(hours / 24)
            epPerFlame = epPerSong / 3
            epFromAds = (daysofAds * 5) * epPerFlame
            naturalSongsLeft = math.floor((2 * hours) / 3)
            epAtEnd = currentEP + (naturalSongsLeft * epPerSong) + (epFromAds)
            totalSongs = naturalSongsLeft + ((daysofAds * 5) / 3)
            epAtEnd = round(epAtEnd)
            coastingOutputString = ("```" + tabulate([["Ending EP", "{:,}".format(epAtEnd)],["Hours Left", "{:,}".format(math.floor(hours))],["Songs Played", "{:,}".format(round(totalSongs))]],tablefmt="plain") + "```")
        return coastingOutputString

def GetEPGainOutput(yourScore: int, multiScore: int, bpPercent: int, flamesUsed: int, eventType: int, bbPlace: int = 0): 

    bpPercentModifier = (bpPercent / 100) + 1

    epPerFlame = getEPPerFlame(flamesUsed)
    if(eventType == 1):
        eventScaling = 10000
        eventBase = 50
    elif (eventType == 2):
        eventScaling = 13000
        eventBase = 40
    elif (eventType == 3):
        eventScaling = 25000
        eventBase = 20
    elif (eventType == 4):
        eventScaling = 550
        eventBase = 1
    if (eventType == 1 or eventType == 2 or eventType == 3):
        ep = eventBase
        teamScore = multiScore - yourScore
        if (yourScore <= 1600000):
            ep += math.floor(yourScore / eventScaling)
        else:
            ep += math.floor(1600000 / eventScaling)
            if (yourScore <= 1750000):
                ep += math.floor((yourScore - 1600000) / eventScaling / 2)
            else:
                ep += math.floor((1750000 - 1600000) / eventScaling / 2)
                if (yourScore <= 2000000):
                    ep += math.floor((yourScore - 1750000) / eventScaling / 3)
                else:
                    ep += math.floor((2000000 - 1750000) / eventScaling / 3)
                    ep += math.floor((yourScore - 2000000) / eventScaling / 4)      
        if (teamScore <= 6400000):
            ep += math.floor(teamScore / eventScaling / 10)
        else:
            ep += math.floor(6400000 / eventScaling / 10)
            if (teamScore <= 7000000):
                ep += math.floor((teamScore - 6400000) / eventScaling / 10 / 2)
            else:
                ep += math.floor((7000000 - 6400000) / eventScaling / 10 / 2)
                if (teamScore <= 8000000):
                    ep += math.floor((teamScore - 7000000) / eventScaling / 10 / 3)
                else:
                    ep += math.floor((8000000 - 7000000) / eventScaling / 10 / 3)
                    ep += math.floor((teamScore - 8000000) / eventScaling / 10 / 4)

        ep = (ep * bpPercentModifier)
        ep *= epPerFlame
    else:
        #bp calcs
        if (bbPlace == 1):
            bbPlaceBonus = 60
            ep = (bbPlaceBonus + math.floor(yourScore / 5500)) * epPerFlame
        elif(bbPlace == 2):
            bbPlaceBonus = 52
            ep = (bbPlaceBonus + math.floor(yourScore / 5500)) * epPerFlame
        elif(bbPlace == 3):
            bbPlaceBonus = 44
            ep = (bbPlaceBonus + math.floor(yourScore / 5500)) * epPerFlame
        elif(bbPlace == 4):
            bbPlaceBonus = 37
            ep = (bbPlaceBonus + math.floor(yourScore / 5500)) * epPerFlame
        elif(bbPlace == 5):
            bbPlaceBonus = 30
            ep = (bbPlaceBonus + math.floor(yourScore / 5500)) * epPerFlame
    return ep

async def GenerateBandandTitlesImage(members: list, titles: list, server: str):
    from PIL import Image
    from PIL.ImageDraw import Draw
    from PIL.ImageFont import truetype
    from io import BytesIO
    from os import path
    from commands.apiFunctions import GetBestdoriAllTitlesAPI
    TitlesAPI = await GetBestdoriAllTitlesAPI()
    PathToIcons = []
    for x in members:
        IconPath = f'img/icons/full_icons/{x}_trained.png'
        if path.exists(IconPath):
            PathToIcons.append(IconPath)
        else:
            IconPath = f'img/icons/full_icons/{x}.png'
            PathToIcons.append(IconPath)
    images = [Image.open(x) for x in PathToIcons]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights) * 2
    new_im = Image.new('RGBA', (int(total_width), max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]        
    
    Tier = ''
    if len(titles) == 2:
        x_offset = 0
        for Title_ID in titles:
            ImageContents = []
            titleinfo = TitlesAPI[str(Title_ID)]  
            EventTitle = f"img/titles/{server}/{titleinfo['baseImageName'][1]}.png"
            ImageContents.append(EventTitle)
            event = Image.open(ImageContents[0])
            event = event.resize((368,100), Image.ANTIALIAS)
            new_im.paste(event, (x_offset,250), event)

            Tier = titleinfo['rank'][1]
            if Tier != 'none' and Tier != 'normal' and Tier != 'extra':
                TierTitle = f'img/titles/{server}/event_point_{Tier}.png'
                ImageContents.append(TierTitle)
                tier = Image.open(ImageContents[1])
                tier = tier.resize((368,100), Image.ANTIALIAS)
                new_im.paste(tier, (x_offset,250), tier)
            elif Tier == 'normal' or Tier == 'extra':
                TierTitle = f'img/{server}/titles/try_clear_{Tier}.png'
                ImageContents.append(TierTitle)
                tier = Image.open(ImageContents[1])
                tier = tier.resize((368,100), Image.ANTIALIAS)
                new_im.paste(tier, (x_offset,250), tier)

            x_offset += 525
    else:
        x_offset = 250
        ImageContents = []
        titleinfo = TitlesAPI[str(titles[0])]  
        EventTitle = f"img/titles/{server}/{titleinfo['baseImageName'][1]}.png"
        ImageContents.append(EventTitle)
        event = Image.open(ImageContents[0])
        event = event.resize((368,100), Image.ANTIALIAS)
        new_im.paste(event, (x_offset,250), event)

        Tier = titleinfo['rank'][1]
        if Tier != 'none':
            TierTitle = f'img/titles/{server}/event_point_{Tier}.png'
            ImageContents.append(TierTitle)
            tier = Image.open(ImageContents[1])
            tier = tier.resize((368,100), Image.ANTIALIAS)
            new_im.paste(tier, (x_offset,250), tier)

        
    
    import uuid
    from discord import File
    FileName = f'{str(uuid.uuid4())}.png'
    SavedFilePath = f'img/imgTmp/{FileName}.png'
    new_im.save(SavedFilePath)
    return FileName, SavedFilePath

async def characterOutput(character: str):
    from commands.apiFunctions import GetBestdoriAllCharasAPI, GetBestdoriCharasAPI
    r = await GetBestdoriAllCharasAPI()
    character = character.capitalize()
    charaId = False
    for x in r:
        if charaId:
            break
        charalist = r[x]['characterName']
        if character in charalist[1]:
            charaId = x
        elif character in charalist[0]:
            charaId = x

    charaApi = await GetBestdoriCharasAPI(int(charaId))
    charaNames = charaApi['characterName'][1] + ' / ' + charaApi['characterName'][0]
    try:
        charaFavFood = '**Favorite Food**: ' + charaApi['profile']['favoriteFood'][1] 
        charaSeiyuu = '**Seiyuu**: ' + charaApi['profile']['characterVoice'][1] 
        charaHatedFood = '**Hated Food**: ' + charaApi['profile']['hatedFood'][1] 
        charaHobbies = '**Hobbies**: ' + charaApi['profile']['hobby'][1] 
        charaAbout = charaApi['profile']['selfIntroduction'][1] 
        charaSchool = '**School**: ' + charaApi['profile']['school'][1]
    except:
        charaFavFood = '**Favorite Food**: ' + charaApi['profile']['favoriteFood'][0] 
        charaSeiyuu = '**Seiyuu**: ' + charaApi['profile']['characterVoice'][0] 
        charaHatedFood = '**Hated Food**: ' + charaApi['profile']['hatedFood'][0] 
        charaHobbies = '**Hobbies**: ' + charaApi['profile']['hobby'][0] 
        charaAbout = charaApi['profile']['selfIntroduction'][0] 
        charaSchool = '**School**: ' + charaApi['profile']['school'][0]

    if 'hanasakigawa_high' in charaSchool:
        charaSchool = '**School**: Hanasakigawa High'
    elif 'haneoka_high' in charaSchool:
        charaSchool = '**School**: Haneoka High'
    elif 'tsukinomori_high' in charaSchool:
        charaSchool = '**School**: Tsukinomori High'

    charaYearAnime = '**Year (anime)**: ' + str(charaApi['profile']['schoolYear'][0])
    charaPosition = '**Position**: ' + charaApi['profile']['part'].capitalize()
    if 'Guitar_vocal' in charaPosition:
        charaPosition = '**Position**: Guitarist + Vocals' 
    charaBirthdayFmt = '**Birthday**: ' + time.strftime("%d %b %Y", time.localtime(int(charaApi['profile']['birthday']) / 1000))
    charaConstellation = '**Constellation**: ' + charaApi['profile']['constellation'].capitalize()
    charaHeight = '**Height**: ' + str(charaApi['profile']['height']) + "cm"
    charaImageURL = 'https://bestdori.com/res/icon/chara_icon_%s.png' %charaId
    charaUrl = 'https://bestdori.com/info/characters/%s' %charaId

    charaInfo = tabulate([[charaSeiyuu], [charaHeight], [charaBirthdayFmt], [charaPosition], [charaConstellation]],tablefmt="plain")
    charaInterests = [charaFavFood,charaHatedFood,charaHobbies]
    charaEdu = [charaSchool, charaYearAnime]
    
    embed=discord.Embed(title=charaNames, url=charaUrl, description=charaAbout)
    embed.set_thumbnail(url=charaImageURL)
    embed.add_field(name='About', value=(charaInfo), inline=True)
    embed.add_field(name='Interests', value='\n'.join(charaInterests), inline=True)
    embed.add_field(name='School', value='\n'.join(charaEdu), inline=True)
    return embed

async def GetLevelOutput(CurrentLevel: int, XPPerSong: int, SongsPlayed: int):
    from commands.formatting.GameCommands import findRank, xpTableFnc
    CurrentXP = findRank(CurrentLevel)
    NewXP = CurrentXP + (XPPerSong * SongsPlayed)
    xpTable = xpTableFnc()
    counter = 0
    if NewXP < xpTable[-1]:
        for xp in xpTable:
            if xp < NewXP < xpTable[counter+1]:
                NewLevel = counter
                break
            counter +=1  
    else:
        NewLevel = 300
    return NewLevel

async def GetLeaderboardsOutput(server: str = 'en', type: str = 'highscores', entries: int = 20):
    from commands.apiFunctions import GetBestdoriPlayerLeaderboardsAPI
    ValidTypes = ['highscores','hs','ranks','rank','fullcombo','fc','cleared']
    if type not in ValidTypes:
        Output = 'Invalid type, please enter one of these valid types: highscores/hs, ranks/rank, fullcombo/fc, or cleared'
    else:
        api = await GetBestdoriPlayerLeaderboardsAPI(server, type, entries)
        TotalEntries = api['count']
        if entries > TotalEntries:
            entries = TotalEntries
        Output = 'Found %s entries. Posting the first %s' %(str(TotalEntries), str(entries)) + '\n'
        Entries = []
        RowCount = 1
        while RowCount <= entries:
            for row in api['rows']:
                if row['user']['nickname']:
                    Entries.append([str(RowCount),row['user']['username'], row['stats'], row['user']['nickname']])
                else:
                    Entries.append([str(RowCount),row['user']['username'], row['stats']])
                RowCount += 1
        Output += "```" + tabulate(Entries,tablefmt="plain",headers=["#", "Player", "Value", "Bestdori Name"]) + "```"
    if len(Output) > 2000:
        Output = 'Output is greater than 2000 characters, please select a smaller list of values to return!'    
    return Output