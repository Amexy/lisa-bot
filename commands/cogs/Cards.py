import uuid
import requests

from io import BytesIO
from PIL import Image
from typing import Dict, List
from enum import Enum, IntEnum

from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

from commands.cogs import Result


class Character(Enum):
    Kasumi = ["Kasumi"]
    Tae = ["Tae"]
    Rimi = ["Rimi"]
    Saya = ["Saya", "Saaya"]
    Arisa = ["Arisa"]
    Ran = ["Ran"]
    Moca = ["Moca"]
    Himari = ["Himari"]
    Tomoe = ["Tomoe"]
    Tsugumi = ["Tsugumi", "Npc"]
    Kokoro = ["Kokoro"]
    Kaoru = ["Kaoru"]
    Hagumi = ["Hagumi"]
    Kanon = ["Kanon"]
    Misaki = ["Misaki", "Furry"]
    Aya = ["Aya"]
    Hina = ["Hina"]
    Chisato = ["Chisato", "Cheeto"]
    Maya = ["Maya"]
    Eve = ["Eve"]
    Yukina = ["Yukina", "Yukinya"]
    Sayo = ["Sayo"]
    Lisa = ["Lisa"]
    Ako = ["Ako"]
    Rinko = ["Rinko"]
    Mashiro = ["Mashiro"]
    Toko = ["Toko"]
    Nanami = ["Nanami"]
    Tsukushi = ["Tsukushi"]
    Rui = ["Rui"]

    @staticmethod
    def switch(i: int):
        switcher = {
            1: Character.Kasumi,
            2: Character.Tae,
            3: Character.Rimi,
            4: Character.Saya,
            5: Character.Arisa,
            6: Character.Ran,
            7: Character.Moca,
            8: Character.Himari,
            9: Character.Tomoe,
            10: Character.Tsugumi,
            11: Character.Kokoro,
            12: Character.Kaoru,
            13: Character.Hagumi,
            14: Character.Kanon,
            15: Character.Misaki,
            16: Character.Aya,
            17: Character.Hina,
            18: Character.Chisato,
            19: Character.Maya,
            20: Character.Eve,
            21: Character.Yukina,
            22: Character.Sayo,
            23: Character.Lisa,
            24: Character.Ako,
            25: Character.Rinko,
            26: Character.Mashiro,
            27: Character.Toko,
            28: Character.Nanami,
            29: Character.Tsukushi,
            30: Character.Rui
        }
        return switcher.get(i)


class Rarity(IntEnum):
    Normal = 1
    Rare = 2
    Sr = 3
    Ssr = 4

    @staticmethod
    def switch(name: str):
        switcher = {
            "normal": Rarity.Normal,
            "rare": Rarity.Rare,
            "sr": Rarity.Sr,
            "ssr": Rarity.Ssr
        }
        return switcher.get(name)


class Attribute(Enum):
    Powerful = "powerful"
    Cool = "cool"
    Pure = "pure"
    Happy = "happy"


class Acquisition(Enum):
    Initial = "initial"
    Permanent = "permanent"
    Limited = "limited"
    Event = "event"
    Campaign = "campaign"
    Others = "others"


class Stat:
    performance: int
    technique: int
    visual: int

    def __init__(self, performance: int, technique: int, visual: int):
        self.performance = performance
        self.technique = technique
        self.visual = visual


class Palette:
    primaryStr: str
    primaryInt: int
    accentHsv: str

    def __init__(self, attribute: Attribute):
        if attribute == Attribute.Powerful:
            primary = "910000"
            self.primaryStr = "#" + primary
            self.primaryInt = int(primary, 16)
            self.accentHsv = "hsv(20,30%,100%)"
        elif attribute == Attribute.Cool:
            primary = "003391"
            self.primaryStr = "#" + primary
            self.primaryInt = int(primary, 16)
            self.accentHsv = "hsv(20,30%,100%)"
        elif attribute == Attribute.Pure:
            primary = "00B515"
            self.primaryStr = "#" + primary
            self.primaryInt = int(primary, 16)
            self.accentHsv = "hsv(20,30%,100%)"
        else:
            primary = "B56A00"
            self.primaryStr = "#" + primary
            self.primaryInt = int(primary, 16)
            self.accentHsv = "hsv(20,30%,100%)"


