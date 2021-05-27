from KeyboardCommanding import writeCommand
from typing import Union

class NameRetriever:
    """Functions to retrieve and store character names from the Mudae bot"""
    def __init__(self):
        self.maxRank = 0
        self.names = set()
        self.lastCommand : callable
        self.__maxRankPrefix = "No result! Max rank: "

    def requestCharacter(self, rank: int):
        requestMessage = "$top #" + str(rank)
        writeCommand(requestMessage)

    def addName(self, name):
        if name in self.names:
            return False

        self.names.add(name)

    def validCharacterPrefix(self, message: str, rank: int):
        prefix = "**#" + str(rank) + " - "
        return message.startswith(prefix)

    def parseCharacterName(self, message: str, rank: int) -> Union[bool, str]:
        if(not self.validCharacterPrefix(message, rank)):
            return False

        prefix = "**#" + str(rank) + " - "
        leftIgnore = len(prefix)
        rightIgnore = message.rfind("**", leftIgnore)
        name = message[leftIgnore:rightIgnore]
        return name

    def requestCharacterNum(self):
        requestMessage = "$top #"
        writeCommand(requestMessage)
        self.lastCommand = self.requestCharacterNum

    def validMax(self, message: str):
        prefix = self.__maxRankPrefix
        return message.startswith(prefix)

    def parseMaxCharacters(self, response: str):
        if(not self.validMax(response)):
            return False

        prefix = self.__maxRankPrefix
        leftIgnore = len(prefix)
        self.maxRank = int(response[leftIgnore:])
        return self.maxRank