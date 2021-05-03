import urllib
from urllib.request import urlopen
from csv import writer
import pandas as pd
import requests
import ast
from bs4 import BeautifulSoup


def getWebPage(url):
    """Returns a UTF-8 decoded HTML Page"""
    page = urlopen(url)
    htmlBytes = page.read()
    decodedHtml = htmlBytes.decode("utf-8")
    return decodedHtml


def getCardName(html):
    """Returns the cards name"""
    cardNameStart = html.find('<h1 class="card-text-title" lang="en">') + 38
    cardNameEnd = html.find('<', cardNameStart)
    title = html[cardNameStart:cardNameEnd].replace("&#39;", "'").strip()
    cardNameTwo = html.find('<h1 class="card-text-title" lang="en">', cardNameEnd + 1)
    if cardNameTwo != -1 and html.count("card-text-mana-cost") == 1:
        cardNameTwoEnd = html.find('<br>', cardNameTwo)
        cardNameTwo = html[cardNameTwo + 38: cardNameTwoEnd].replace("&#39;", "'").strip()
        title = [title, cardNameTwo]
    if cardNameTwo != -1 and html.count("card-text-mana-cost") == 2:
        cardNameTwoEnd = html.find('<span', cardNameTwo)
        cardNameTwo = html[cardNameTwo + 38: cardNameTwoEnd].replace("&#39;", "'").strip()
        title = [title, cardNameTwo]
    return title  # strip function removes leading and ending whitespaces


def getCardCmc(html):
    """Returns the card converted mana cost"""
    cardCmcBoxStart = html.find("card-text-mana-cost")
    cardCmcBoxEnd = html.find("<br>", cardCmcBoxStart)
    manaCost = ""
    cmcTwo = ""
    cardCmcEndTwo = -1
    while cardCmcBoxStart < cardCmcBoxEnd:
        maxIndex = html.find("</span>", cardCmcBoxStart)
        cardCmcEnd = html.find("</abbr>", cardCmcBoxStart, maxIndex)
        cardCmcStart = cardCmcEnd
        while html[cardCmcStart] != ">":
            cardCmcStart -= 1
        if cardCmcEnd != -1:
            cardCmcStart += 1
            cardCmcBoxStart = cardCmcEnd + 5
            manaCost += html[cardCmcStart: cardCmcEnd] + " "
            cardCmcEndTwo = cardCmcEnd
        else:
            break
    if isDual(html):
        cardCmcBoxStart = html.find("card-text-mana-cost", cardCmcEndTwo)
        cardCmcBoxEnd = html.find("<br>", cardCmcBoxStart)
        finalIndex = html.find("<em>", cardCmcBoxStart)
        cmcTwo = ""
        while cardCmcBoxStart < cardCmcBoxEnd:
            cardCmcEnd = html.find("</abbr>", cardCmcBoxStart, finalIndex)
            cardCmcStart = cardCmcEnd
            while html[cardCmcStart] != ">":
                cardCmcStart -= 1
            if cardCmcEnd != -1:
                cardCmcStart += 1
                cardCmcBoxStart = cardCmcEnd + 5
                cmcTwo += html[cardCmcStart: cardCmcEnd] + " "
            else:
                break
        manaCost = [manaCost, cmcTwo]
    return manaCost


def getCardType(html):
    """Returns card type"""
    cardNameStart = html.find('"card-text-type-line" lang="en">') + 32
    cardNameEnd = html.find('<div class="card-text-box"') - 15
    cardType = html[cardNameStart:cardNameEnd].strip()
    x = cardType.split("—", 2)
    return x  # strip function removes leading and ending whitespaces


def getCardText(html):
    """Returns the cards oracle text"""
    cardNameStart = html.find('"card-text-oracle">') + 39
    cardNameEnd = html.find('</div>', cardNameStart)
    cardText = html[cardNameStart:cardNameEnd]
    return cardText.replace("</p>", "").replace("<p>",
                                                "").strip()  # strip function removes leading and ending whitespaces


def isCreature(html):
    """Returns a boolean True if creature, false otherwise"""
    cardNameStart = html.find('"card-text-type-line" lang="en">') + 32
    cardNameEnd = html.find('<div class="card-text-box"') - 15
    cardType = html[cardNameStart:cardNameEnd]
    if cardType.strip().find("Creature") != -1 or cardType.strip().find("Legendary Creature") != -1:
        return True
    else:
        return False


def getPowTou(html):
    """Returns Power and Toughness"""
    if isCreature(html):
        cardNameStart = html.find('card-text-stats"') + 17
        cardNameEnd = html.find('</div>', cardNameStart)
        cardPowTou = html[cardNameStart:cardNameEnd]
    else:
        return None
    return cardPowTou.strip()  # strip function removes leading and ending whitespaces


def getSet(html):
    """Returns set name"""
    cardNameStart = html.find('prints-current-set-name">') + 25
    cardNameEnd = html.find('</span>', cardNameStart)
    setName = html[cardNameStart:cardNameEnd]
    return setName.strip()  # strip function removes leading and ending whitespaces


def getSetDetails(html):
    """Returns set number, rarity, and language"""
    cardNameStart = html.find('prints-current-set-details">') + 30
    cardNameEnd = html.find('</span>', cardNameStart)
    setDetails = html[cardNameStart:cardNameEnd].strip()
    x = setDetails.split("·", 3)
    return x  # strip function removes leading and ending whitespaces


# change function to return a array of the form [set number, rarity, language]

