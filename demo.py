import lockbox
import time

lb = lockbox.Lockbox()

lb.solenoid.open()
lb.solenoid.close()
print("Try pressing button 3 ")
for i in range(50):
  input = lb.keypad.readKey()
  if input:
    print("Button IS pressed")
  else:
    print("Button is NOT pressed")
  time.sleep(0.1)

print(lb.keypad.readKey())

lb.display.off()
time.sleep(5)
lb.display.on()
lb.display.showText("Test1")

lb.printer.sendText("Test2")

print("Demo complete!")
