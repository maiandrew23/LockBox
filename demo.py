import lockbox

lb = lockbox.Lockbox()

lb.solenoid.open()
lb.solenoid.close()

lb.keypad.readKey()

lb.display.on()
lb.display.off()
lb.display.showText("Test1")

lb.printer.sendText("Test2")

print("Demo complete!")
