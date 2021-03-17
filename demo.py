import lockbox
import time

lb = lockbox.Lockbox()

lb.solenoid.open()
lb.solenoid.close()

print(lb.keypad.readKey())

lb.display.off()
time.sleep(5)
lb.display.on()
lb.display.showText("Test1")

lb.printer.sendText("Test2")

print("Demo complete!")
