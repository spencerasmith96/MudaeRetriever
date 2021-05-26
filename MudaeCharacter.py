class MudaeCharacter:
    """Data of a single character from the Mudae bot"""

    def __init__(self, name : str, aliases : list[str], imgLink : str, waifu : bool = False, husbando : bool = False):
        self.name = name
        self.aliases = aliases
        self.imgLink = imgLink
        self.waifu = waifu
        self.husbando = husbando