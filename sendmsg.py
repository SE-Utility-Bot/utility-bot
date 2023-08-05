import sechat
import sys

EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
EVENT_NAME = sys.argv[3]
EVENT_DATA = sys.argv[4]

bot = sechat.Bot()
bot.login(EMAIL, PASSWORD)
r = bot.joinRoom(147676)

r.send(f"event {EVENT_NAME} occured. Data: {EVENT_DATA}")
