import sechat
import secrets
import sys
import time

EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
TESTING_ROOM = 147571
BOT_ID = 576644

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
    bot = sechat.Bot()
    bot.login(EMAIL, PASSWORD)
    p = bot.joinRoom(TESTING_ROOM)
    MSG = "The bot is undergoing a test. Please do not send any messages until said otherwise."
    p.send(MSG)
    message = p.getRecentMessages()[-1]
    p.send("You may now send messages.")
    assert (message['content'] == MSG and message['user_id'] == BOT_ID)

  def test_echo():
    bot = sechat.Bot()
    bot.login(EMAIL, PASSWORD)
    p = bot.joinRoom(1)
    p.send("Bot is being tested. Do not send any messages.")
    hext = secrets.token_hex(16)
    p.send("echo {}".format(hext))
    time.sleep(2)
    message = p.getRecentMessages()[-1]
    p.send("You may continue sending messages.")
    assert message['content'] == hext
    
