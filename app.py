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
lb.display.on()

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
  pass
  return redirect("/admin")

@app.route("/admin/displayAll")
def displayAll():
	return app.render_template("html/displayAll.html", devices=devices)

@app.route("/admin/displayAll/delete/<string:item>")
def deleteDevice():
  #print("Delete " + item)
  return app.render_template("html/displayAll.html", devices=devices)

devices = {}

def validate_admin(lb):
    count = 0
    while count < 2:
        lb.display.show_text("Enter Passcode", 1)
        passcode = ""
        for i in range(4):
            passcode += lb.keypad.read_key()
        if passcode == lb.admin_passcode:
            return True
        else:
            lb.display.show_text("Wrong Passcode!", 1)
            #TODO: Display second line
            if count == 0:
                input = lb.keypad.read_key()
                if input == "*":#Try Again selected
                    count += 1
                elif input == "#":#Back to Main Menu
                    return False
            else:
                lb.display.show_text("Wrong Passcode!")
                #TODO: Display second line
                input = ""
                while input != "*":#Back to Main Menu
                    input = lb.keypad.read_key()
                return False
    return False

def validate_device(devices):
    lb.display.show_text("Enter Device #")
    device_num = ""
    for i in range(4):
        device_num += lb.keypad.read_key()
    if device_num in devices:#Valid Device Number
        count = 0
        while count < 2:
            lb.display.show_text("Enter Passcode")
            passcode = ""
            for i in range(4):
                passcode += lb.keypad.read_key()
            if devices[device_num] == passcode:#Correct passcode
               return device_num
            else:#Incorrect passcode
                lb.display.show_text("Wrong Passcode")
                if count == 0:
                    #TODO: Display second line
                    input = lb.keypad.read_key()
                    if input == "*":#Try Again selected
                        count += 1
                    elif input == "#":#Back to Main Menu
                        return None
                else:
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                    return None
    else:
        lb.display.show_text("Device Not Found")
        input = ""
        while input != "*":#Back to Main Menu
            input = lb.keypad.read_key()
        menu = 1

def lock(lb):
    lb.solenoid.close()

def unlock(lb):
    lb.solenoid.open()

def menu():
    menu = 1
    while(True):
        #Register New Device
        if menu == 1:
            lb.display.show_text("Register New Device")
            input = lb.keypad.read_key()
            if input == '*':#Selected
                lb.display.show_text("Are You Sure?")
                #TODO: Display second line
                input = lb.keypad.read_key()
                if input == '*':#Verified Yes
                    #TODO: Register device and print receipt
                    menu = 2
                elif input == '#':#Verified No
                    menu == 2
            elif input == '#':#Down
                menu = 2
        #Lock Device
        elif menu == 2:
            lb.display.show_text("Lock Device")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                device_num = validate_device(devices)
                if device_num:
                    unlock(lb)
                    lb.display.show_text("Insert Your Device")
                    #TODO: Display second line
                    input = lb.keypad.read_key()
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    #TODO: Start timer for device
                    lock(lb)
                    lb.display.show_text("Locked!")
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                    menu = 1
            elif input == '#':#Down
                menu = 3
        #Take Out Device
        elif menu == 3:
            lb.display.show_text("Take Out Device")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                device_num = validate_device(devices)
                if device_num:
                    lb.display.show_text("Door Unlocked!")
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Lock Door
                        input = lb.keypad.read_key()
                    lock(lb)
                    menu = 1
            elif input == '#':#Down
                menu = 4
        #Checkout Device
        elif menu == 4:
            lb.display.show_text("Checkout Device")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                device_num = validate_device(devices)
                if device_num:
                    #TODO: Print receipt
                    lb.display.show_text("Door Unlocked, Printing Receipt!")
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Lock Door
                        input = lb.keypad.read_key()
                    lock(lb)
                    menu = 1
            elif input == '#':#Down
                menu = 5
        #Display Points
        elif menu == 5:
            lb.display.show_text("Display Points")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                device_num = validate_device(devices)
                if device_num:
                    #TODO: Display points
                    #TODO: Display second line

                    menu = 1
            elif input == '#':#Down
                menu = 6
        #Admin Unlock
        elif menu == 6:
            lb.display.show_text("Admin Unlock")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                if validate_admin(lb):
                    unlock(lb)
                    lb.display.show_text("Unlocked!")
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Lock selected
                        input = lb.keypad.read_key()
                    lock(lb)
                else:
                    menu = 1
            elif input == '#':#Down
                menu = 7
        #Admin Display All
        elif menu == 7:
            lb.display.show_text("Admin Display All")
            #TODO: Display second line
            input = lb.keypad.read_key()
            if input == '*':#Selected
                if validate_admin(lb):
                   #TODO:Display devices and points in searchable list
                   pass
                else:
                    menu = 1
            elif input == '#':#Down
                menu = 1
            
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    menu()