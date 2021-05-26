# Writes commands as if I was typing
# Used so Mudae can respond (does not respond to bot accounts)

import keyboard

def writeCommand(command):
    keyboard.write(command)
    keyboard.press_and_release('enter')