class Card:
    cardId: int
    characterId: int
    character: Character
    rarity: Rarity
    attribute: Attribute
    levelLimit: int
    resourceName: str
    skillId: int
    acquisition: Acquisition
    cardName: str
    skill: str
    stat: Stat

    def __init__(self, cardId: int, characterId: int, character: Character, rarity: Rarity,
                 attribute: Attribute, levelLimit: int, resourceName: str, skillId: int,
                 acquisition: Acquisition, cardName: str, skill: str, stat: Stat):
        self.cardId = cardId
        self.characterId = characterId
        self.character = character
        self.rarity = rarity
        self.attribute = attribute
        self.levelLimit = levelLimit
        self.resourceName = resourceName
        self.skillId = skillId
        self.acquisition = acquisition
        self.cardName = cardName
        self.skill = skill
        self.stat = stat


class FilteredArguments:
    char: Character
    rarity: Rarity
    attr: Attribute
    df: bool
    last: bool
    position: int

    def __init__(self, char: Character, rarity: Rarity = None, attr: Attribute = None, df: bool = False, last: bool = False, position: int = None):
        self.char = char
        self.rarity = rarity
        self.attr = attr
        self.df = df
        self.last = last
        self.position = position


def parseCards(cards: Dict, skills: Dict) -> List[Card]:
    return [mapJsonToCards(k, v, skills) for k, v in cards.items()]


def mapJsonToCards(k, v, skills) -> Card:
    cardId = int(k)
    characterId = v['characterId']
    levelLimit = v['levelLimit']
    resourceName = str(v['resourceSetName'])
    skillId = v['skillId']
    character = Character.switch(characterId)
    rarity = Rarity(v['rarity'])
    attribute = Attribute(v['attribute'])
    acquisition = Acquisition(v['type'])

    cardName = ""
    enName = v['prefix'][1]
    if enName:
        cardName = enName

    stat = v['stat']

    if rarity == Rarity.Normal or rarity == Rarity.Rare:
        maxLvl = stat[str(levelLimit)]
        performance = maxLvl['performance']
        technique = maxLvl['technique']
        visual = maxLvl['performance']
    else:
        maxLvl = stat[str(levelLimit + 10)]
        performance = maxLvl['performance']
        technique = maxLvl['technique']
        visual = maxLvl['performance']

    if 'episodes' in stat:
        for ep in stat['episodes']:
            performance += ep['performance']
            technique += ep['technique']
            visual += ep['visual']

    if 'training' in stat:
        tr = stat['training']
        performance += tr['performance']
        technique += tr['technique']
        visual += tr['visual']

    stat = Stat(performance, technique, visual)

    skill = skills[str(skillId)]
    desc: str = skill['description'][1]
    duration = skill['duration'][4]
    # Life recovery values are not in API
    # fml
    if "{1}" in desc:
        desc = desc.replace("{0} ", "")
        desc = desc.replace("{1}", "{0}")
        desc = desc.format(duration)
    else:
        desc = desc.format(duration)

    return Card(cardId, characterId, character, rarity, attribute, levelLimit, resourceName, skillId, acquisition, cardName, desc, stat)


def splitStrings(textToSplit: str, font, maxSize: int) -> str:
    split = textToSplit.split()
    for i in range(len(split)):
        take = split[:(i+1)]
        joined = " ".join(take)
        joinedSize = font.getsize(joined)[0]
        if joinedSize > maxSize:
            previousList = split[:i]
            nextList = split[i:]
            prevString = " ".join(previousList)
            # recursion memes
            return str(prevString + "\n" + splitStrings(" ".join(nextList), font, maxSize))
    return " ".join(split)


