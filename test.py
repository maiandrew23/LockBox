import RPi.GPIO as GPIO
import time
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LCD_RS = 6
LCD_E = 5
LCD_D4 = 13
LCD_D5 = 19
LCD_D6 = 26
LCD_D7 = 1

LCD_CHR = GPIO.HIGH
LCD_CMD = GPIO.LOW

LCD_CLEAR = [0,0,0,0,0,0,0,1]
LCD_D_OFF = [0,0,0,0,1,0,0,0]
LCD_4BIT1 = [0,0,1,1,0,0,1,1]
LCD_4BIT2 = [0,0,1,1,0,0,1,0]
LCD_ON_NC = [0,0,0,0,1,1,0,0]
LCD_ENTRY = [0,0,0,0,0,1,1,0]

E_PULSE = 0.0005
E_DELAY = 0.0005

def char_to_arr(c):
        return [int(b) for b in format(ord(c), '08b')]

def write_arr_4bit(bits, mode, debug=True):

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




def setup_lcd():
        GPIO.setup(LCD_RS, GPIO.OUT)
        GPIO.setup(LCD_E, GPIO.OUT)
        GPIO.setup(LCD_D4, GPIO.OUT)
        GPIO.setup(LCD_D5, GPIO.OUT)
        GPIO.setup(LCD_D6, GPIO.OUT)
        GPIO.setup(LCD_D7, GPIO.OUT)

        write_arr_4bit(LCD_4BIT1, LCD_CMD)
        write_arr_4bit(LCD_4BIT2, LCD_CMD)
        write_arr_4bit(LCD_ON_NC, LCD_CMD)
        write_arr_4bit(LCD_ENTRY, LCD_CMD)
        write_arr_4bit(LCD_CLEAR, LCD_CMD)

def string_to_lcd(word):
        for c in word:
                arr = char_to_arr(c)
                write_arr_4bit(arr, LCD_CHR)

try:
        setup_lcd()
        time.sleep(0.005)
        string_to_lcd('AM8760')
        time.sleep(600)
except KeyboardInterrupt:
        pass
finally:
        write_arr_4bit(LCD_CLEAR, LCD_CMD) #clear display
        write_arr_4bit(LCD_D_OFF, LCD_CMD) #0000 1000 Display off  - 5.2.4 datasheet
