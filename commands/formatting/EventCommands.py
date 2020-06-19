from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup
from protodefs.ranks import t10ranks
from startup.login import enICEObject, jpICEObject
from datetime import datetime
from pytz import timezone
import discord, asyncio, time, json, sys


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
                try:
                    if float(api[event]['endAt'][TimeKey]) < currentTime < float(api[str(int(event) + 1)]['endAt'][TimeKey]): #In jp's case, there may not be an entry for the next event yet
                        CurrentEventID = event
                        break
                except TypeError: # For between events
                    CurrentEventID = int(event)
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
            LastUpdatedSmoothingEstimate = api[str(EventID)]['estimate'][-1]
            LastUpdatedNoSmoothingEstimate = api[str(
                EventID)]['smoothingestimate'][-1]
            LastUpdatedEPPerHour = api[str(EventID)]['epperhour'][-1]
        elif Position == 'secondlast':
            if len(api[str(EventID)]['current']) >= 2:
                LastUpdatedCurrent = api[str(EventID)]['current'][-2]
                LastUpdatedSmoothingEstimate = api[str(
                    EventID)]['estimate'][-2]
                LastUpdatedNoSmoothingEstimate = api[str(
                    EventID)]['smoothingestimate'][-2]
                LastUpdatedEPPerHour = api[str(EventID)]['epperhour'][-2]

        return LastUpdatedCurrent, LastUpdatedSmoothingEstimate, LastUpdatedNoSmoothingEstimate, LastUpdatedEPPerHour
        
def GetNonSmoothingEstimate(TimeEntries, EPEntries, Rate):
    import numpy as np
    x = np.array(TimeEntries).reshape((-1, 1))
    y = np.array(EPEntries)
    model = LinearRegression().fit(x, y)
    slope, intercept = model.coef_, model.intercept_
    estimate = (intercept + slope + (Rate * slope))
    return estimate, slope, intercept

async def CalculatecutoffEstimates(server, tier, EventID):
    from commands.apiFunctions import GetBestdoriRateAPI, GetTierKey, GetBestdoriCutoffAPI, GetBestdoriEventAPI, GetServerAPIKey
    from protodefs.ranks import GetEventType
    import math
    CutoffAPI = await GetBestdoriCutoffAPI(server, tier)
    EventAPI = await GetBestdoriEventAPI(EventID)
    Key = await GetServerAPIKey(server)
    RatesAPI = await GetBestdoriRateAPI()
    EventType = await GetEventType(EventID)
    TierKey = await GetTierKey(tier)
    if EventType == 'livetry':
        EventType = 'live_try'
    elif EventType == 'mission':
        EventType = 'mission_live'
    for x in RatesAPI:
        if x['type'] == EventType and x['server'] == Key and x['tier'] == TierKey:
            Rate = x['rate']
    LastUpdatedCutoff = CutoffAPI['cutoffs'][-1]['ep']
    EventStartTime = int(EventAPI['startAt'][Key])
    EventEndTime = int(EventAPI['endAt'][Key])
    Duration = EventEndTime - EventStartTime
    TwelveHoursPast = EventStartTime + 43200000
    TwentyFourHoursPast = TwelveHoursPast + 43200000
    TwentyFourHoursBeforeEnd = EventEndTime - 86400000
    TimeEntries = []
    EPEntries = []
    Weights = []
    Ests = [] # Used for graph making
    Slopes = []
    Intercepts = []
    NonSmoothingEstimates = []
    AllTimeEntires = []
    AllEPEntries = []
    EstTimes = []
    for x in CutoffAPI['cutoffs']:
        AllEPEntries.append(x['ep'])
        TimeEntry = int(x['time'])
        TimeDifference = TimeEntry - EventStartTime
        PercentIntoEvent = TimeDifference / Duration
        AllTimeEntires.append(PercentIntoEvent * 100)

        # Store all values past 12 hour mark and 1 day before event ends
        if TimeEntry >= TwelveHoursPast and TimeEntry <= TwentyFourHoursBeforeEnd:
            TimeEntries.append(PercentIntoEvent)
            EPEntries.append(x['ep'])
        if TimeEntry >= TwentyFourHoursPast and TimeEntry <= TwentyFourHoursBeforeEnd and len(EPEntries) >= 5:
            estimate = GetNonSmoothingEstimate(
                TimeEntries, EPEntries, Rate)[0]
            NonSmoothingEstimates.append(estimate)
            Slopes.append(GetNonSmoothingEstimate(
                TimeEntries, EPEntries, Rate)[1])
            Intercepts.append(GetNonSmoothingEstimate(
                TimeEntries, EPEntries, Rate)[2])
            Weights.append(
                [estimate * PercentIntoEvent**2, PercentIntoEvent**2])
            EstTimes.append(PercentIntoEvent * 100)
            Ests.append(estimate[0])
        if TimeEntry >= TwentyFourHoursBeforeEnd:
            # Calculate the last estimate, but use a new weight
            estimate = (Intercepts[-1] + Slopes[-1] + (Rate * Slopes[-1]))
            NonSmoothingEstimates.append(estimate)
            TimeDifference = TimeEntry - EventStartTime
            PercentIntoEvent = TimeDifference / Duration
            Weights.append(
                [estimate * PercentIntoEvent**2, PercentIntoEvent**2])

    TotalWeight = 0
    TotalTime = 0
    for x in Weights:
        TotalWeight += x[0]
        TotalTime += x[1]

    if TimeEntries and EPEntries:
        EstimateNoSmoothing = math.floor(
            GetNonSmoothingEstimate(TimeEntries, EPEntries, Rate)[0])
        try:
            EstimateSmoothing = math.floor(TotalWeight / TotalTime)
        except ZeroDivisionError:
            EstimateSmoothing = 0
    else:
        EstimateSmoothing = 0
        EstimateNoSmoothing = 0
    LastUpdatedTime = CutoffAPI['cutoffs'][-1]['time']
    ElapsedTimeHours = (LastUpdatedTime - EventStartTime) / 1000 / 3600
    EPPerHour = math.floor(LastUpdatedCutoff / ElapsedTimeHours)
    return EstimateSmoothing, EstimateNoSmoothing, EPPerHour, Ests,AllTimeEntires, AllEPEntries,EstTimes

