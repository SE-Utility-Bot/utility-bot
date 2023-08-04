import html
import sechat
from sechat.events import Events
import sys
import os
import time
import re
import decimal
import datetime
from urllib.request import urlopen

bot = sechat.Bot()
bot.login(sys.argv[1], sys.argv[2])
r = bot.joinRoom(1)
bot.joinRoom(147516).send("No freezing!")


def indent(string):
    return "\n".join("    " + x for x in string.split("\n"))


def remote(event):
    if event.content[:10] == "remotesay ":
        r.send(event.user_name + ": " + html.unescape(event.content[10:]))
        g.send(g.buildReply(event.message_id, "Message sent."))


def msg(event):
    if event.content[:5] == "echo ":
        r.send(html.unescape(event.content[5:]))
    elif event.content[:8] == "echochr ":
        r.send(html.unescape(chr(int(event.content[8:]))))
    elif event.content[:5] == "calc ":
        allowed = {
            "+",
            "-",
            "*",
            "/",
            "=",
            "!",
            "<",
            ">",
            "&",
            "|",
            "^",
            "~",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "0",
            " ",
            "(",
            ")",
            ".",
            "%",
        }
        string = html.unescape(event.content[5:])
        val = set(string)
        if val.issubset(allowed):
            r.send(
                r.buildReply(
                    event.message_id, "The answer is " + str(eval(string)) + "."
                )
            )
        else:
            r.send(
                r.buildReply(
                    event.message_id,
                    "Sorry, only characters in the set "
                    + str(sorted(allowed))
                    + " are allowed due to security reasons.",
                )
            )
    elif event.content[:5] == "ping ":
        r.send("@" + re.sub(" ", "", html.unescape(event.content[5:])))
    elif event.content[:10] == "remotesay ":
        global g
        com = html.unescape(event.content[10:])
        li = com.partition(",")
        if li[1] == "":
            li = ("147516", ",", li[0])

        if li[0] == "147571":
            r.send(r.buildReply(event.message_id, "Sorry, I'm afraid I can't do that."))
        else:
            g = bot.joinRoom(int(li[0]))
            g.send(event.user_name + ": " + li[2])
            g.on(Events.MESSAGE, remote)
            r.send(r.buildReply(event.message_id, "Message sent."))
    elif event.content == "getsource":
        r.send(
            r.buildReply(
                event.message_id,
                "https://github.com/PlaceReporter99/utility-bot/blob/main/utilitybot.py",
            )
        )
    elif event.content == "getcmd":
        commands = {
            "echo <message>": "Sends the message given to it.",
            "echochr <character number>": "Sends the unicode character with the codepoint of the number given to it. Must be in base 10.",
            "calc <python expression>": "Sends the answer to the given Python expression. Uses a restricted character set due to security reasons.",
            "ping <user name>": "Pings the person with the username that was passed to it.",
            "remotesay <room>, <message>": "Sends a message in the specified room ID. If no room ID is given, the room defaults to Sandbox 2.",
            "getsource": "Sends a link to the source code.",
            "getcmd": "Lists the commands with their descriptions.",
            "emptystring": "Sends a picture of an empty string.",
            "help": "Shows some information.",
            "op": 'Replies with the message "All systems operational!". Exists to quickly check whether the bot is running.',
            "webscrape <URL>": "Sends the HTML content of the specified URL.",
        }
        r.send(
            r.buildReply(
                event.message_id,
                "Here are the available commands for this bot and their structures:\n\n"
                + ("\n".join(f"• {x}: {commands[x]}" for x in commands.keys())),
            )
        )
    elif event.content == "emptystring":
        r.send(r.buildReply(event.message_id, "https://i.stack.imgur.com/Fh2Cq.png"))
    elif event.content == "help":
        r.send(
            r.buildReply(
                event.message_id,
                'Type in "getcmd" (without the quotes) for a list of commands and their descriptions.\n\nRepo: https://github.com/PlaceReporter99/utility-bot',
            )
        )
    elif event.content == "op":
        r.send(r.buildReply(event.message_id, "All systems operational."))
    elif event.content[:10] == "webscrape ":
        r.send(
            r.buildReply(
                event.message_id,
                "Here is the source code of the HTML webpage:\n\n"
                + indent(urlopen(event.content[10:]).read().decode("utf-8")),
            )
        )


r.on(Events.MESSAGE, msg)
print("Startup Successful.")

try:
    counter = 0
    r.send("Bot has started.")
    while True:
        print("Bot is running. Seconds since start: {}".format(counter))
        time.sleep(1)
        counter += 1
finally:
    r.send("Bot has stopped for updates.")
    bot.leaveAllRooms()
