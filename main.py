import html
import re
import secrets
import subprocess
import sys
import os
import time
import requests
from urllib.request import urlopen
from urllib.parse import quote
import multiprocessing

from flask import Flask

import sechat
from deep_translator import GoogleTranslator
from sechat.events import Events

# import streamlit as st

#c = Conversation()
#h = pipeline("conversational", pad_token_id=0)
#last_msg = ""

app = Flask(__name__)
@app.route("/")
def page():
    return "<h1 style='text-align: center;'><a href='https://chat.stackexchange.com/rooms/1/sandbox'>Try it here</a></h1>"

main_ = __name__ == "__main__"


def onn(room, bot):
    room.on(Events.MESSAGE, roomer(room, bot))


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


def remote(event):
    if event.content[:10] == "remotesay ":
        r.send(event.user_name + ": " + html.unescape(event.content[10:]))
        g.send(g.buildReply(event.message_id, "Message sent."))

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

def roomer(r, bot):

    def msg(event):
        try:
            rid = r.roomID
            nofish = [146039]
            if (result := re.match(
                    r"🐟 <i>(.*)'s line quivers\.<\/i>",
                    html.unescape(event.content),
                    re.UNICODE,
            )) and event.user_id == 375672:
                r.send(f"@{result.group(1).replace(' ', '')} your fish is ready!")
            elif event.content[:5] == "echo ":
                if event.user_id == 540406 or event.content[5:10] != "/fish":
                    r.send(html.unescape(event.content[5:]))
                else:
                    r.send(
                        r.buildReply(event.message_id, "Sorry, I cannot do that."))
            elif event.content[:8] == "echochr ":
                r.send(html.unescape(chr(int(event.content[8:]))))
            elif event.content[:5] == "calc ":
                string = html.unescape(event.content[5:])
                def send_r():
                    r.send(indent(urlopen(f"https://safe-exec.onrender.com/calc/{quote(string, safe='')}").read().decode("utf-8")))
                p = multiprocessing.Process(target=send_r)
                p.start()
                p.join(15)
                if p.is_alive():
                    p.kill()
                    r.send(r.buildReply(event.message_id, "Request took too long."))
            elif event.content[:5] == "ping ":
                r.send("@" + re.sub(" ", "", html.unescape(event.content[5:])))
            elif event.content[:10] == "remotesay ":
                com = html.unescape(event.content[10:])
                li = com.partition(",")
                if li[1] == "":
                    li = ("147516", ",", li[0])

                if li[0] == "147571":
                    r.send(
                        r.buildReply(event.message_id,
                                     "Sorry, I'm afraid I can't do that."))
                else:
                    global g  # skipcq: PYL-W0601
                    g = bot.joinRoom(int(li[0]))
                    g.send(event.user_name + ": " + li[2])
                    g.on(Events.MESSAGE, remote)
                    r.send(r.buildReply(event.message_id, "Message sent."))
            elif event.content == "getsource":
                r.send(
                    r.buildReply(
                        event.message_id,
                        "https://github.com/SE-Utility-Bot/utility-bot/blob/main/main.py",
                    ))
            elif event.content[:6] == "getcmd":
                commands = {
                    "echo <message>":
                    "                      Sends the message given to it.",
                    "echochr <character number>":
                    "          Sends the unicode character with the codepoint of the number given to it. Must be in base 10.",
                    "calc <python expression>":
                    "            Sends the answer to the given Python expression. Times out after 10 seconds.",
                    "ping <user name>":
                    "                    Pings the person with the username that was passed to it.",
                    "remotesay <room>, <message>":
                    "         Sends a message in the specified room ID. If no room ID is given, the room defaults to Sandbox 2.",
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
                if len(event.content) > 6:
                    try:
                        r.send(
                            r.buildReply(
                                event.message_id,
                                "`" + (result := [
                                    x for x in commands if re.match(
                                        event.content.partition(" ")[2], x)
                                ][0]) + "`: " + commands[result],
                            ))
                    except IndexError:
                        r.send(
                            r.buildReply(event.message_id,
                                         "Command does not exist."))
                else:
                    r.send(
                        indent(
                            f"@{event.user_name.replace(' ', '')}\nHere are the available commands for this bot and their structures:\n\n"
                            + ("\n".join(f"{chr(8226)} {x}: {commands[x]}"
                                         for x in commands)), ))
            elif event.content == "emptystring":
                r.send(
                    r.buildReply(event.message_id,
                                 "https://i.stack.imgur.com/Fh2Cq.png"))
            elif event.content == "help":
                r.send(
                    r.buildReply(
                        event.message_id,
                        'Type in "getcmd" (without the quotes) for a list of commands and their descriptions.\n\nRepo: https://github.com/SE-Utility-Bot/utility-bot\nWebsite: https://utility-bot.streamlit.app/\nCalculation Module: https://github.com/SE-Utility-Bot/safe-exec',
                    ))
            elif event.content in ("op", "status"):
                with open("status.txt") as f, open(__file__) as g:
                    r.send(
                        r.buildReply(
                            event.message_id,
                            secrets.choice(f.read().split("\n")).replace("\\n", "\n").replace(
                                "[prog_rand]",
                                secrets.choice(g.read().split("\n"))),
                        ))
            elif event.content[:10] == "webscrape ":
                try:
                    r.send(
                        indent(
                            f"@{event.user_name.replace(' ', '')}" +
                            "\nHere is the source code of the HTML webpage:\n\n" +
                            urlopen(event.content[10:]).read().decode("utf-8")))
                except Exception as err:  # skipcq: PYL-W0703
                    r.send(r.buildReply(event.message_id, f"`{repr(err)}`"))

            elif event.content[:7] == "random ":
                args = [int(x) for x in event.content[7:].split(",")]
                if len(args) == 1:
                    args.append(0)
                    args.append(255)
                elif len(args) == 2:
                    args.insert(1, 0)
                if args[0] > 1000 or any(x > 9 * 10**18 for x in args):
                    r.send(
                        r.buildReply(
                            event.message_id,
                            "Sorry, that will probably take me too long."))
                else:
                    numbers = [
                        secrets.choice(range(args[1], args[2] + 1))
                        for x in range(args[0])
                    ]
                    r.send(
                        r.buildReply(event.message_id,
                                     f"Here are your random numbers:\n{numbers}"))
            elif event.content[:10] == "translate ":
                arguments = [
                    remove_space(x)
                    for x in html.unescape(event.content[10:]).split("|")
                ]
                while len(arguments) < 3:
                    arguments.append("auto")
                r.send(
                    r.buildReply(
                        event.message_id,
                        GoogleTranslator(**dict(
                            zip(
                                ["target", "source"],
                                [
                                    a if (a := arguments[1]) != "auto" else "en",
                                    arguments[2],
                                ],
                            ))).translate(arguments[0]),
                    ))
            elif event.content == "fishinv":
                r.send("/fish inv")

            elif event.content[:6] == "shell ":
                if event.user_id == 540406:
                    try:
                        output = subprocess.getoutput(event.content[6:])
                        r.send(indent(r.buildReply(event.message_id, '\n' + output)))
                    except:
                        r.send(r.buildReply(event.message_id, "An error occured while executing the command."))
                else:
                    r.send(r.buildReply(event.message_id, "You don't have permission, sorry!"))
                    
            elif event.content[:4] == "run ":
                string = html.unescape(event.content[4:])
                def send_r():
                    r.send(indent(urlopen(f"https://safe-exec.onrender.com/run/{quote(string, safe='')}").read().decode("utf-8")))
                p = multiprocessing.Process(target=send_r)
                p.start()
                p.join(15)
                if p.is_alive():
                    p.kill()
                    r.send(r.buildReply(event.message_id, "Request took too long."))

            elif event.content[:6] == "paste ":
                string = html.unescape(event.content[6:]).replace("<br>","\n")
                req = requests.post("https://pastebin.com/api/api_post.php", data={"api_dev_key": os.environ["PASTEBIN_API_KEY"], "api_option": "paste", "api_paste_code": string, "api_paste_format": "python", "api_paste_private": 0}, timeout=15)
                r.send(r.buildReply(event.message_id, req.text))
        except ConnectionError:
            bot.leaveAllRooms()
            mainf()
    return msg

def mainf():
    bot = sechat.Bot()
    bot.login(os.environ["BOT_EMAIL"], os.environ["BOT_PASSWORD"])
    [r, baso, ubot] = map(bot.joinRoom, [1, 146039, 154629])
    #ubot.send("Bot successfully redeployed!")
    for room in [r, baso, ubot]:
        onn(room, bot)

if main_:
    mainf()
    try:
        app.run(host='0.0.0.0', port=5000)
        while True:
            pass
    finally:
        bot.leaveAllRooms()
