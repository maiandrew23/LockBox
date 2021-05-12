from Adafruit_Thermal import *
import RPi.GPIO as GPIO
import time
from threading import Thread, Event
from RPLCD import CharLCD
#Solenoid Globals
SOL_CONTROL = 16

# LCD Globals
LCD_RS = 6
LCD_E  = 5
LCD_D4 = 13
LCD_D5 = 19
LCD_D6 = 26
LCD_D7 = 1
LCD_CHR = GPIO.HIGH   # High in data (character) mode
LCD_CMD = GPIO.LOW    # Low in instruction (command) mode

# Important commands
LCD_CLEAR = [0,0,0,0,0,0,0,1]
LCD_D_OFF = [0,0,0,0,1,0,0,0]
LCD_D_ON = [0,0,0,0,1,1,0,0]
LCD_4BIT1 = [0,0,1,1,0,0,1,1]
LCD_4BIT2 = [0,0,1,1,0,0,1,0]
LCD_ON_NC = [0,0,0,0,1,1,0,0]
LCD_ENTRY = [0,0,0,0,0,1,1,0]
LCD_LINE_1 = [1,0,0,0,0,0,0,0]
LCD_LINE_2 = [1,1,0,0,0,0,0,0]

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

def info():
  '''Prints a basic library description'''
  print("Software library for the Lockbox project.")

class Solenoid:
  def setup(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOL_CONTROL, GPIO.OUT)
    print("Solenoid setup fininshed")

  def open(self):
    GPIO.output(SOL_CONTROL, GPIO.HIGH)
    print("Solenoid is open")

  def close(self):
    GPIO.output(SOL_CONTROL, GPIO.LOW)
    print("Solenoid is closed")

class Keypad:
  def __init__(self):
    self.activated = False
    self.lcd = CharLCD(cols=16, rows=2, pin_rs=6, pin_e=5, pins_data=[13,19,26,1],numbering_mode=GPIO.BCM)

  def setup(self):
    GPIO.setmode(GPIO.BCM)
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
  def setup(self):
    GPIO.setmode(GPIO.BCM)
    self.lcd = CharLCD(cols=16,rows=2,pin_rs=6,pin_e=5,pins_data=[13,19,26,1],numbering_mode=GPIO.BCM)
    self.lcd.cursor_mode = 'hide'
    print("Display setup finished")

  def clear(self):
    self.lcd.clear()
    return


  def show_text(self, text, line=1):
    if line == 1:
      self.lcd.cursor_pos = (0,0)
      self.lcd.write_string("                ")
      self.lcd.cursor_pos = (0,0)
      self.lcd.write_string(text)

    elif line == 2:
      self.lcd.cursor_pos = (1,0)
      self.lcd.write_string("                ")
      self.lcd.cursor_pos = (1,0)
      self.lcd.write_string(text)

class Printer:
  def __init__(self):
    self.printer_device = None

  def setup(self):
    self.printer_device = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)
    print("Printer setup finished")

  def print_text(self, word):
    self.printer_device.println(word)
    print(word, "is being printed")

class Lockbox:
  def __init__(self):
    GPIO.setwarnings(False)
    self.keypad = Keypad()
    self.printer = Printer()
    self.display = Display()
    self.solenoid = Solenoid()
