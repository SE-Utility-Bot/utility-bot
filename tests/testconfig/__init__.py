from testhelper import metaclass

import sechat
import sys

EMAIL = sys.argv[1]
PASSWORD = sys.argv[2]
TESTING_ROOM = 147571

class Tests(metaclass=metaclass):
  """
  Testing functions go in this class.
  """
  def test_message_send(self):
    bot = sechat.Bot()
    bot.login(EMAIL, PASSWORD)
    p = bot.joinRoom(TESTING_ROOM)
    MSG = "The bot is undergoing a test. Please do not send any messages until said otherwise."
    p.send(MSG)
    message = r.getRecentMessages()[-1]
    p.send("You may now send messages.")
    bot.leaveRoom(TESTING_ROOM)
    del p
    assert (message['content'] == MSG and message['user_id'] == 576644)
