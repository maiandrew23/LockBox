def info():  
  '''Prints a basic library description'''
  print("Software library for the Lockbox project.")


class Lockbox:
 
  class Solenoid:
    def __init__(self):
      pass    
    def open():
      return True

    def close():
      return True

  class Keypad:
    def __init__(self):
      
    def readKey():
      return "String"

  class Display:
    
    def __init__(self):

    def on():

    def off():
    
  class Printer:
    def __init__(self):
      pass
    def sendText(word):
      pass

  def __init__(self):
    keypad = Keypad()
    printer = Printer()
    display = Display()
    solenoid = Solenoid()
