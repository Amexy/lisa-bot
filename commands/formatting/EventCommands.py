from bs4 import BeautifulSoup
from protodefs.ranks import t10ranks
from startup.login import enICEObject, jpICEObject
from datetime import datetime
from pytz import timezone
import discord, asyncio, time, json

def parseHTML(driver):
    html = driver.page_source
    soup = BeautifulSoup(html,features="html.parser")
    parsedHTML = soup.find_all("td")
    return parsedHTML

def getICEObject(server: str):
    if server == 'en':
        ice = enICEObject
    else:
        ice = jpICEObject
    return ice

async def GetCutoffHistory(server, tier):
    from commands.apiFunctions import GetBestdoriEventArchivesAPI, GetServerAPIKey, GetBestdoriBannersAPI
    from commands.formatting.EventCommands import GetEventName, GetEventAttribute
    from commands.formatting.TimeCommands import GetEventLengthSeconds
    import math
    HistoryAPI = await GetBestdoriEventArchivesAPI()
    Key = await GetServerAPIKey(server)
    Histories = []
    for x in range(1, len(HistoryAPI)):
        x = str(x)
        if HistoryAPI[x]['cutoff'][Key]:
            if tier in HistoryAPI[x]['cutoff'][Key]: # Event 17 for example doesn't have a value for T100, so we need to check if it exists
                Histories.append(HistoryAPI[x]['cutoff'][Key][tier])
            else:
                Histories.append(0) # If we don't add an entry if the event exists, then the EventID result will be incorrect
    # Because of the above `else`, the list may be full of zeros (e.g. En and tier 5000)
    if not all(x==Histories[0] for x in Histories):
        Cutoff = max(Histories) 
        EventID = Histories.index(Cutoff)+ 1
        EventName = await GetEventName(server, EventID)
        Attribute = await GetEventAttribute(EventID)
        BannerAPI = await GetBestdoriBannersAPI(EventID)
        EventLengthHours = await GetEventLengthSeconds(server, EventID) / 3600
        EPPerHour = "{:,}".format(math.floor(Cutoff / EventLengthHours))
        Thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,BannerAPI['assetBundleName'])
        Cutoff = "{:,}".format(Cutoff)
        EventUrl = 'https://bestdori.com/info/events/' + str(EventID)
        if(Attribute == 'powerful'):
            EmbedColor = 0x0ff345a
        elif(Attribute == 'cool'):
            EmbedColor = 0x04057e3
        elif(Attribute == 'pure'):
            EmbedColor = 0x044c527
        else:
            EmbedColor = 0x0ff6600

        embed=discord.Embed(title=EventName, url=EventUrl, color=EmbedColor)
        embed.set_thumbnail(url=Thumbnail)
        embed.add_field(name='Tier', value=tier, inline=True)
        embed.add_field(name='EP', value=Cutoff, inline=True)
        embed.add_field(name='EP Per Hour', value=EPPerHour, inline=True)
        return embed

