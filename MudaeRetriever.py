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

def saveNames(names):
    """ Saves names to txt document """

    print("Progress: ", (rank/names.maxRank) * 100, "%", sep='')

    namesFile = open("names.txt", "w", encoding='utf-8')
    namesFile.write("Characters: " + str(rank) + "\n" + str(names.names))
    namesFile.close()

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
            await retrieveNames(1, maxChars, on_message.names, message.channel)
            saveNames(on_message.names)

on_message.names = NameRetriever()

client.run(TOKEN)