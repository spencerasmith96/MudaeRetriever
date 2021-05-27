import discord
import os
import asyncio
from MudaeCharacter import MudaeCharacter
from NameRetriever import NameRetriever
from dotenv import load_dotenv

prefix = "?"
mudaeID = 432610292342587392

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


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
                return message.author.id == mudaeID

            try:
                message = await client.wait_for('message', check=check, timeout = 5.0)
            except asyncio.TimeoutError:
                await message.channel.send("Mudae timed out. Retrying (" + str(retry + 1) + "/" + str(maxRetry) + ")")
                if(retry + 1 == maxRetry):
                    return
            else:
                break


        response = on_message.names.parseMaxCharacters(message.content)
        if(response == False):
            print("Error, unable to parse max characters. Message:", message.content)
            return

        # Get name for every rank
        for rank in range(1, on_message.names.maxRank + 1):
            maxRetry = 3
            for retry in range(maxRetry):
                on_message.names.requestCharacter(rank = rank)

                def check(message):
                    return message.author.id == mudaeID

                try:
                    message = await client.wait_for('message', check=check, timeout = 2.0)
                except asyncio.TimeoutError:
                    await message.channel.send("Mudae timed out. Retrying (" + str(retry + 1) + "/" + str(maxRetry) + ")")
                    if(retry + 1 == maxRetry):
                        return
                else:
                    break

            name = on_message.names.parseCharacterName(message.content, rank)
            if(name == False):
                print("Error requesting name from:", message.content)
                continue
            result = on_message.names.addName(name)
            if(result == False):
                print("Error, name:", name, "might already exist. (Rank:", rank, ")")

        namesFile = open("names", "w")
        namesFile.write(str(on_message.names.names))



        
on_message.names = NameRetriever()

client.run(TOKEN)