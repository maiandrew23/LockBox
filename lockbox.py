def info():
  '''Prints a basic library description'''
  print("Software library for the Lockbox project.")

class Solenoid:
  def __init__(self):
    pass
  def open(self):
    return True

  def close(self):
    return True

class Keypad:
  def __init__(self):
    pass
  def readKey(self):
    return "String"

class Display:
  def __init__(self):
    pass

  def on(self):
    return True

  def off(self):
    return True

  def showText(self, text):
    print(text)

class Printer:
  def __init__(self):
    pass
  def sendText(self, word):
    print(word)



class Lockbox:
  def __init__(self):
    self.keypad = Keypad()
    self.printer = Printer()
    self.display = Display()
    self.solenoid = Solenoid()
