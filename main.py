import html
import re
import secrets
import subprocess
import sys
import os
import time
import requests
from typing import Optional
from urllib.request import urlopen
from urllib.parse import quote
import multiprocessing

from flask import Flask

import sechat
from deep_translator import GoogleTranslator

import asyncio

from sechat import Credentials, Room
from sechat.events import MessageEvent

# import streamlit as st

#c = Conversation()
#h = pipeline("conversational", pad_token_id=0)
#last_msg = ""

app = Flask(__name__)
@app.route("/")
def page():
    return "<h1 style='text-align: center;'><a href='https://chat.stackexchange.com/rooms/1/sandbox'>Try it here</a></h1>"

main_ = __name__ == "__main__"

def message_handler(message: str, message_id: int, sender: int, sender_name: str, room: Optional[Room] = None) -> str:
    if (result := re.match(
            r"🐟 <i>(.*)'s line quivers\.<\/i>",
            html.unescape(message),
            re.UNICODE,
    )) and sender == 375672:
        return(f"@{result.group(1).replace(' ', '')} your fish is ready!")
    elif message[:5] == "echo ":
        if sender == 540406 or message[5:10] != "/fish":
            return(html.unescape(message[5:]))
        else:
            return(
                build_reply(message_id, "Sorry, I cannot do that."))
    elif message[:8] == "echochr ":
        return(html.unescape(chr(int(message[8:]))))
    elif message[:5] == "calc ":
        string = html.unescape(message[5:])
        def send_r():
            room.send(indent(urlopen(f"https://safe-exec.onrender.com/calc/{quote(string, safe='')}").read().decode("utf-8")))
        p = multiprocessing.Process(target=send_r)
        p.start()
        p.join(15)
        if p.is_alive():
            p.kill()
            return(build_reply(message_id, "Request took too long."))
    elif message[:5] == "ping ":
        return("@" + re.sub(" ", "", html.unescape(message[5:])))
    elif message == "getsource":
        return(
            build_reply(
                message_id,
                "https://github.com/SE-Utility-Bot/utility-bot/blob/main/main.py",
            ))
    elif message[:6] == "getcmd":
        commands = {
            "echo <message>":
            "                      Sends the message given to it.",
            "echochr <character number>":
            "          Sends the unicode character with the codepoint of the number given to it. Must be in base 10.",
            "calc <python expression>":
            "            Sends the answer to the given Python expression. Times out after 10 seconds.",
            "ping <user name>":
            "                    Pings the person with the username that was passed to it.",
            "getsource":
            "                           Sends a link to the source code.",
            "getcmd <command>":
            "                    Sends the command description. If no command is given, it lists the commands with their descriptions instead.",
            "emptystring":
            "                         Sends a picture of an empty string.",
            "help":
            "                                Shows some information.",
            "op / status":
            "                         Replies with a random message from statuses.txt. Exists to quickly check whether the bot is running.",
            "webscrape <URL>":
            "                     Sends the HTML content of the specified URL.",
            "random <quantity>, <start>, <end>":
            "   Sends the specified number of random numbers in the inclusive range (using secrets.choice). 1 argument uses the range 0 to 255, and 2 arguments uses the range 0 to <end>. Maximum argument value is 1000 for <quantity> and 9 * 10 ** 18 for all other arguments.",
            "translate <text> | <to> | <from>":
            "    Translates <text> from the language code in <from> (automatically detects language if none is given) to the language code in <to> (translates to English if none is given). See https://utility-bot.streamlit.app/Supported_translation_languages for supported languages and their language codes.",
            "fishinv":
            "                             Get's the bot's fishing inventory, with the fishing game being run by OakBot.",
            "setting <setting>, <value>":
            "        Changes the specified setting to the specified boolean value",

        }
        if len(message) > 6:
            try:
                return(
                    build_reply(
                        message_id,
                        "`" + (result := [
                            x for x in commands if re.match(
                                message.partition(" ")[2], x)
                        ][0]) + "`: " + commands[result],
                    ))
            except IndexError:
                return(
                    build_reply(message_id,
                                    "Command does not exist."))
        else:
            return(
                indent(
                    f"@{sender_name.replace(' ', '')}\nHere are the available commands for this bot and their structures:\n\n"
                    + ("\n".join(f"{chr(8226)} {x}: {commands[x]}"
                                    for x in commands)), ))
    elif message == "emptystring":
        return(
            build_reply(message_id,
                            "https://i.stack.imgur.com/Fh2Cq.png"))
    elif message == "help":
        return(
            build_reply(
                message_id,
                'Type in "getcmd" (without the quotes) for a list of commands and their descriptions.\n\nRepo: https://github.com/SE-Utility-Bot/utility-bot\nWebsite: https://utility-bot.streamlit.app/\nCalculation Module: https://github.com/SE-Utility-Bot/safe-exec',
            ))
    elif message in ("op", "status"):
        with open("status.txt") as f, open(__file__) as g:
            return(
                build_reply(
                    message_id,
                    secrets.choice(f.read().split("\n")).replace("\\n", "\n").replace(
                        "[prog_rand]",
                        secrets.choice(g.read().split("\n"))),
                ))
    elif message[:10] == "webscrape ":
        try:
            return(
                indent(
                    f"@{sender_name.replace(' ', '')}" +
                    "\nHere is the source code of the HTML webpage:\n\n" +
                    urlopen(message[10:]).read().decode("utf-8")))
        except Exception as err:  # skipcq: PYL-W0703
            return(build_reply(message_id, f"`{repr(err)}`"))

    elif message[:7] == "random ":
        args = [int(x) for x in message[7:].split(",")]
        if len(args) == 1:
            args.append(0)
            args.append(255)
        elif len(args) == 2:
            args.insert(1, 0)
        if args[0] > 1000 or any(x > 9 * 10**18 for x in args):
            return(
                build_reply(
                    message_id,
                    "Sorry, that will probably take me too long."))
        else:
            numbers = [
                secrets.choice(range(args[1], args[2] + 1))
                for x in range(args[0])
            ]
            return(
                build_reply(message_id,
                                f"Here are your random numbers:\n{numbers}"))
    elif message[:10] == "translate ":
        arguments = [
            remove_space(x)
            for x in html.unescape(message[10:]).split("|")
        ]
        while len(arguments) < 3:
            arguments.append("auto")
        return(
            build_reply(
                message_id,
                GoogleTranslator(**dict(
                    zip(
                        ["target", "source"],
                        [
                            a if (a := arguments[1]) != "auto" else "en",
                            arguments[2],
                        ],
                    ))).translate(arguments[0]),
            ))
    elif message == "fishinv":
        return("/fish inv")

    elif message[:6] == "shell ":
        if sender == 540406:
            try:
                output = subprocess.getoutput(message[6:])
                return(indent(build_reply(message_id, '\n' + output)))
            except:
                return(build_reply(message_id, "An error occured while executing the command."))
        else:
            return(build_reply(message_id, "You don't have permission, sorry!"))
            
    elif message[:4] == "run ":
        string = html.unescape(message[4:])
        def send_r():
            room.send(indent(urlopen(f"https://safe-exec.onrender.com/run/{quote(string, safe='')}").read().decode("utf-8")))
        p = multiprocessing.Process(target=send_r)
        p.start()
        p.join(15)
        if p.is_alive():
            p.kill()
            return(build_reply(message_id, "Request took too long."))

    elif message[:6] == "paste ":
        string = html.unescape(message[6:]).replace("<br>","\n")
        req = requests.post("https://pastebin.com/api/api_post.php", data={"api_dev_key": os.environ["PASTEBIN_API_KEY"], "api_option": "paste", "api_paste_code": string, "api_paste_format": "python", "api_paste_private": 0}, timeout=15)
        return(build_reply(message_id, req.text))

