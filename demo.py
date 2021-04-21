import lockbox
import time
from threading import Thread, Event

lb = lockbox.Lockbox()
lb.solenoid.setup()
lb.display.setup()
lb.printer.setup()
lb.keypad.setup()
print("")

print("TESTING SOLENOID")
lb.solenoid.open()
lb.solenoid.close()
print("==============================\n")

print("TESTING DISPLAY\n")
lb.display.off()
time.sleep(5)
lb.display.on()
print("Sending \"Hello World!\" to display...")
lb.display.show_text("Hello", 1)
lb.display.show_text("World!", 2)
print("==============================\n")

print("TESTING PRINTER\n")
print("Sending \"Hello\" to be printed")
lb.printer.print_text("Hello")
print("==============================\n")

def start_keypad():
  while lb.keypad.is_on():
    key = lb.keypad.read_key()
    if key != None:
      print(key)
    time.sleep(0.2)

print("TESTING KEYPAD\n")
lb.keypad.on()
print("Try pressing buttons on keypad for the next 10 seconds")
t1 = Thread(target=start_keypad)
t1.start()
time.sleep(10)
lb.keypad.off()
t1.join()
print("==============================\n")


print("Demo complete!")
