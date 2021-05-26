import discord
import os
import json
import KeyboardCommanding
from dotenv import load_dotenv

prefix = "?"
mudaeID = 432610292342587392

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

def rankMessageToName(rank, message):
    rankLength = len(str(rank))
    constPadding = len("**# - ")
    left = rankLength + constPadding

    right = message.rfind("**")

    name = message[left:right]

    return name

def requestCharacters():
    requestCharacters.currentRank += 1
    requestMessage = "$top #" + str(requestCharacters.currentRank)
    KeyboardCommanding.writeCommand(requestMessage)

requestCharacters.currentRank = 0

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if(on_message.gettingCharacters and message.author.id == mudaeID):
        if(on_message.getStep == 0):
            on_message.getStep = 1
            on_message.name = rankMessageToName(requestCharacters.currentRank, message.content)
            return
        if(on_message.getStep == 1):
            print(on_message.name)
            return

    if message.content.startswith(prefix + "get"):
        on_message.gettingCharacters = True
        requestCharacters()
        return

on_message.gettingCharacters = False
on_message.getStep = 0

client.run(TOKEN)