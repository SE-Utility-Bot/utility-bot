import sechat
import sys
import re
from urllib.parse import quote

EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
EVENT_NAME = sys.argv[3]
EVENT_USER = sys.argv[4]

bot = sechat.Bot()
bot.login(EMAIL, PASSWORD)
r = bot.joinRoom(147676)


def indent(text):
    return "\n".join("    " + x for x in text.split("\n"))


r.send(
    f'Event "{EVENT_NAME}" was triggered by {f"[{(cleaned := re.sub('[.*]','',EVENT_USER))}](https://github.com/{quote(cleaned)})"}.'
)
