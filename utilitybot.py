import html
import sechat
from sechat.events import Events
import sys
import os
import time
import re
import decimal
import datetime
import multiprocessing
from urllib.request import urlopen

main_ = __name__ == "__main__"

if main_:
    bot = sechat.Bot()
    bot.login(sys.argv[1], sys.argv[2])
    r = bot.joinRoom(1)
    t = bot.joinRoom(147676)
    priv = bot.joinRoom(147571)
    sb2 = bot.joinRoom(147516)


def indent(string):
    return "\n".join("    " + x for x in string.split("\n"))


def remote(event):
    if event.content[:10] == "remotesay ":
        r.send(event.user_name + ": " + html.unescape(event.content[10:]))
        g.send(g.buildReply(event.message_id, "Message sent."))


def roomer(r):
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
            result = []
            if val.issubset(allowed):

                def calculate():
                    nonlocal string
                    nonlocal result
                    result.append(eval(string))
                
                calculate()

                r.send(
                    r.buildReply(
                        event.message_id, "The answer is " + str(result[0]) + "."
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
                r.send(
                    r.buildReply(event.message_id, "Sorry, I'm afraid I can't do that.")
                )
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
        elif event.content[:6] == "getcmd":
            commands = {
                "echo <message>": "                      Sends the message given to it.",
                "echochr <character number>": "          Sends the unicode character with the codepoint of the number given to it. Must be in base 10.",
                "calc <python expression>": "            Sends the answer to the given Python expression. Uses a restricted character set due to security reasons.",
                "ping <user name>": "                    Pings the person with the username that was passed to it.",
                "remotesay <room>, <message>": "         Sends a message in the specified room ID. If no room ID is given, the room defaults to Sandbox 2.",
                "getsource": "                           Sends a link to the source code.",
                "getcmd <command>": "                    Sends the command description. If no command is given, it lists the commands with their descriptions instead.",
                "emptystring": "                         Sends a picture of an empty string.",
                "help": "                                Shows some information.",
                "op": '                                  Replies with the message "All systems operational.". Exists to quickly check whether the bot is running.',
                "webscrape <URL>": "                     Sends the HTML content of the specified URL.",
                "random <quantity>, <start>, <end>": "   Sends the specified number of random numbers in the inclusive range (using os.urandom). 1 argument uses the range 0 to 255, and 2 arguments uses the range 0 to <end>.",
            }
            if len(event.content) > 6:
                try:
                    r.send(
                        r.buildReply(
                            event.message_id,
                            "`"
                            + (
                                result := [
                                    x
                                    for x in commands.keys()
                                    if re.match(event.content.partition(" ")[2], x)
                                ][0]
                            )
                            + "`: "
                            + commands[result],
                        )
                    )
                except IndexError:
                    r.send(r.buildReply(event.message_id, "Command does not exist."))
            else:
                r.send(
                    indent(
                        f"@{event.user_name}\nHere are the available commands for this bot and their structures:\n\n"
                        + (
                            "\n".join(
                                f"{chr(8226)} {x}: {commands[x]}"
                                for x in commands.keys()
                            )
                        ),
                    )
                )
        elif event.content == "emptystring":
            r.send(
                r.buildReply(event.message_id, "https://i.stack.imgur.com/Fh2Cq.png")
            )
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
                    indent(
                        "\nHere is the source code of the HTML webpage:\n\n"
                        + urlopen(event.content[10:]).read().decode("utf-8")
                    ),
                )
            )
        elif event.content[:7] == "random ":
            args = [int(x) for x in event.content[7:].split(',')]
            if len(args) == 1:
                r.send(r.buildReply(event.message_id, "Here are your random numbers: " + str([*os.urandom(args[0])])))
            elif len(args) == 2:
                r.send(r.buildReply(event.message_id, "Here are your random numbers: " + str([(args[1] * x) // 255 for x in os.urandom(args[0])])))
            elif len(args) == 3:
                r.send(r.buildReply(event.message_id, "Here are your random numbers: " + str([(((args[2] - args[1]) * x) // 255) + args[1] for x in os.urandom(args[0])])))

    return msg


if main_:
    r.on(Events.MESSAGE, roomer(r))
    t.on(Events.MESSAGE, roomer(t))
    priv.on(Events.MESSAGE, roomer(priv))
    sb2.on(Events.MESSAGE, roomer(sb2))

    try:
        counter = 0
        print("Startup Successful.")
        r.send("Bot has started.")
        t.send("Bot has started.")
        priv.send("Bot has started.")
        sb2.send("Bot has started. No freezing!")
        while True:
            print("Bot is running. Seconds since start: {}".format(counter))
            time.sleep(1)
            counter += 1
    finally:
        r.send("Bot has stopped for updates.")
        bot.leaveAllRooms()
