import html
import sechat
from sechat.events import Events
import sys
import os
import time
import re
import decimal
from mfunc.mfunc import mfunc
bot=sechat.Bot()
bot.login("computertext@outlook.com","MyLaptop+9")
r=bot.joinRoom(1)
r.send("Bot has started.")
def remote(event):
    if event.content[:10]=="remotesay ":
        r.send(event.user_name+": "+html.unescape(event.content[10:]))
        g.send(g.buildReply(event.message_id,"Message sent."))
def msg(event):
    if event.content[:5]=="echo ":
        r.send(html.unescape(event.content[5:]))
    elif event.content[:8]=="echochr ":
        r.send(html.unescape(chr(int(event.content[8:]))))
    elif event.content[:5]=="calc ":
        allowed={'+','-','*','/','=','!','<','>','&','|','^','~','1','2','3','4','5','6','7','8','9','0',' ','(',')','.','%'}
        string=html.unescape(event.content[5:])
        val=set(string)
        if val.issubset(allowed):
            if string=="^^^":
                r.send(r.buildReply(event.message_id,"Disabled for security reasons."))
            else:
                r.send(r.buildReply(event.message_id,'The answer is '+str(eval(string))+'.'))
        else:
            r.send(r.buildReply(event.message_id,'Sorry, only characters in the set '+str(sorted(allowed))+' are allowed due to security reasons.'))
    elif event.content[:5]=="ping ":
        r.send('@'+re.sub(" ","",html.unescape(event.content[5:])))
    elif event.content[:10]=="remotesay ":
        global g
        com=html.unescape(event.content[10:])
        li=com.partition(',')
        g=bot.joinRoom(int(li[0]))
        g.send(event.user_name+': '+li[2])
        g.on(Events.MESSAGE,remote)
        r.send(r.buildReply(event.message_id,"Message sent."))
    elif event.content[:8]=="suggest ":
        h=open("suggestions.txt","a")
        h.write("User no. "+str(event.user_id)+":\n"+html.unescape(event.content[8:])+"\n\n")
        h.close()
        r.send(r.buildReply(event.message_id,"Your suggestion has been recorded. Thank you for your feedback."))
    elif event.content=="getsource":
        k=open(__file__)
        l=k.readlines()
        for y in range(len(l)):
            l[y]="    "+l[y]
        source=l[13:-8]
        actual=''.join(source)
        r.send(r.buildReply(event.message_id,"Here are the callable functions for this bot:"))
        r.send(actual)
    elif event.content=="getcmd":
        commands=['• echo','• echochr','• calc','• ping','• remotesay','• suggest','• getsource','• getcmd','• emptystring']
        r.send(r.buildReply(event.message_id, "Here are the available commands for this bot:"))
        r.send('\n'.join(commands))
    elif event.content=="emptystring":
        r.send(r.buildReply(event.message_id, "https://i.stack.imgur.com/Fh2Cq.png"))
r.on(Events.MESSAGE,msg)
print("Startup Successful.")
try:
    while True:
        pass
finally:
    r.send("Bot has stopped for updates.")
    bot.leaveAllRooms()
