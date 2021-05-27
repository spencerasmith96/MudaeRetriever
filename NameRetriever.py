from KeyboardCommanding import writeCommand
from typing import Union

class NameRetriever:
    """Functions to retrieve and store character names from the Mudae bot"""
    def __init__(self):
        self.maxRank = 0
        self.names = set()
        self.lastCommand : callable

    def requestCharacter(self, rank: int):
        requestMessage = "$top #" + str(rank)
        writeCommand(requestMessage)

    def addName(self, name):
        if name in self.names:
            return False

        self.names.add(name)

    def parseCharacterName(self, message: str, rank: int) -> Union[bool, str]:
        prefix = "**#" + str(rank) + " - "
        if(not message.startswith(prefix)):
            return False

        leftIgnore = len(prefix)
        rightIgnore = message.rfind("**", leftIgnore)
        name = message[leftIgnore:rightIgnore]
        return name

    def requestCharacterNum(self):
        requestMessage = "$top #"
        writeCommand(requestMessage)
        self.lastCommand = self.requestCharacterNum

    def parseMaxCharacters(self, response: str):
        prefix = "No result! Max rank: "
        if(not response.startswith(prefix)):
            return False

        leftIgnore = len(prefix)
        self.maxRank = int(response[leftIgnore:])
        return self.maxRank