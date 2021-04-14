import lockbox
import time
from flask import Flask, redirect, render_template

lb = lockbox.Lockbox()
lb.solenoid.setup()
lb.display.setup()
lb.printer.setup()
lb.keypad.setup()
print("")

lb.keypad.on()

app = Flask(__name__, static_folder='')

@app.route("/")
def home():
  print("Home page")
  return app.send_static_file('html/index.html')

@app.route("/admin")
def admin():
  print("Admin")
  return app.send_static_file('html/admin.html')

@app.route("/admin/<int:menu>")
def menu():
  if menu == 1:
  	#print receipt
  if menu == 2:
  	pass
  return redirect("/admin")

@app.route("/admin/displayAll")
def displayAll():
	return app.render_template("html/displayAll.html", devices=devices)

@app.route("/admin/displayAll/delete/<string:item>")
def deleteDevice():
  print("Delete " + item)
  return app.render_template("html/displayAll.html", devices=devices)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

devices = {}

def verify():
    lb.display.show_text("Are You Sure?")
    return lb.Keypad.read_key()

def menu():
    menu = 1
    while(True):
        #Register New Device
        if menu == 1:
            lb.display.show_text("Register New Device")
            input = lb.Keypad.read_key()
            if input == '*':#Selected
                input = verify()
                if input == '*':#Verified Yes
                    #TODO: Register device and print receipt
                    menu = 2
                elif input == '#':#Verified No
                    menu == 1
            elif input == '#':#Down
                menu = 2
        #Lock Device
        elif menu == 2:
            lb.display.show_text("Lock Device")
            input = lb.Keypad.read_key()
            if input == '*':#Selected
                lb.display.show_text("Enter Device #")
                device_num = ""
                for i in range(4):
                    device_num += lb.Keypad.read_key()
                if device_num in devices:#Valid Device Number
                    count = 0
                    while count < 2:
                        lb.display.show_text("Enter Passcode")
                        passcode = ""
                        for i in range(4):
                            passcode += lb.Keypad.read_key()
                        if devices[device_num] == passcode:#Correct passcode
                            lb.display.show_text("Insert Your Device")
                            input = lb.Keypad.read_key()
                            if input == '*':#Lock was selected
                                #TODO: Start timer for device
                                lb.solenoid.close()
                                lb.display.show_text("Locked!")
                                input = ""
                                while input != "*":#Back to Main Menu
                                    input = lb.Keypad.read_key()
                                menu = 1
                            elif input == '#':#Cancel
                                menu = 1
                            count = 2
                        else:#Incorrect passcode
                            lb.display.show_text("Wrong Passcode")
                            input = lb.Keypad.read_key()
                            if input == "*":#Try Again selected
                                count += 1
                            elif input == "#":#Back to Main Menu
                                menu = 1
                else:
                    lb.display.show_text("Device Not Found")
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.Keypad.read_key()
                    menu = 1
            elif input == '#':#Down
                menu = 3
        elif menu == 3:
            pass
