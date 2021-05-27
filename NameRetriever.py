from KeyboardCommanding import writeCommand

class NameRetriever:
    """Functions to retrieve and store character names from the Mudae bot"""
    def __init__(self):
        self.currentRank = 0
        self.maxRank = 0
        self.lastCommand : callable

    def requestNext(self):
        self.currentRank += 1
        if(self.currentRank > self.maxRank):
            return False

        requestMessage = "$top #" + str(self.currentRank)
        writeCommand(requestMessage)
        return True

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