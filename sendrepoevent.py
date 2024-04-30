import re
import sys
import os

import requests
import sechat

EMAIL = os.environ["email"]
PASSWORD = os.environ["password"]
EVENT_NAME = os.environ["event"]
EVENT_USER = os.environ["actor"]
PAYLOAD = os.environ["payload"]
PASTEBIN_KEY = os.environ["pastebin"]

CLEANED = re.sub(r"\[.*\]", "", EVENT_USER)

bot = sechat.Bot()
bot.login(EMAIL, PASSWORD)
r = bot.joinRoom(152883)

def pastebin(text, key):
    return requests.post("https://pastebin.com/api/api_post.php", data = {'api_dev_key': key, 'api_option': 'paste', 'api_paste_code': text, 'api_paste_private': '1'}).text

def indent(text):
    return "\n".join("    " + x for x in text.split("\n"))


r.send(f'Event "{EVENT_NAME}" was triggered by [{CLEANED}](https://github.com/{CLEANED}). The [payload]({pastebin(PAYLOAD, PASTEBIN_KEY)}) is linked.')