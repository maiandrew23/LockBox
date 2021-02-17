import lockbox

lb = Lockbox()

lb.solenoid.open()
lb.solenoid.close()

lb.keypad.readkey()

lb.display.on()
lb.display.off()
lb.display.showText()

lb.printer.senText("Test")

