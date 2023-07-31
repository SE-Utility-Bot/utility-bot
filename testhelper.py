def metaclass(a, b, c):
  """
  Metaclass for the Tests class, so that testing is as easy as doing Tests().
  """
  return Ctuple(c.values())[2:]

class Ctuple(tuple):
  """
  A class representing a callable tuple, which calls everything inside it. Used in the metaclass function.
  """
  def __call__(self, *args, **kwargs):
    return Ctuple(x(*args, **kwargs) for x in self)
