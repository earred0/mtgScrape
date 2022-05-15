# mtgScrape
In an attempt to learn how to webscrape, I scraped all of the standard legal cards created in the past 8 years and compiled them into a CSV. Originally I was going to use beautiful soup to decode Scryfall, but their code was presented in a very clean matter, it was not necessary. 

I then practiced manipulating the data using pandas and matplotlib. dataScrape.py consists of a script that plots the rarity distrbution on a single page in a simple and visually pleasing way. 

dataScrape.py : Creates a set of pie graphs. Created as an exercise for data visualization

historyOfSet.csv : The csv file that main appends to. Contains all of the standard legal Magic the Gathering sets created in the past 8 years. Contains information such as: name, mana cost, card type, creature type, power and toughness, set name, set number, rarity, language and a URL to the card image. 

main.py: The application that scrapes the information. Depends on the information in setInfo to run. Compiles all of the card information into the CSV historyOfSet.csv

setData.csv: Similar to history of sets, but contains a single set. Good for testing on.

setInfo.csv: Contains information such as set name, set code, and set number 

pricetest.csv: Contains the same information as setInfo but includes a current price. 

