import discord
import os
import asyncio
from datetime import datetime, date
from MudaeCharacter import MudaeCharacter
from NameRetriever import NameRetriever
from dotenv import load_dotenv
from time import sleep

prefix = "?"
mudaeID = 432610292342587392

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

def logError(error: str):
    errorFile = open("errorlog.txt", "a", encoding='utf-8')
    currentTime = datetime.now().strftime("%H:%M:%S")
    currentDay = date.today().strftime("%m/%d/%Y")
    fullErrorMessage = currentDay + " - " + currentTime + " - " + error + "\n"
    errorFile.write(fullErrorMessage)
    errorFile.close()

async def retrieveMaxChars(channel, names):
    """Calls and retrieves max number of characters from Mudae using Discord.
    Stores in names on sucess or returns False."""
    maxRetry = 3

    ### Find Max number of characters ####
    maxRankMessage = False
    for retry in range(maxRetry):
        names.requestCharacterNum()
        
        def check(message):
            return message.author.id == mudaeID and on_message.names.validMax(message.content)

        try:
            maxRankMessage = await client.wait_for('message', check=check, timeout = 5.0)
        except asyncio.TimeoutError:
            await channel.send("Mudae timed out. Attempt (" + str(retry + 1) + "/" + str(maxRetry) + ")")

        if(maxRankMessage != False): # Names retrieves successfully
            break
    
    if(maxRankMessage == False): # Retries end, log error and quit
        errorMsg = "Unable to retrieve max characters. Aborting."
        await channel.send(errorMsg)
        logError(errorMsg)
        return False

    ### Get max chars in form of an int ###
    maxChars = names.parseMaxCharacters(maxRankMessage.content)
    if(maxChars == False): # Unable to get the int
        errorMsg = "Error, unable to parse max characters. Message: " + maxRankMessage.content
        await channel.send(errorMsg)
        logError(errorMsg)
        return False

    return maxChars

async def retrieveNames(startRank: int, endRank: int, names, channel):
    """Adds the names of characters from startRank to endRank into the names object, logs any error"""
    maxRetry = 3

    for rank in range(startRank, endRank):    
        ### Retrieve character name for rank ###
        charRankMessage = False
        for retry in range(maxRetry):
            sleep(1)
            names.requestCharacter(rank)

            def check(message):
                return message.author.id == mudaeID and on_message.names.validCharacterPrefix(message.content, rank)

            try:
                charRankMessage = await client.wait_for('message', check=check, timeout = 2.0)
            except asyncio.TimeoutError:
                await channel.send("Mudae timed out. Retrying (" + str(retry + 1) + "/" + str(maxRetry) + ")")

            if(charRankMessage != False): # Names retrieves successfully
                break

        if(charRankMessage == False):
            errorMsg = "Mudae timed out for rank:" + str(rank)
            await channel.send(errorMsg)
            logError(errorMsg)
            sleep(60)
            continue

        name = names.parseCharacterName(charRankMessage.content, rank)
        if(name == False):
            logError("Error requesting name from: " + charRankMessage.content)
            continue

        result = on_message.names.addName(name)
        if(result == False):
            logError("Unable to add name: " + name + " at rank: " + str(rank))
            continue

def saveNames(names, rank):
    """ Saves names to txt document """
    if(names.maxRank != 0):
        percent = format((rank/names.maxRank) * 100, ".2f")
        print("Progress: ", percent, "%", sep='')

    namesFile = open("names.txt", "w", encoding='utf-8')
    characterString = '\n'.join(names.names)
    namesFile.write("Characters: " + str(rank) + "\n" + characterString)
    namesFile.close()

def loadNames(names):
    """ Loads names in names.names set and returns last saved rank """
    namesFile = open("names.txt", "r", encoding='utf-8')

    progressLine = namesFile.readline().rsplit(' ', 1)
    lastRank = progressLine[1].strip()
    if(lastRank.isdigit() == False):
        namesFile.close()
        return False

    lastRank = int(lastRank)
    thisNames = set(namesFile.read().splitlines())
    names.names = thisNames
    namesFile.close()
    return lastRank

@client.event
async def on_message(message):
    if message.author == client.user:
        return  
    
    # Requests and compiles a list of all character names from Mudae
    if message.content.startswith(prefix + "getName"):
        maxChars = await retrieveMaxChars(message.channel, on_message.names)
        if(maxChars == False):
            return
        bulk = 100
        for rankStep in range(1, maxChars, bulk):
            endRange = rankStep + bulk
            if(endRange >= maxChars):
                endRange = maxChars + 1
            await retrieveNames(rankStep, endRange, on_message.names, message.channel)
            saveNames(on_message.names, endRange)

    if message.content.startswith(prefix + "continue"):
        lastRank = loadNames(on_message.names)
        if(lastRank == False):
            logError("Unable to read last rank")
            return
        maxChars = await retrieveMaxChars(message.channel, on_message.names)
        if(maxChars == False):
            return
        bulk = 100
        for rankStep in range(lastRank, maxChars, bulk):
            endRange = rankStep + bulk
            if(endRange >= maxChars):
                endRange = maxChars + 1
            await retrieveNames(rankStep, endRange, on_message.names, message.channel)
            saveNames(on_message.names, endRange)

    if message.content.startswith(prefix + "hunt"):
        leftignore = len(prefix + "hunt") + 1
        args:list = message.content[leftignore:].split(' ')
        badInputMsg = "Ussage: " + prefix + "hunt " + "[search point] [extent to search]"
        if(len(args) < 2):
            await message.channel.send(badInputMsg)
            return
        try:
            suggest = int(args[0])
            bounds = int(args[1])
        except:
            await message.channel.send(badInputMsg)
            return

        loadNames(on_message.names)
        if(suggest == False):
            logError("Unable to read last rank")
            return
        maxChars = await retrieveMaxChars(message.channel, on_message.names)
        if(maxChars == False):
            return

        missing = maxChars - len(on_message.names.names)
        print("Missing characters:",  missing)
        lbound = suggest - bounds
        rbound = suggest + bounds
        if(lbound <= 0): lbound = 1
        if(rbound >= maxChars): rbound = maxChars
    
        await retrieveNames(lbound, rbound, on_message.names, message.channel)
        saveNames(on_message.names, rbound)

        remaining = maxChars - len(on_message.names.names)
        foundChars = missing - remaining
        print("Done. Found:", foundChars, "Remaining:", remaining)


    if message.content.startswith(prefix + "add"):
        lastRank = loadNames(on_message.names)
        left = len(prefix + "add")
        name = message.content[left:]
        name = name.strip()
        on_message.names.addName(name)
        saveNames(on_message.names, lastRank)
        


on_message.names = NameRetriever()

client.run(TOKEN)