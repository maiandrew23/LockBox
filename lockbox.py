from Adafruit_Thermal import *
import RPi.GPIO as GPIO
import sys
import time
from threading import Thread, Event

# LCD Globals
LCD_RS = 6
LCD_E  = 5
LCD_D4 = 13
LCD_D5 = 19
LCD_D6 = 26
LCD_D7 = 1
LCD_CHR = GPIO.HIGH   # High in data (character) mode
LCD_CMD = GPIO.LOW    # Low in instruction (command) mode
LCD_LINE_1 = [1,0,0,0,0,0,0,0]
LCD_LINE_2 = [1,1,0,0,0,0,0,0]

# Important commands
LCD_CLEAR = [0,0,0,0,0,0,0,1]
LCD_D_OFF = [0,0,0,0,1,0,0,0]
LCD_D_ON = [0,0,0,0,1,1,0,0]
LCD_4BIT1 = [0,0,1,1,0,0,1,1]
LCD_4BIT2 = [0,0,1,1,0,0,1,0]
LCD_ON_NC = [0,0,0,0,1,1,0,0]
LCD_ENTRY = [0,0,0,0,0,1,1,0]

E_PULSE = 0.0005
E_DELAY = 0.0005
#===========================

# Keypad Globals
MATRIX = [['1','2','3'],
          ['4','5','6'],
          ['7','8','9'],
          ['*','0','#']]
ROW = [2,3,17,27]
COL = [22,23,24]
#===========================

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
    self.activated = False

    for i in range(len(COL)):
      GPIO.setup(COL[i], GPIO.IN, GPIO.PUD_DOWN)
    for i in range(len(ROW)):
      GPIO.setup(ROW[i], GPIO.OUT)
      GPIO.output(ROW[i], GPIO.LOW)
    print("Keypad setup finished")

  def on(self):
    self.activated = True
    print("Keypad is on")

  def off(self):
    self.activated = False
    print("Keypad is off")

  def is_on(self):
    return self.activated

  def read_key(self):
    while(self.activated):
      for i in range(len(ROW)):
        GPIO.output(ROW[i], GPIO.HIGH)
        for j in range(len(COL)):
          if GPIO.input(COL[j]) == GPIO.HIGH:
            while GPIO.input(COL[j]) == GPIO.HIGH:
              pass
            GPIO.output(ROW[i], GPIO.LOW)
            return MATRIX[i][j]
        GPIO.output(ROW[i], GPIO.LOW)
    return None

class Display:
  def __init__(self):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)

    self.write_arr_4bit(LCD_4BIT1, LCD_CMD)
    self.write_arr_4bit(LCD_4BIT2, LCD_CMD)
    self.write_arr_4bit(LCD_ON_NC, LCD_CMD)
    self.write_arr_4bit(LCD_ENTRY, LCD_CMD)
    self.write_arr_4bit(LCD_CLEAR, LCD_CMD)
    print("Display setup finished")

  def on(self):
    self.write_arr_4bit(LCD_D_ON, LCD_CMD)
    print("Display is on")

  def off(self):
    self.write_arr_4bit(LCD_D_OFF, LCD_CMD)
    print("Display is off")
  def char_to_arr(self, c):
    return [int(b) for b in format(ord(c), '08b')]


  def write_arr_4bit(self, bits, mode, debug=True):
    
    pins = [LCD_D7, LCD_D6, LCD_D5, LCD_D4]
    GPIO.output(LCD_RS, mode)
    # set the most significant bits (high bits) on data lines
    for p, b in zip(pins, bits[:4]):

      GPIO.setup(p, GPIO.OUT)
      GPIO.output(p, b)

    # pulse clock
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)

    #set lease significant bits on data lines
    for p, b in zip(pins, bits[4:]):
      GPIO.setup(p, GPIO.OUT)
      GPIO.output(p,b)
      # pulse clock
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)

    #reset pins to 0
    for p in pins:
      GPIO.output(p,GPIO.LOW)


  def show_text(self, text):
    for c in text:
      arr = self.char_to_arr(c)
      self.write_arr_4bit(arr, LCD_CHR)
    print("'" + text + "'", "on display")

class Printer:
  def __init__(self):
    self.printer_device = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)
    print("Printer setup finished")
  def print_text(self, word):
    self.printer_device.println(word)
    print(word, "is being printed")


class Lockbox:
  def __init__(self):
    self.keypad = Keypad()
    self.printer = Printer()
    self.display = Display()
    self.solenoid = Solenoid()


