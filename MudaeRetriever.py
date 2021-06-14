import discord
import os
import asyncio
from datetime import datetime, date
from MudaeCharacter import MudaeCharacter
from NameRetriever import NameRetriever
from dotenv import load_dotenv
from time import sleep
import keyboard

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
            except:
                raise

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

async def commandContinueNames(channel):
    try:
        lastRank = on_message.names.load()
        if(lastRank == False):
            logError("Unable to read last rank")
            return
        maxChars = await retrieveMaxChars(channel, on_message.names)
        if(maxChars == False):
            return
        bulk = 100
        for rankStep in range(lastRank, maxChars, bulk):
            endRange = rankStep + bulk
            if(endRange >= maxChars):
                endRange = maxChars + 1
            await retrieveNames(rankStep, endRange, on_message.names, channel)
            on_message.names.save(endRange)
    except asyncio.CancelledError:
        on_message.names.save(rankStep)
        print("Cancelled.")

async def commandHuntNames(channel, suggest, bounds):
    try:
        on_message.names.load()
        maxChars = await retrieveMaxChars(channel, on_message.names)
        if(maxChars == False):
            return

        missing = maxChars - len(on_message.names.names)
        print("Missing characters:",  missing)
        lbound = suggest - bounds
        rbound = suggest + bounds
        if(lbound <= 0): lbound = 1
        if(rbound >= maxChars): rbound = maxChars
    
        await retrieveNames(lbound, rbound, on_message.names, channel)
        on_message.names.save(rbound)

        remaining = maxChars - len(on_message.names.names)
        foundChars = missing - remaining
        print("Done. Found:", foundChars, "Remaining:", remaining)
    except asyncio.CancelledError:
        on_message.names.save(lbound)
        print("Cancelled.")
        remaining = maxChars - len(on_message.names.names)
        foundChars = missing - remaining
        print("Found:", foundChars, "Remaining:", remaining)

async def commandGetAllNames(channel):
    try:
        maxChars = await retrieveMaxChars(channel, on_message.names)
        if(maxChars == False):
            return
        bulk = 100
        for rankStep in range(1, maxChars, bulk):
            endRange = rankStep + bulk
            if(endRange >= maxChars):
                endRange = maxChars + 1
            await retrieveNames(rankStep, endRange, on_message.names, channel)
            on_message.names.save(endRange)
    except asyncio.CancelledError:
        on_message.names.save(rankStep)
        print("Cancelled.")

def cancelCommand(task, keyboardEvent):
    task.cancel()
    print("Canceling!")


async def startCommand(command, *args):
    task = asyncio.create_task(command(*args))
    hookCancel = keyboard.on_release_key('esc', lambda a: cancelCommand(task, a))
    await task
    keyboard.unhook(hookCancel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return  
    
    # Requests and compiles a list of all character names from Mudae
    if message.content.startswith(prefix + "getName"):
        await startCommand(commandGetAllNames, message.channel)
        return

    if message.content.startswith(prefix + "continue"):
        await startCommand(commandContinueNames, message.channel)
        return

    if message.content.startswith(prefix + "hunt"):
        leftignore = len(prefix + "hunt") + 1
        args:list = message.content[leftignore:].split(' ')
        badInputMsg = "Ussage: " + prefix + "hunt [search point] [extent to search]"
        if(len(args) < 2):
            await message.channel.send(badInputMsg)
            return
        try:
            suggest = int(args[0])
            bounds = int(args[1])
        except:
            await message.channel.send(badInputMsg)
            return

        await startCommand(commandHuntNames, message.channel, suggest, bounds)
        return

    if message.content.startswith(prefix + "listen"):
        def check(message):
            return message.author.id == mudaeID

        newMessage = await client.wait_for('message', check=check)
        print("Message:")
        embed = newMessage.embeds[0]
        print(embed.image.url)
        print(embed.description) # 1st line: Series_Name <:emoji:>
        print(embed.author.name) # Name
        return

    if message.content.startswith(prefix + "add"):
        lastRank = on_message.names.load()
        left = len(prefix + "add")
        name = message.content[left:]
        name = name.strip()
        on_message.names.addName(name)
        on_message.names.save(lastRank)
        return
        


on_message.names = NameRetriever()

client.run(TOKEN)