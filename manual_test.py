import sys
import time

import sechat
from sechat.events import Events

from utilitybot import onn

bot = sechat.Bot()
bot.login(sys.argv[1], sys.argv[2])
r = bot.joinRoom(147805)
r.send("@TheE PR test deployed. You have 6 hours to test it.")

onn(r)

try:
    while True:
        print("Bot is running")
        time.sleep(5)
finally:
    bot.leaveAllRooms()