async def GetEventName(server: str, eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
    Key = await GetServerAPIKey(server)
    api = await GetBestdoriEventAPI(eventid)  
    EventName = api['eventName'][Key]
    return EventName

async def IsEventActive(server: str, eventid: int):
    currentTime = time.time() * 1000
    from commands.apiFunctions import GetBestdoriEventAPI, GetServerAPIKey
    api = await GetBestdoriEventAPI(eventid)
    TimeKey = await GetServerAPIKey(server)
    if api['startAt'][TimeKey]:
        if float(api['startAt'][TimeKey]) < currentTime < float(api['endAt'][TimeKey]):
            return True
        else:
            return False
    else:
        return False

async def GetEventAttribute(eventid: int):
    from commands.apiFunctions import GetBestdoriEventAPI

    api = await GetBestdoriEventAPI(eventid)  
    EventAttribute = api['attributes'][0]['attribute']
    return EventAttribute
    
async def GetCurrentEventID(server: str):
    from commands.apiFunctions import GetBestdoriAllEventsAPI, GetServerAPIKey
    currentTime = time.time() * 1000
    CurrentEventID = ''
    TimeKey = await GetServerAPIKey(server)
    api = await GetBestdoriAllEventsAPI()
    for event in api:
        if api[event]['startAt'][TimeKey]:
            if float(api[event]['startAt'][TimeKey]) < currentTime < float(api[event]['endAt'][TimeKey]):
                CurrentEventID = event
                break
    if not CurrentEventID:
        try:
            for event in api:
                if float(api[event]['endAt'][TimeKey]) < currentTime < float(api[str(int(event) + 1)]['endAt'][TimeKey]): #In jp's case, there may not be an entry for the next event yet
                    CurrentEventID = event
                    break
        except KeyError:
            CurrentEventID = list(api.keys())[-1]
    if CurrentEventID:
        return CurrentEventID
    else:
        return 0

def GetCutoffJSONFile(Server, Tier):
    if Server == 'en':
        if Tier == 100:
            FileName = 'databases/ent100.json'
        else:
            FileName = 'databases/ent1000.json'
    elif Server == 'jp':
        if Tier == 100:
            FileName = 'databases/jpt100.json'
        elif Tier == 1000:
            FileName = 'databases/jpt1000.json'
        else:
            FileName = 'databases/jpt2000.json'
    elif Server == 'cn':
        if Tier == 100:
            FileName = 'databases/cnt100.json'
        elif Tier == 1000:
            FileName = 'databases/cnt1000.json'
        else:
            FileName = 'databases/cnt2000.json'
    elif Server == 'tw':
        FileName = 'databases/twt100.json'
    else:
        FileName = 'databases/krt100.json'
    return FileName

def UpdateCutoffJSON(Server, Tier, EventID, Current, Estimate, SmoothingEstimate, EPPerHour):
    FileName = GetCutoffJSONFile(Server, Tier)
    try:
        with open(FileName) as file:
            api = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        # Create the file and add an empty dict to it so we can load the json file
        with open(FileName, 'a+') as file:
            data = {}
            json.dump(data, file, indent=2)
        
        # Load the newly created file
        with open(FileName) as file:
            api = json.load(file)

    # Check if there's an entry for the EventID in the json file 
    if str(EventID) in api:
        if Current in api[str(EventID)]['current']:
            print(f'Current value already in list for event {str(EventID)}')
        else:
            api[str(EventID)]['current'].append(Current)

        if Estimate in api[str(EventID)]['estimate']:
            print(f'Estimate value already in list for event {str(EventID)}')
        else:    
            api[str(EventID)]['estimate'].append(Estimate)

        if SmoothingEstimate in api[str(EventID)]['smoothingestimate']:
            print(f'Smoothing Estimate value already in list for event {str(EventID)}')
        else:    
            api[str(EventID)]['smoothingestimate'].append(SmoothingEstimate)

        if EPPerHour in api[str(EventID)]['epperhour']:
            print(f'EPPerHour value already in list for event {str(EventID)}')
        else:    
            api[str(EventID)]['epperhour'].append(EPPerHour)
            
        with open(FileName, 'w') as f:
            json.dump(api, f)
    # This adds a new key to the dictionary
    else:
        data = {EventID: {
                        "current" : [Current],
                        "estimate" : [Estimate],
                        "smoothingestimate" : [SmoothingEstimate],
                        "epperhour" : [EPPerHour]
                        }
                }
        with open(FileName, 'w') as f:
            api.update(data)
            json.dump(api, f)

def GetUpdatedValues(Server, Tier, EventID, Position):
    FileName = GetCutoffJSONFile(Server, Tier)
    try:
        with open(FileName) as file:
            api = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        with open(FileName, 'a+') as file:
            data = {}
            json.dump(data, file, indent=2)
        with open(FileName) as file:
            api = json.load(file)

    if str(EventID) in api:
        if Position == 'last':
            LastUpdatedCurrent = api[str(EventID)]['current'][-1]
            LastUpdatedEstimate = api[str(EventID)]['estimate'][-1]
            LastUpdatedSmoothingEstimate = api[str(EventID)]['smoothingestimate'][-1]
            LastUpdatedEPPerHour = api[str(EventID)]['epperhour'][-1]
        elif Position == 'secondlast':
            if len(api[str(EventID)]['current']) >= 2:
                LastUpdatedCurrent = api[str(EventID)]['current'][-2]
                LastUpdatedEstimate = api[str(EventID)]['estimate'][-2]
                LastUpdatedSmoothingEstimate = api[str(EventID)]['smoothingestimate'][-2]
                LastUpdatedEPPerHour = api[str(EventID)]['epperhour'][-2]

        return LastUpdatedCurrent, LastUpdatedEstimate, LastUpdatedSmoothingEstimate, LastUpdatedEPPerHour
        

async def GetCutoffFormatting(driver, server: str, tier: int):
    from commands.apiFunctions import GetBestdoriAllEventsAPI, GetBestdoriBannersAPI, GetBestdoriCutoffAPI
    from commands.formatting.TimeCommands import GetTimeLeftString, GetEventProgress, GetEventTimeLeftSeconds, GetEventLengthSeconds, GetEventStartTime
    import math
    eventId = await GetCurrentEventID(server)
    eventAPI = await GetBestdoriAllEventsAPI()
    eventName = eventAPI[str(eventId)]['eventName'][1]
    if eventName is None:
        eventName = eventAPI[str(eventId)]['eventName'][0]

    valid = 'n'
    while valid == 'n':
        if tier != 10:
            if tier == 100:
                eventName = 'T100: ' + eventName
                if server != 'kr' and server != 'tw':               
                    driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[2]').click()
                    await asyncio.sleep(.3)
                    driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[1]').click()
                    await asyncio.sleep(.3)
                else:
                    if server == 'kr':
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[10]/div[2]/div/div/div/a[3]').click()
                        await asyncio.sleep(.5)
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[10]/div[2]/div/div/div/a[5]').click()
                        await asyncio.sleep(.5)
                    else:
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[10]/div[2]/div/div/div/a[5]').click()
                        await asyncio.sleep(.5)
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[10]/div[2]/div/div/div/a[3]').click()
                        await asyncio.sleep(.5)
            elif tier == 1000:
                eventName = 'T1000: ' + eventName
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[1]').click()                
                await asyncio.sleep(.3)
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[2]').click()
                await asyncio.sleep(.5)   
            else:
                eventName = 'T2000: ' + eventName
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[1]').click()                
                await asyncio.sleep(.5)
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[11]/div[2]/div/div/div/a[3]').click()                
                await asyncio.sleep(.5)
            await asyncio.sleep(.5)
            # Have to do this twice to get non smoothed values
            parsedHTMLSmoothed = parseHTML(driver)
            driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[8]/div[2]/div/div/div/a[2]').click()
            parsedHTMLNoSmoothing = parseHTML(driver)
            driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[8]/div[2]/div/div/div/a[1]').click()

            if not parsedHTMLSmoothed:
                valid = 'n'
            else:
                valid = 'y'
            
            # for when the event is completed
            if parsedHTMLSmoothed[2].text == 'Final Cutoff':
                if parsedHTMLSmoothed[3].text == '?':
                    estimate = parsedHTMLSmoothed[9].text    
                    lastupdated = parsedHTMLSmoothed[11].text
                    current = parsedHTMLSmoothed[7].text    
                else:
                    estimate = parsedHTMLSmoothed[7].text
                    lastupdated = parsedHTMLSmoothed[9].text
                    current = parsedHTMLSmoothed[3].text
                estimatenosmoothing = estimate # Because there's only 1 estimate at the end of the event
            else:
                estimate = parsedHTMLSmoothed[5].text
                lastupdated = parsedHTMLSmoothed[7].text
                current = parsedHTMLSmoothed[3].text
                estimatenosmoothing = parsedHTMLNoSmoothing[5].text

        else:
            ice = getICEObject(server)
            valid = 'y'
            eventranking = await t10ranks(ice, server, eventId)
            current = eventranking.top_10.contents[9].event_pts
            current = "{:,}".format(current)
            estimate = "N/A"
            lastupdated  = "Just now!"

    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Eastern'))
    EventLengthSeconds = await GetEventLengthSeconds(server, eventId)
    timeLeft = await GetTimeLeftString(server,eventId)
    #await ctx.send("Grabbing cutoff...")
    prog = await GetEventProgress(server,eventId) 
    prog = str(prog) + '%'
    eventAPI = await GetBestdoriAllEventsAPI()
    bannerAPI = await GetBestdoriBannersAPI(int(eventId))
    bannerName = bannerAPI['assetBundleName']
    eventUrl = 'https://bestdori.com/info/events/' + str(eventId)
    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)
    
    # Get difference in current and estimate values
    LastUpdatedValues = GetUpdatedValues(server, tier, eventId, 'last')


    if LastUpdatedValues:
        if current != LastUpdatedValues[0]:    
            LastUpdatedTime = (await GetBestdoriCutoffAPI(tier))['cutoffs'][-1]['time']
            EventStartTime = await GetEventStartTime(server, eventId)
            ElapsedTimeHours = (LastUpdatedTime - EventStartTime) / 1000 / 3600            
            EPPerHour = math.floor(float(current.replace(',','')) / ElapsedTimeHours)
            if estimate == '?':
                UpdateCutoffJSON(server,tier,eventId,current,"0","0",EPPerHour)     
            else:
                UpdateCutoffJSON(server,tier,eventId,current,estimate,estimatenosmoothing,EPPerHour)     
            LastCurrent = int(LastUpdatedValues[0].replace(',',''))
            LastEstimate = int(LastUpdatedValues[1].replace(',',''))
            LastEstimateNoSmoothing = int(LastUpdatedValues[2].replace(',',''))
            LastEPPerHour = LastUpdatedValues[3] #this value is stored as an int
            CurrentDifference = "{:,}".format(int(current.replace(',','')) - LastCurrent)
            EstimateDifference = "{:,}".format(int(estimate.replace(',','')) - LastEstimate)
            EstimateNoSmoothingDifference = "{:,}".format(int(estimatenosmoothing.replace(',','')) - LastEstimateNoSmoothing)
            EPPerHourDifference = EPPerHour - LastEPPerHour
            if int(CurrentDifference.replace(',','')) > 0:
                CurrentDifference = "{:+,}".format(int(CurrentDifference.replace(',','')))
            if int(EstimateDifference.replace(',','')) > 0:
                EstimateDifference = "{:+,}".format(int(EstimateDifference.replace(',','')))
            if int(EstimateNoSmoothingDifference.replace(',','')) > 0:
                EstimateNoSmoothingDifference = "{:+,}".format(int(EstimateNoSmoothingDifference.replace(',','')))
            if  EPPerHourDifference > 0:
                EPPerHourDifference = "{:+,}".format(EPPerHourDifference)
            current = f'{current} ({CurrentDifference})'
            estimate = f'{estimate} ({EstimateDifference})'
            estimatenosmoothing = f'{estimatenosmoothing} ({EstimateNoSmoothingDifference})'
            EPPerHour = f"{'{:,}'.format(EPPerHour)} ({EPPerHourDifference})"
        elif current == LastUpdatedValues[0]:
            try:
                SecondLastUpdatedValues = GetUpdatedValues(server, tier, eventId, 'secondlast')
            except:
                SecondLastUpdatedValues = []
                pass
            if SecondLastUpdatedValues:
                TimeLeftSeconds = await GetEventTimeLeftSeconds(server, eventId)
                ElapsedTimeHours = (EventLengthSeconds - TimeLeftSeconds) / 3600
                EPPerHour = math.floor(float(current.replace(',','')) / ElapsedTimeHours)
                LastCurrent = int(SecondLastUpdatedValues[0].replace(',',''))
                LastEstimate = int(SecondLastUpdatedValues[1].replace(',',''))
                LastEstimateNoSmoothing = int(SecondLastUpdatedValues[2].replace(',',''))
                LastEPPerHour = SecondLastUpdatedValues[3] #this value is stored as an int
                CurrentDifference = "{:,}".format(int(current.replace(',','')) - LastCurrent)
                EstimateDifference = "{:,}".format(int(estimate.replace(',','')) - LastEstimate)
                EstimateNoSmoothingDifference = "{:,}".format(int(estimatenosmoothing.replace(',','')) - LastEstimateNoSmoothing)
                EPPerHourDifference = EPPerHour - LastEPPerHour
                if int(CurrentDifference.replace(',','')) > 0:
                    CurrentDifference = "{:+,}".format(int(CurrentDifference.replace(',','')))
                if int(EstimateDifference.replace(',','')) > 0:
                    EstimateDifference = "{:+,}".format(int(EstimateDifference.replace(',','')))
                if int(EstimateNoSmoothingDifference.replace(',','')) > 0:
                    EstimateNoSmoothingDifference = "{:+,}".format(int(EstimateNoSmoothingDifference.replace(',','')))
                if  EPPerHourDifference > 0:
                    EPPerHourDifference = "{:+,}".format(EPPerHourDifference)
                current = f'{current} ({CurrentDifference})'
                estimate = f'{estimate} ({EstimateDifference})'
                estimatenosmoothing = f'{estimatenosmoothing} ({EstimateNoSmoothingDifference})'
                EPPerHour = f"{'{:,}'.format(EPPerHour)} ({EPPerHourDifference})"
            else:
                EPPerHour = "{:,}".format(LastUpdatedValues[3])
    else:
        LastUpdatedTime = (await GetBestdoriCutoffAPI(tier))['cutoffs'][-1]['time']
        EventStartTime = await GetEventStartTime(server, eventId)
        ElapsedTimeHours = (LastUpdatedTime - EventStartTime) / 1000 / 3600            
        EPPerHour = math.floor(float(current.replace(',','')) / ElapsedTimeHours)
        if estimate == '?':
            UpdateCutoffJSON(server,tier,eventId,current,"0","0",EPPerHour)     
        else:
            UpdateCutoffJSON(server,tier,eventId,current,estimate,estimatenosmoothing,EPPerHour)     
        EPPerHour = "{:,}".format(EPPerHour)
    embed=discord.Embed(title=eventName, url=eventUrl, color=0x09d9fd)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Current', value=current, inline=True)
    embed.add_field(name='EP Per Hour', value=EPPerHour, inline=True)        
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name='Estimate', value=estimate, inline=True)
    embed.add_field(name='Estimate (No Smoothing)', value=estimatenosmoothing, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name='Last Updated', value=lastupdated, inline=True)
    embed.add_field(name='Time Left', value=timeLeft, inline=True)
    embed.add_field(name='Progress', value=prog, inline=True)
    embed.set_footer(text=now_time.strftime(fmt))
    output = embed
    return output