def filterArguments(*args) -> Result:
    name: str = args[0]
    if len(name.rstrip('0123456789')) != len(name):
        return filterArguments(name[:len(name.rstrip('0123456789'))], name[len(name.rstrip('0123456789')):], *(args[1:]))
    else:
        for ch in Character:
            char: Character = ch
            if findStringInList(name, char.value):
                args = args[1:]
                if len(args) == 0:
                    return Result.createSuccess(FilteredArguments(char=char, rarity=Rarity.Ssr, last=True))
                nextParam: str = args[0]
                rarity = paramIntoRarity(args[0])
                if nextParam.isdigit():
                    return Result.createSuccess(FilteredArguments(char=char, rarity=Rarity.Ssr, position=int(nextParam)))
                elif len(nextParam.rstrip('0123456789')) != len(nextParam):
                    return filterArguments(name, nextParam[:len(nextParam.rstrip('0123456789'))], nextParam[len(nextParam.rstrip('0123456789')):], *(args[1:]))
                elif rarity:
                    args = args[1:]
                    if len(args) == 0:
                        return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, last=True))
                    number: str = args[0]
                    if number.isdigit():
                        return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, position=int(number)))
                    else:
                        return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, last=True))
                elif nextParam.lower() == "df":
                    args = args[1:]
                    if len(args) == 0:
                        return Result.createSuccess(FilteredArguments(char=char, df=True, last=True))
                    attr = paramIntoAttr(args[0])
                    if attr:
                        return Result.createSuccess(FilteredArguments(char=char, attr=attr, df=True))
                    else:
                        return Result.createSuccess(FilteredArguments(char=char, df=True, last=True))
                elif nextParam.lower().startswith("last"):
                    if len(nextParam) > 4:
                        return filterArguments(name, nextParam[:4], nextParam[4:], *(args[1:]))
                    args = args[1:]
                    if len(args) == 0:
                        return Result.createSuccess(FilteredArguments(char=char, rarity=Rarity.Ssr, last=True))
                    attr = paramIntoAttr(args[0])
                    rarity = paramIntoRarity(args[0])
                    if attr:
                        args = args[1:]
                        if len(args) == 0:
                            return Result.createSuccess(FilteredArguments(char=char, attr=attr, last=True))
                        rarity = paramIntoRarity(args[0])
                        if rarity:
                            return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, attr=attr, last=True))
                        else:
                            return Result.createSuccess(FilteredArguments(char=char, attr=attr, last=True))
                    if rarity:
                        args = args[1:]
                        if len(args) == 0:
                            return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, last=True))
                        attr = paramIntoAttr(args[0])
                        if attr:
                            return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, attr=attr, last=True))
                        else:
                            return Result.createSuccess(FilteredArguments(char=char, rarity=rarity, last=True))
                else:
                    return Result.createSuccess(FilteredArguments(char=char, rarity=Rarity.Ssr, last=True))
        return Result.createFailure("Character with name \"{}\" not found".format(name))


def paramIntoAttr(param: str):
    if param.lower() == "powerful" or param.lower() == "cool" or param.lower() == "pure" or param.lower() == "happy":
        attr: Attribute = Attribute(param.lower())
        return attr
    return None


def paramIntoRarity(param: str):
    if param.lower() == "ssr" or param.lower() == "sr" or param.lower() == "rare" or param.lower() == "normal":
        rarity: Rarity = Rarity.switch(param.lower())
        return rarity
    return None


def findStringInList(find: str, collection: List[str]) -> bool:
    for thing in collection:
        if find.lower() == thing.lower():
            return True
    return False


def findCardFromArguments(cardList: List[Card], arg: FilteredArguments) -> Result:
    lst = [it for it in cardList if
           it.character == arg.char and
           it.acquisition != Acquisition.Others]

    if arg.rarity:
        lst = [it for it in lst if it.rarity == arg.rarity]

    if arg.df:
        lst = [it for it in lst if it.skillId in [20, 27, 28, 29, 30, 31, 32]]

    if arg.attr:
        lst = [it for it in lst if it.attribute == arg.attr]

    listLength = len(lst)
    if listLength == 0:
        return Result.createFailure("No card with selected filters found")

    if arg.position:
        if listLength < arg.position:
            return Result.createFailure("Error: Only {} card(s) with selected filters found".format(listLength))
        else:
            return Result.createSuccess(lst[arg.position - 1])

    return Result.createSuccess(lst[-1])


