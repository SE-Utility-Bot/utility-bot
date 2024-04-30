import os

import sechat

EMAIL = os.environ["email"]
PASSWORD = os.environ["password"]
MSG = os.environ["message"]
ROOM = os.environ["room"]

bot = sechat.Bot()
bot.login(EMAIL, PASSWORD)
r = bot.joinRoom(int(ROOM))
r.send(MSG)