def getCardImage(html):
    """returns a link to the image"""
    imageStart = html.find('src="https://c1.scryfall.com/file/scryfall-cards') + 5
    imageEnd = html.find('</div>', imageStart)
    imageLink = html[imageStart:imageEnd].replace('" />', "").replace("\n", "").strip()
    imageTwo = html.find('"card-image-back"')
    if imageTwo != -1:
        imageTwoStart = html.find('src="https://c1.scryfall.com/file/scryfall-cards', imageTwo) + 5
        imageTwoEnd = html.find("</div>", imageTwoStart)
        imageTwo = html[imageTwoStart:imageTwoEnd].replace('" />', "").replace("\n", "").strip()
        imageLink = [imageLink.strip(), imageTwo.strip()]
    return imageLink


def isDual(html):
    """returns boolean true if is a dual faced card"""
    count = html.count("card-text-mana-cost")
    if count > 1:
        return True
    return False


def append_list_as_row(file_name, list_of_elem):
    """appends row"""
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def gatherData():
    """Compiles data into a CSV"""
    setCsv = pd.read_csv("setInfo.csv")
    setCodes = list(setCsv.expansionCode)
    setSize = list(setCsv.numberOfCards)
    tracker = 0
    for code in setCodes:
        for j in range(1, int(setSize[tracker]) + 1):
            if tracker == len(setCodes):
                break
            try:
                html = getWebPage("https://scryfall.com/card/" + code.lower() + "/" + str(j))
            except urllib.error.HTTPError:
                html = getWebPage("https://scryfall.com/card/" + code.lower() + "/" + str(j) + "a")
            setNum = getSetDetails(html)[0]
            setRarity = getSetDetails(html)[1]
            lang = getSetDetails(html)[2]
            if isCreature(html):
                creatureType = getCardType(html)[1]
            else:
                creatureType = None
            cardDetails = [getCardName(html), getCardCmc(html),
                           getCardType(html)[0], creatureType, getPowTou(html), getSet(html), setNum, setRarity, lang
                , getCardImage(html)]
            append_list_as_row('historyOfSet.csv', cardDetails)
            print(cardDetails)
        tracker += 1


def getSite(url):
    """returns site using request"""
    r = requests.get(url)
    return r


def appendPrice():
    """Adds a current price to data frame"""
    df = pd.read_csv("pricetest.csv")
    for ind in range(4584, len(df.index)):  # iterates through all of the cards
        # Change to for ind in df.index after finishing compiling.
        if len(df['cardName'][ind]) > 1:
            #if df['set'] == "Guilds of Ravnica (GRN)":
            lookUp = df['cardName'][ind].replace(" ", "-").replace(",", "").replace("[", "").replace("]", "").replace(
                "'", "").replace(":", "")
        else:
            lookUp = df['cardName'][ind].replace(" ", "-").replace("'", "").replace(":", "")
        lookUp2 = df['set'][ind].replace(" ", "-").replace("'", '')[:-6]
        lookUp3 = df["setNum"][ind].replace("#", "").replace(" ", "")
        if df['cardName'][ind].find("]") != -1:
            if not df['set'][ind] == "Guilds of Ravnica (GRN)" or not df['set'][ind] == "Ravnica Allegiance (RNA)" :
                x = ast.literal_eval(df['cardName'][ind])
                lookUp = x[0].replace(" ", "-").replace("'", "").replace(":", "")
        try:
            if lookUp2 == 'Ikoria:-Lair-of-Behemoths':
                lookUp2 = 'ikoria-lair-of-behemoths'
            if df['cardType'][ind] == 'Basic Land ' or df['cardType'][ind] == "Basic Snow Land ":
                r = getSite("https://shop.tcgplayer.com/magic/{}/{}-{}".format(lookUp2, lookUp, lookUp3))
            else:
                if lookUp2 == 'Ikoria:-Lair-of-Behemoths':
                    lookUp2 == 'ikoria-lair-of-behemoths'
                r = getSite("https://shop.tcgplayer.com/magic/{}/{}".format(lookUp2, lookUp))
            if lookUp2 == 'Ikoria:-Lair-of-Behemoths':
                lookUp2 == 'ikoria-lair-of-behemoths'
        except urllib.error.HTTPError:
            r = getSite("https://shop.tcgplayer.com/magic/{}/{}a".format(lookUp2, lookUp))
        print("https://shop.tcgplayer.com/magic/{}/{}".format(lookUp2, lookUp))
        soup = BeautifulSoup(r.content, 'html.parser')
        price_containers = soup.find_all('td',
                                         class_="price-point__data")  # finds all instances of 'td' with the price point class
        try:
            priceA = price_containers[0]
            price = priceA.text
            print("{} current market price: {}".format(df['cardName'][ind], price))
            df['price'][ind] = price[1:]
            if ind % 100 == 0:
                updated_df = df[
                    ['cardName', 'cardCmc', 'cardType', 'creatureType', 'powTough', 'set', 'setNum', 'rarity',
                     'language'
                        , 'cardImage', 'price']]
                updated_df.to_csv("pricetest.csv", index=True)
        except IndexError:
            print("Failed to read site")


def fixDragon():
    """Fixes a formatting issue with dragon's maze  in the CSV"""
    df = pd.read_csv("historyOfSet.csv")
    df.loc[df["set"] == 'Dragon&#39;s Maze (DGM)', "set"] = "Dragon's Maze (DGM)"
    new_df = df[['cardName', 'cardCmc', 'cardType', 'creatureType', 'powTough', 'set', 'setNum', 'rarity', 'language'
        , 'cardImage', 'price']]
    new_df.to_csv("pricetest.csv", index=True)


def main():
    appendPrice()


main()
