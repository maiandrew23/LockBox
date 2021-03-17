import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)

def info():
  '''Prints a basic library description'''
  print("Software library for the Lockbox project.")

class Solenoid:
  def __init__(self):
    print("Solenoid setup fininshed")
  def open(self):
    print("Solenoid is open")

  def close(self):
    print("Solenoid is closed")

class Keypad:
  def __init__(self):
    GPIO.setup(17, GPIO.IN, GPIO.PUD_DOWN)

    print("Keypad setup finished")
  def readKey(self):
    return GPIO.input(17)

class Display:
  def __init__(self):
    print("Display setup finished")

  def on(self):
    print("Display is on")

  def off(self):
    print("Display is off")

  def showText(self, text):
    print("'" + text + "'", "on display")

class Printer:
  def __init__(self):
    print("Printer setup finished")
  def sendText(self, word):
    print(word, "is being printed")



class Lockbox:
  def __init__(self):
    self.keypad = Keypad()
    self.printer = Printer()
    self.display = Display()
    self.solenoid = Solenoid()
