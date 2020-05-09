import json
from selenium import webdriver

with open("config.json") as file:
    config_json = json.load(file)
    driverPath = config_json["chromeDriverPath"]
    drivers_enabled = config_json['webdrivers_enabled']

def LoadWebDrivers(server: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    if server == 'en':
        global enDriver
        enDriver = webdriver.Chrome(options=options,executable_path=driverPath)
        enDriver.get('https://bestdori.com/tool/eventtracker/en/t100')
        enDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
        return enDriver
    if server == 'jp':
        global jpDriver
        jpDriver = webdriver.Chrome(options=options,executable_path=driverPath)
        jpDriver.get('https://bestdori.com/tool/eventtracker/jp/t100')
        jpDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
        return jpDriver
    if server == 'cn':
        global cnDriver
        cnDriver = webdriver.Chrome(options=options,executable_path=driverPath)
        cnDriver.get('https://bestdori.com/tool/eventtracker/cn/t100')
        cnDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
        return cnDriver
    if server == 'tw' or server == 'kr':
        global twkrDriver
        twkrDriver = webdriver.Chrome(options=options,executable_path=driverPath) # Only need 1 driver because TW and KR are only having T100 tracked. During a request to get the data, you can just swap between regions with 1 click 
        twkrDriver.get('https://bestdori.com/tool/eventtracker/tw/t100')
        twkrDriver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[3]/a/span[2]').click()
        return twkrDriver

if drivers_enabled == 'true':
    import psutil
    for p in psutil.process_iter():
        if 'Google' in p.name():
            print(f'Killing process: {p.name()}')
            p = psutil.Process(p.pid)
            p.kill()
    enDriver = LoadWebDrivers('en')
    jpDriver = LoadWebDrivers('jp')
    cnDriver = LoadWebDrivers('cn')
    twkrDriver = LoadWebDrivers('tw')
else:
    print('Not loading webdrivers')
