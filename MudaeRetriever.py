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
    fullErrorMessage = currentDay + currentTime + error + "\n"
    errorFile.write(fullErrorMessage)
    errorFile.close()

@client.event
async def on_message(message):
    if message.author == client.user:
        return  
    
    # Requests and compiles a list of all character names from Mudae
    if message.content.startswith(prefix + "getName"):

        # Request max chars
        maxRetry = 3
        for retry in range(maxRetry):
            on_message.names.requestCharacterNum()
        
            def check(message):
                print("valid?")
                print(message.content)
                return message.author.id == mudaeID and on_message.names.validMax(message.content)

            try:
                maxRankMessage = await client.wait_for('message', check=check, timeout = 5.0)
            except asyncio.TimeoutError:
                await message.channel.send("Mudae timed out. Retrying (" + str(retry + 1) + "/" + str(maxRetry) + ")")
                if(retry + 1 == maxRetry):
                    return
            else:
                break


        response = on_message.names.parseMaxCharacters(maxRankMessage.content)
        if(response == False):
            print("Error, unable to parse max characters. Message:", maxRankMessage.content)
            return

        # Get name for every rank
        bulk = 100 #Saves every 100 entries
        for rank in range(1, on_message.names.maxRank + 1):
            maxRetry = 3
            for retry in range(maxRetry):
                sleep(0.5)
                on_message.names.requestCharacter(rank)

                def check(message):
                    return message.author.id == mudaeID and on_message.names.validCharacterPrefix(message.content, rank)

                try:
                    charRankMessage = await client.wait_for('message', check=check, timeout = 2.0)
                except asyncio.TimeoutError:
                    await message.channel.send("Mudae timed out. Retrying (" + str(retry + 1) + "/" + str(maxRetry) + ")")
                    if(retry + 1 == maxRetry):
                        logError("Mudae timed out for rank:" + str(rank))
                        return
                else:
                    break

            name = on_message.names.parseCharacterName(charRankMessage.content, rank)
            if(name == False):
                logError("Error requesting name from: " + charRankMessage.content)
                continue

            result = on_message.names.addName(name)
            if(result == False):
                logError("unable to add name: " + name + " at rank: " + str(rank))
                continue

            if(rank % bulk == 0):
                print("Progress: ", (rank/on_message.names.maxRank) * 100, "%", sep='')
                namesFile = open("names.txt", "w")
                namesFile.write("Characters: " + str(rank) + "\n" + str(on_message.names.names))
                namesFile.close()

        namesFile = open("names", "w")
        namesFile.write(str(on_message.names.names))
        namesFile.close()



        
on_message.names = NameRetriever()

client.run(TOKEN)