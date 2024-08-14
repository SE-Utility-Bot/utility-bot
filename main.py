import html
import re
import secrets
import subprocess
import sys
import os
import time
from urllib.request import urlopen
from flask import Flask

import sechat
from deep_translator import GoogleTranslator
from sechat.events import Events

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

with open('database_auth.json') as f:
    print(f.read())
cred = credentials.Certificate('database_auth.json')
print(cred)
f_init = firebase_admin.initialize_app(cred)
print(f_init)
db = firestore.client()
print(db)

# import streamlit as st

#c = Conversation()
#h = pipeline("conversational", pad_token_id=0)
#last_msg = ""

app = Flask(__name__)
@app.route("/")
def page():
    return "<h1 style='text-align: center;'><a href='https://chat.stackexchange.com/rooms/1/sandbox'>Try it here</a></h1>"

main_ = __name__ == "__main__"


def onn(room):
    room.on(Events.MESSAGE, roomer(room))


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

def dataread(coll, user, key):
    try:
        return db.collection(coll).document(user).to_dict()[key]
    except BaseException as e:
        print(e)
        return None

def datawrite(coll, user, key, value):
    return db.collection(coll).document(user).set({key: value}, merge=True)

def datatoggle(coll, user, key):
    return datawrite(coll, user, key, not dataread(coll, user, key))

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

def roomer(r):

    def msg(event):
        rid = r.roomID
        nofish = [146039]
        if (result := re.match(
                r"🐟 <i>(.*)'s line quivers\.<\/i>",
                html.unescape(event.content),
                re.UNICODE,
        )) and event.user_id == 375672:
            if result.group(1) == "Utility Bot" and rid not in nofish:
                r.send("/fish again")
            else:
                settingr = dataread("settings", result.group(1), "fishping")
                if settingr == None:
                    datawrite("settings", result.group(1), "fishping", False)
                elif settingr:
                    r.send(
                        f"@{result.group(1).replace(' ', '')} your fish is ready!")
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
            val = set(string)
            result = []
            try:
                r.send(
                    r.buildReply(
                        event.message_id,
                        "The answer is\n" + subprocess.check_output([
                            "timeout",
                            "-s",
                            "SIGKILL",
                            "10s",
                            "python3",
                            "calculate.py",
                            string,
                        ]).decode("utf-8").replace("\n", ""),
                    ) + ".", )
            except subprocess.CalledProcessError:
                r.send(
                    r.buildReply(
                        event.message_id,
                        "Sorry, the calculation took longer than 10 seconds.",
                    ))
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
                    "https://github.com/PlaceReporter99/utility-bot/blob/main/utilitybot.py",
                ))
        elif event.content[:6] == "getcmd":
            commands = {
                "echo <message>":
                "                      Sends the message given to it.",
                "echochr <character number>":
                "          Sends the unicode character with the codepoint of the number given to it. Must be in base 10.",
                "calc <python expression>":
                "            Sends the answer to the given Python expression. Uses a restricted character set due to security reasons. Times out after 10 seconds.",
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
                    'Type in "getcmd" (without the quotes) for a list of commands and their descriptions.\n\nRepo: https://github.com/PlaceReporter99/utility-bot\nWebsite: https://utility-bot.streamlit.app/',
                ))
        elif event.content in ("op", "status"):
            with open("status.txt") as f, open(__file__) as g:
                r.send(
                    r.buildReply(
                        event.message_id,
                        secrets.choice(f.read().split("\n")).replace(
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

        elif event.content[:8] == "setting ":
            setting, value = map(remove_space, event.content[8:].split(","))
            bool_settings = ["fishping"]
            int_settings = []
            if setting in bool_settings:
                value = tobool(value)
                if value == None:
                    r.send(r.buildReply(event.message_id, "The provided value isn't a recognised boolean."))
                    return
            elif setting in int_settings:
                value = errortodefault(int)(value)
                if value == None:
                    r.send(r.buildReply(event.message_id, "The provided value isn't a recognised number."))
                    return
            try:
                datawrite("settings", event.user_name, setting, value)
            except:
                r.send(r.buildReply(event.message_id, "Setting could not be saved."))
            else:
                r.send(r.buildReply(event.message_id, "Setting changed!"))
    return msg


if main_:
    bot = sechat.Bot()
    bot.login(os.environ["BOT_EMAIL"], os.environ["BOT_PASSWORD"])
    def repeat():
        [r, baso, ubot] = map(bot.joinRoom, [1, 146039, 154629])
        for room in [r, baso, ubot]:
            onn(room)
        ubot.send(f"Wake up, it's antifreeze time!")
    repeat()
    app.run(host='0.0.0.0', port=5000)
    try:
        counter = 0
        print("Startup Successful.")
        while True:
            print(f"Bot is running. Seconds since start: {counter}")
            # st.write(f"Bot is running. Seconds since start: {counter}")
            time.sleep(1)
            counter += 1
    finally:
        r.send("Bot has stopped for updates.")
        bot.leaveAllRooms()
