from bs4 import BeautifulSoup
from protodefs.ranks import t10ranks
from startup.login import enICEObject, jpICEObject
from datetime import datetime
from pytz import timezone
import discord, asyncio, time

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
    
async def GetCutoffFormatting(driver, server: str, tier: int):
    from commands.apiFunctions import GetBestdoriAllEventsAPI, GetBestdoriBannersAPI
    from commands.formatting.TimeCommands import GetTimeLeftString, GetEventProgress
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
                    driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[2]').click()
                    await asyncio.sleep(.5)
                    driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[1]').click()
                    await asyncio.sleep(.5)
                else:
                    if server == 'kr':
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[4]/div[2]/div/div/div/a[3]').click()
                        await asyncio.sleep(.5)
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[4]/div[2]/div/div/div/a[5]').click()
                        await asyncio.sleep(.5)
                    else:
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[4]/div[2]/div/div/div/a[5]').click()
                        await asyncio.sleep(.5)
                        driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div[1]/div[3]/div[4]/div[2]/div/div/div/a[3]').click()
                        await asyncio.sleep(.5)
            elif tier == 1000:
                eventName = 'T1000: ' + eventName
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[1]').click()                
                await asyncio.sleep(.3)
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[2]').click()  
                await asyncio.sleep(.5)   
            else:
                eventName = 'T2000: ' + eventName
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[1]').click()
                await asyncio.sleep(.5)
                driver.find_element_by_xpath('//*[@id="app"]/div[4]/div[2]/div/div[3]/div[5]/div[2]/div/div/div/a[3]').click()
                await asyncio.sleep(.5)
            await asyncio.sleep(.5)
            parsedHTML = parseHTML(driver)
            if not parsedHTML:
                valid = 'n'
            else:
                valid = 'y'
            
            # for when the event is completed
            if parsedHTML[2].text == 'Final Cutoff':
                if parsedHTML[3].text == '?':
                    estimate = parsedHTML[9].text    
                    lastupdated = parsedHTML[11].text
                    current = parsedHTML[7].text    
                else:
                    estimate = parsedHTML[7].text
                    lastupdated = parsedHTML[9].text
                    current = parsedHTML[3].text
            else:
                estimate = parsedHTML[5].text
                lastupdated = parsedHTML[7].text
                current = parsedHTML[3].text

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
    timeLeft = await GetTimeLeftString(server,eventId)
    #await ctx.send("Grabbing cutoff...")
    prog = await GetEventProgress(server,eventId) 
    prog = str(prog) + '%'
    eventAPI = await GetBestdoriAllEventsAPI()
    bannerAPI = await GetBestdoriBannersAPI(int(eventId))
    bannerName = bannerAPI['assetBundleName']
    eventUrl = 'https://bestdori.com/info/events/' + str(eventId)
    thumbnail = 'https://bestdori.com/assets/%s/event/%s/images_rip/logo.png'  %(server,bannerName)


    embed=discord.Embed(title=eventName, url=eventUrl, color=0x09d9fd)
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name='Current', value=current, inline=True)
    embed.add_field(name='Estimate', value=estimate, inline=True)
    embed.add_field(name='Last Updated', value=lastupdated, inline=False)
    embed.add_field(name='Time Left', value=timeLeft, inline=True)
    embed.add_field(name='Progress', value=prog, inline=True)
    embed.set_footer(text=now_time.strftime(fmt))
    output = embed
    return output