async def CreateGraph(Server, EventID, Tier, CurrentEPValues, CurrentTimes, EstimateEPValues, EstimateTimes):
    import plotly.graph_objects as go
    import os, plotly
    from selenium import webdriver
    import plotly.offline as offline
    fig = go.Figure()
    fig.add_trace(go.Scatter(go.Scatter(x=CurrentTimes,y=CurrentEPValues)))
    fig.add_trace(go.Scatter(go.Scatter(x=EstimateTimes,y=EstimateEPValues)))
    fig.update_xaxes(range=[0,100])
    fig.update_layout(
        xaxis=dict(
            title='Event Progress (%)',
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            title='EP Values',
            showgrid=False,
            zeroline=False,
            showline=True,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),

        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=False,
        template='plotly_dark'
    )
    FileName = f"{EventID}_{Server}_{Tier}.png"
    SavedFile = f"img/graphs/{FileName}"

    with open("config.json") as file:
        config_json = json.load(file)
        driverPath = config_json["chromeDriverPath"]
    offline.plot(fig, image='svg', auto_open=False)
    
    # Just when I thought I was done with this shit
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--headless')
    Driver = webdriver.Chrome(options=options,executable_path=driverPath)
    Driver.set_window_size(1000, 800)
    Driver.get('temp-plot.html')
    await asyncio.sleep(1)
    img = Driver.find_element_by_class_name('svg-container')
    img.screenshot(SavedFile)
    Driver.close()
    from discord import File
    DiscordFileObject = File(SavedFile,filename=FileName)
    return FileName, DiscordFileObject

