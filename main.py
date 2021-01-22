import urllib
from urllib.request import urlopen
from csv import writer
import pandas as pd


def getWebPage(url):
    page = urlopen(url)
    htmlBytes = page.read()
    decodedHtml = htmlBytes.decode("utf-8")
    return decodedHtml


def getCardName(html):
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
    cardNameStart = html.find('"card-text-type-line" lang="en">') + 32
    cardNameEnd = html.find('<div class="card-text-box"') - 15
    cardType = html[cardNameStart:cardNameEnd].strip()
    x = cardType.split("—", 2)
    return x  # strip function removes leading and ending whitespaces


def getCardText(html):
    cardNameStart = html.find('"card-text-oracle">') + 39
    cardNameEnd = html.find('</div>', cardNameStart)
    cardText = html[cardNameStart:cardNameEnd]
    return cardText.replace("</p>", "").replace("<p>",
                                                "").strip()  # strip function removes leading and ending whitespaces


def isCreature(html):
    cardNameStart = html.find('"card-text-type-line" lang="en">') + 32
    cardNameEnd = html.find('<div class="card-text-box"') - 15
    cardType = html[cardNameStart:cardNameEnd]
    if cardType.strip().find("Creature") != -1 or cardType.strip().find("Legendary Creature") != -1:
        return True
    else:
        return False


def getPowTou(html):
    if isCreature(html):
        cardNameStart = html.find('card-text-stats"') + 17
        cardNameEnd = html.find('</div>', cardNameStart)
        cardPowTou = html[cardNameStart:cardNameEnd]
    else:
        return None
    return cardPowTou.strip()  # strip function removes leading and ending whitespaces


def getSet(html):
    cardNameStart = html.find('prints-current-set-name">') + 25
    cardNameEnd = html.find('</span>', cardNameStart)
    setName = html[cardNameStart:cardNameEnd]
    return setName.strip()  # strip function removes leading and ending whitespaces


def getSetDetails(html):
    cardNameStart = html.find('prints-current-set-details">') + 30
    cardNameEnd = html.find('</span>', cardNameStart)
    setDetails = html[cardNameStart:cardNameEnd].strip()
    x = setDetails.split("·", 3)
    return x  # strip function removes leading and ending whitespaces


# change function to return a array of the form [set number, rarity, language]

def getCardImage(html):
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
    count = html.count("card-text-mana-cost")
    if count > 1:
        return True
    return False


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def main():
    setCsv = pd.read_csv("setInfo.csv")
    setCodes = list(setCsv.expansionCode)
    setSize = list(setCsv.numberOfCards)
    tracker = 0
    for code in setCodes:
        for j in range(1, setSize[tracker] + 1):
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


main()
