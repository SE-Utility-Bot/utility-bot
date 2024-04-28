import re
import sys
import os

import sechat

EMAIL = os.environ["email"]
PASSWORD = os.environ["password"]
EVENT_NAME = os.environ["event"]
EVENT_USER = os.environ["actor"]

cleaned = re.sub(r"\[.*\]", "", EVENT_USER)

bot = sechat.Bot()
bot.login(EMAIL, PASSWORD)
r = bot.joinRoom(152883)


def indent(text):
    return "\n".join("    " + x for x in text.split("\n"))


r.send(
    f'Event "{EVENT_NAME}" was triggered by {f"[{cleaned}](https://github.com/{cleaned})"}.'
)
