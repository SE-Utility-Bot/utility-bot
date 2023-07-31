import sechat
import secrets
import sys
import time
import re

EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
TESTING_ROOM = 147571
BOT_ID = 576644
BOT = sechat.Bot()
BOT.login(EMAIL, PASSWORD)
ROOM = BOT.joinRoom(1)

def meta(a, b, c):
  """
  Metaclass for the Tests class, so that testing is as easy as doing Tests().
  """
  def func():
    for x in list(c.values())[3:]:
      x()
  
  return func

class Tests(metaclass=meta):
  """
  Testing functions go in this class.
  Every function must take no arguments, not even the self argument.
  """
  def test_message_send():
    p = BOT.joinRoom(TESTING_ROOM)
    MSG = "The bot is undergoing a test. Please do not send any messages until said otherwise."
    p.send(MSG)
    message = p.getRecentMessages()[-1]
    p.send("You may now send messages.")
    assert (message['content'] == MSG and message['user_id'] == BOT_ID)
    
  def test_start():
    ROOM.send("Bot is being tested. Do not send any messages until otherwise stated by me, or The Empty String Photographer.")
  
  def test_echo():
    hext = secrets.token_hex(16)
    ROOM.send("echo {}".format(hext))
    time.sleep(2)
    message = ROOM.getRecentMessages()[-1]
    assert message['content'] == hext

  def test_calc():
    rand1, rand2 = secrets.randbits(256), secrets.randbits(256)
    result = rand1 * rand2
    ROOM.send("calc {0} * {1}".format(rand1, rand2))
    time.sleep(2)
    message = ROOM.getRecentMessages()[-1]
    number = message['content'][26:-1]
    assert result == int(number)
  def test_finish():
    ROOM.send("You may continue sending messages.")
    