async def onn(room: Room):
    async for event in room.events():
        if type(event) is MessageEvent:
            result = message_handler(event.content, event.message_id, event.user_id, event.user_name, room)
            if result is not None:
                room.send(result)

def build_reply(message_id: int, message: str):
    return f":{message_id} {message}"

def indent(text):
    return "\n".join("    " + x for x in text.split("\n"))


def remove_lead_space(text):
    it = iter(text)
    # skipcq: PTC-W0047
    while (result := next(it)) == " ":  # skipcq: PTC-W0063
        pass
    return result + "".join(it)


def remove_space(text):
    lead_space_x = remove_lead_space(text)
    return remove_lead_space(lead_space_x[::-1])[::-1]

def tobool(val, truthy=["true", "1", "on", "y", "yes", "t", "i"], falsy=["false", "0", "off", "n", "no", "f", "o"], strfunc = (lambda x: str(x).lower())):
    ch = strfunc(val)
    print(ch)
    if ch in truthy:
        return True
    elif ch in falsy:
        return False
    else:
        return None

def errortodefault(func, default=None):
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return default
    return f

def mainf():
    bot = Credentials.authenticate(os.environ["BOT_EMAIL"], os.environ["BOT_PASSWORD"])
    [r, baso, ubot] = map(lambda x:Room.join(bot, x), [1, 146039, 154629])
    for room in [r, baso, ubot]:
        onn(room, bot)

if main_:
    mainf()