def generateImage(card: Card, palette: Palette) -> str:
    im = Image.new("RGBA", (570, 360))
    image: requests.models.Response = requests.get('https://bestdori.com/assets/jp/characters/resourceset/' + card.resourceName + '_rip/card_normal.png')
    cardArt = Image.open(BytesIO(image.content))

    cardArtWidth = cardArt.size[0]
    cardArtHeight = cardArt.size[1]
    ratio = cardArtHeight / 340
    newCardArtWidth = int(cardArtWidth / ratio)
    newCardArtHeight = int(cardArtHeight / ratio)
    cardArt = cardArt.resize((newCardArtWidth, newCardArtHeight))
    border = int((newCardArtWidth - 270) / 2)
    cardArt = cardArt.crop((border, 0, (border + 270), 340))
    im.paste(cardArt, (10, 10))
    imageDraw = Draw(im)
    star = u"\u2605"
    rarityText = ""
    for _ in range(card.rarity.value):
        rarityText = rarityText + star

    segoe28 = truetype('seguisym.ttf', 26)
    imageDraw.text((290, 0), rarityText, font=segoe28, fill="white", stroke_width=1, stroke_fill="black")

    segoe18 = truetype('seguisym.ttf', 18)
    segoe16 = truetype('seguisym.ttf', 16)
    segoe14 = truetype('seguisym.ttf', 14)

    imageDraw.text((290, 35), str(card.cardName), font=segoe14 if segoe18.getsize(card.cardName)[0] > 265 else segoe18, fill="white", stroke_width=1, stroke_fill="black")

    imageDraw.text((290, 60), str(card.acquisition.name), font=segoe14, fill="white", stroke_width=1, stroke_fill="black")

    imageDraw.text((290, 100), "Performance", font=segoe16, fill="white", stroke_width=1, stroke_fill="black")
    imageDraw.text((290, 130), "Technique", font=segoe16, fill="white", stroke_width=1, stroke_fill="black")
    imageDraw.text((290, 160), "Visual", font=segoe16, fill="white", stroke_width=1, stroke_fill="black")
    imageDraw.text((290, 200), "Total Power", font=segoe18, fill="white", stroke_width=1, stroke_fill="black")

    statPerformance = card.stat.performance
    statTechnique = card.stat.technique
    statVisual = card.stat.visual
    perFocus = False
    tecFocus = False
    visFocus = False
    if statPerformance > statTechnique and statPerformance > statVisual:
        perFocus = True
    if statTechnique > statPerformance and statTechnique > statVisual:
        tecFocus = True
    if statVisual > statPerformance and statVisual > statTechnique:
        visFocus = True

    imageDraw.text(((540 - segoe16.getsize(str(statPerformance))[0]), 100), str(statPerformance), font=segoe16, fill=palette.accentHsv if perFocus else "white", stroke_width=1, stroke_fill="black")
    imageDraw.text(((540 - segoe16.getsize(str(statTechnique))[0]), 130), str(statTechnique), font=segoe16, fill=palette.accentHsv if tecFocus else "white", stroke_width=1, stroke_fill="black")
    imageDraw.text(((540 - segoe16.getsize(str(statVisual))[0]), 160), str(statVisual), font=segoe16, fill=palette.accentHsv if visFocus else "white", stroke_width=1, stroke_fill="black")
    imageDraw.text(((540 - segoe18.getsize(str(statPerformance + statTechnique + statVisual))[0]), 200), str(statPerformance + statTechnique + statVisual), font=segoe18, fill="white", stroke_width=1, stroke_fill="black")

    skillText = card.skill
    skillSize = segoe14.getsize(skillText)[0]
    if skillSize > 250:
        skillText = splitStrings(skillText, segoe14, 250)

    imageDraw.text((290, 250), skillText, font=segoe14, spacing=-2, fill="white", stroke_width=1, stroke_fill="black")

    imageDraw.rectangle([(566, 0), (570, 360)], fill=palette.primaryStr)
    fileName = "imgTmp/" + str(uuid.uuid1()) + ".png"
    im.save(fileName)
    return fileName
