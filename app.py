import lockbox
import time
from threading import Thread, Event

lb = lockbox.Lockbox()
lb.solenoid.setup()
lb.display.setup()
lb.printer.setup()
lb.keypad.setup()
print("")