async def GetCutoffFormatting(server: str, tier: int, graph: bool):
    from commands.apiFunctions import GetBestdoriEventAPI, GetBestdoriBannersAPI, GetBestdoriCutoffAPI, GetBestdoriRateAPI, GetTierKey, GetServerAPIKey
    from commands.formatting.TimeCommands import GetTimeLeftString, GetEventProgress, GetEventTimeLeftSeconds, GetEventLengthSeconds, GetEventStartTime
    import math, time, os
    EventID = await GetCurrentEventID(server)

    CutoffAPI = await GetBestdoriCutoffAPI(server, tier)
    EventAPI = await GetBestdoriEventAPI(EventID)
    Key = await GetServerAPIKey(server)

    LastUpdatedCutoff = CutoffAPI['cutoffs'][-1]['ep']
    LastUpdatedTime = CutoffAPI['cutoffs'][-1]['time'] / 1000
    time = time.time()
    LastUpdatedSeconds = time - LastUpdatedTime
    Days = str(int(LastUpdatedSeconds) // 86400)
    Hours = str(int(LastUpdatedSeconds) // 3600 % 24)
    Minutes = str(int(LastUpdatedSeconds) // 60 % 60)
    LastUpdated = (f"{Days}d {Hours}h {Minutes}m ago")

    EventName = f"T{tier}: {EventAPI['eventName'][Key]}"

    LastUpdatedValues = GetUpdatedValues(server, tier, EventID, 'last')
    if graph:
        GraphInfo = []
    if LastUpdatedValues:
        if LastUpdatedValues[0] == LastUpdatedCutoff:
            EstimateSmoothing = LastUpdatedValues[1]
            EstimateNoSmoothing = LastUpdatedValues[2]
            EPPerHour = LastUpdatedValues[3]
            # If SecondLastUpdatesValues is True, then we can find out the difference from last update
            try:
                SecondLastUpdatedValues = GetUpdatedValues(
                    server, tier, EventID, 'secondlast')
            except:
                SecondLastUpdatedValues = []
                pass
            if SecondLastUpdatedValues:
                LastCurrent = SecondLastUpdatedValues[0]
                LastEstimateSmoothing = SecondLastUpdatedValues[1]
                LastEstimateNoSmoothing = SecondLastUpdatedValues[2]
                LastEPPerHour = SecondLastUpdatedValues[3]  # this value is stored as an int
                CurrentDifference = LastUpdatedCutoff - LastCurrent
                EstimateSmoothingDifference = EstimateSmoothing - LastEstimateSmoothing
                EstimateNoSmoothingDifference = EstimateNoSmoothing - LastEstimateNoSmoothing
                EPPerHourDifference = EPPerHour - LastEPPerHour
                if CurrentDifference > 0:
                    CurrentDifference = "{:+,}".format(CurrentDifference)
                else:
                    CurrentDifference = "{:,}".format(CurrentDifference)
                if EstimateSmoothingDifference > 0:
                    EstimateSmoothingDifference = "{:+,}".format(
                        EstimateSmoothingDifference)
                else:
                    EstimateSmoothingDifference = "{:,}".format(
                        EstimateSmoothingDifference)
                if EstimateNoSmoothingDifference > 0:
                    EstimateNoSmoothingDifference = "{:+,}".format(
                        EstimateNoSmoothingDifference)
                else:
                    EstimateNoSmoothingDifference = "{:,}".format(
                        EstimateNoSmoothingDifference)
                if EPPerHourDifference > 0:
                    EPPerHourDifference = "{:+,}".format(EPPerHourDifference)
                else:
                    EPPerHourDifference = "{:,}".format(EPPerHourDifference)
                LastUpdatedCutoff = "{:,}".format(LastUpdatedCutoff)
                EstimateSmoothing = "{:,}".format(EstimateSmoothing)
                EstimateNoSmoothing = "{:,}".format(EstimateNoSmoothing)
                LastUpdatedCutoff = f'{LastUpdatedCutoff} ({CurrentDifference})'
                EstimateSmoothing = f'{EstimateSmoothing} ({EstimateSmoothingDifference})'
                EstimateNoSmoothing = f'{EstimateNoSmoothing} ({EstimateNoSmoothingDifference})'
                EPPerHour = f"{'{:,}'.format(EPPerHour)} ({EPPerHourDifference})"
            else:
                LastUpdatedCutoff = "{:,}".format(LastUpdatedCutoff)
                EstimateSmoothing = "{:,}".format(EstimateSmoothing)
                EstimateNoSmoothing = "{:,}".format(EstimateNoSmoothing)
                EPPerHour = "{:,}".format(EPPerHour)
            if graph:
                FileName = f"{EventID}_{server}_{tier}.png"
                SavedFile = f"img/graphs/{FileName}"
                if os.path.exists(SavedFile):
                    from discord import File
                    DiscordFileObject = File(SavedFile,filename=FileName)
                    GraphInfo.append(FileName)
                    GraphInfo.append(DiscordFileObject)
                else:
                    Estimates = await CalculatecutoffEstimates(server,tier,EventID)
                    GraphInfo = await CreateGraph(server, EventID, tier, Estimates[5],Estimates[4],Estimates[3],Estimates[6])
    
        else:
            LastCurrent = LastUpdatedValues[0]
            LastEstimateSmoothing = LastUpdatedValues[1]
            LastEstimateNoSmoothing = LastUpdatedValues[2]
            LastEPPerHour = LastUpdatedValues[3]
            CurrentDifference = LastUpdatedCutoff - LastCurrent
            Estimates = await CalculatecutoffEstimates(server,tier,EventID) # Returns Smoothing / No Smoothing / EPPerHour
            EstimateSmoothing = Estimates[0]
            EstimateNoSmoothing = Estimates[1]
            EPPerHour = Estimates[2]
            UpdateCutoffJSON(server, tier, EventID, LastUpdatedCutoff, EstimateSmoothing, EstimateNoSmoothing, EPPerHour)
            EstimateSmoothingDifference = EstimateSmoothing - LastEstimateSmoothing
            EstimateNoSmoothingDifference = EstimateNoSmoothing - LastEstimateNoSmoothing
            EPPerHourDifference = EPPerHour - LastEPPerHour
            if CurrentDifference > 0:
                CurrentDifference = "{:+,}".format(CurrentDifference)
            else:
                CurrentDifference = "{:,}".format(CurrentDifference)
            if EstimateSmoothingDifference > 0:
                EstimateSmoothingDifference = "{:+,}".format(EstimateSmoothingDifference)
            else:
                EstimateSmoothingDifference = "{:,}".format(
                    EstimateSmoothingDifference)
            if EstimateNoSmoothingDifference > 0:
                EstimateNoSmoothingDifference = "{:+,}".format(EstimateNoSmoothingDifference)
            else:
                EstimateNoSmoothingDifference = "{:,}".format(
                    EstimateNoSmoothingDifference)
            if EPPerHourDifference > 0:
                EPPerHourDifference = "{:+,}".format(EPPerHourDifference)
            else:
                EPPerHourDifference = "{:,}".format(EPPerHourDifference)
            LastUpdatedCutoff = "{:,}".format(LastUpdatedCutoff)
            EstimateSmoothing = "{:,}".format(EstimateSmoothing)
            EstimateNoSmoothing = "{:,}".format(EstimateNoSmoothing)
            LastUpdatedCutoff = f'{LastUpdatedCutoff} ({CurrentDifference})'
            EstimateSmoothing = f'{EstimateSmoothing} ({EstimateSmoothingDifference})'
            EstimateNoSmoothing = f'{EstimateNoSmoothing} ({EstimateNoSmoothingDifference})'
            EPPerHour = f"{'{:,}'.format(EPPerHour)} ({EPPerHourDifference})"
            
            # If this else is hit, that means there was an update and the graph needs updated regardless if the user requested it
            GraphInfo = await CreateGraph(server, EventID, tier, Estimates[5],Estimates[4],Estimates[3],Estimates[6])

    else:
        # Returns Smoothing / No Smoothing / EPPerHour
        Estimates = await CalculatecutoffEstimates(server, tier, EventID)
        
        EstimateSmoothing = Estimates[0]
        EstimateNoSmoothing = Estimates[1]
        EPPerHour = Estimates[2]
        UpdateCutoffJSON(server, tier, EventID, LastUpdatedCutoff,
                         EstimateSmoothing, EstimateNoSmoothing, EPPerHour)

        LastUpdatedCutoff = "{:,}".format(LastUpdatedCutoff)
        EstimateSmoothing = "{:,}".format(EstimateSmoothing)
        EstimateNoSmoothing = "{:,}".format(EstimateNoSmoothing)
        EPPerHour = "{:,}".format(EPPerHour)
        if graph:
            GraphInfo = await CreateGraph(server, EventID, tier, Estimates[5],Estimates[4],Estimates[3],Estimates[6])
        
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = datetime.now(timezone('US/Eastern'))
    timeLeft = await GetTimeLeftString(server,EventID)
    prog = await GetEventProgress(server,EventID) 
    prog = str(prog) + '%'
    bannerAPI = await GetBestdoriBannersAPI(int(EventID))
    bannerName = bannerAPI['assetBundleName']
    eventUrl = 'https://bestdori.com/info/events/' + str(EventID)
    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)
    
    if EstimateSmoothing == '0':
        EstimateSmoothing = '?'
        EstimateNoSmoothing = '?'
        

    embed=discord.Embed(title=EventName, url=eventUrl, color=0x09d9fd)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Current', value=LastUpdatedCutoff, inline=True)
    embed.add_field(name='EP Per Hour', value=EPPerHour, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name='Estimate', value=EstimateSmoothing, inline=True)
    embed.add_field(name='Estimate (No Smoothing)',
                    value=EstimateNoSmoothing, inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)
    embed.add_field(name='Last Updated', value=LastUpdated, inline=True)
    embed.add_field(name='Time Left', value=timeLeft, inline=True)
    embed.add_field(name='Progress', value=prog, inline=True)
    if graph:
        embed.set_image(url=f"attachment://{GraphInfo[0]}")
        embed.set_footer(text=f"{now_time.strftime(fmt)}")
        DiscordFileObject = GraphInfo[1]
        return embed, DiscordFileObject
    else:
        embed.set_footer(text=f"\nWant a graph? Try cutoff {tier} {server} graph\n\n{now_time.strftime(fmt)}")
        return embed




