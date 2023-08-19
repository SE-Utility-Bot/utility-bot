from utilitybot import roomer
import sechat
from sechat.events import Events
import sys
import time

bot = sechat.Bot()
bot.login(sys.argv[1], sys.argv[2])
r = bot.joinRoom(147805)
r.send("@TheE PR test deployed. You have 6 hours to test it.")

r.on(Events.MESSAGE, roomer(r))

try:
    while True:
        print("Bot is running")
        time.sleep(5)
finally:
    bot.leaveAllRooms()
