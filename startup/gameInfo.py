import requests
import json
def getGameVersions(server: str):
    try:
        if(server == 'en'):
            itunesURL = 'id=1335529760&lang=en_us&country=us'
        elif(server == 'jp'):
            itunesURL = 'id=1195834442&lang=ja_jp&country=jp'
        url = "https://itunes.apple.com/lookup?%s" % itunesURL
        data = requests.get(url).text
        version = json.loads(str(data))['results'][0]['version']
        if version.find("iOS App") == -1:
            if version.find("iOS ") == 0:
                return (version[4:])
            else:
                return (version)
        else:
            return (version[8:]) 
    except Exception as e:
        print('Failed getting game version data.\n' + str(e))

