import lockbox
import time
from flask import Flask, redirect, render_template

app = Flask(__name__, static_folder='html')

@app.route("/")
def home():
  print("Home page")
  return app.send_static_file('index.html')

@app.route("/admin")
def admin():
  print("Admin")
  return app.send_static_file('admin.html')

@app.route("/admin/<int:menu>")
def menu():
  pass
  return redirect("/admin")

@app.route("/admin/displayAll")
def displayAll():
	return app.render_template("displayAll.html", devices=devices)

@app.route("/admin/displayAll/delete/<string:item>")
def deleteDevice():
  #print("Delete " + item)
  return app.render_template("displayAll.html", devices=devices)

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
    menu = 0
    while(True):
        #Create Event
        if menu == 0:
            lb.display.clear()
            lb.display.show_text("    Welcome!", 1)
            lb.display.show_text(" * Create Event", 2)
            input = ""
            while input != "*":#Create Event
                input = lb.keypad.read_key()
            #TODO: Setup event
            menu = 1
        #Register New Device
        if menu == 1:
            lb.display.clear()
            lb.display.show_text("Register Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                lb.display.clear()
                lb.display.show_text(" Are You Sure?", 1)
                lb.display.show_text("* Yes       # No", 2)
                input = lb.keypad.read_key()
                if input == '*':#Yes
                    #TODO: Register device and print receipt
                    menu = 2
                elif input == '#':#No
                    menu == 2
            elif input == '#':#Down
                menu = 2
        #Lock Device
        elif menu == 2:
            lb.display.clear()
            lb.display.show_text("  Lock Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                device_num = validate_device(devices)
                if device_num:
                    unlock(lb)
                    lb.display.clear()
                    lb.display.show_text(" Insert Device", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = lb.keypad.read_key()
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    #TODO: Start timer for device
                    lock(lb)
                    lb.display.clear()
                    lb.display.show_text("    Locked!", 1)
                    lb.display.show_text("  * Main Menu", 2)
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                    menu = 1
            elif input == '#':#Down
                menu = 3
        #Take Out Device
        elif menu == 3:
            lb.display.clear()
            lb.display.show_text("Take Out Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                device_num = validate_device(devices)
                if device_num:
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock(lb)
                    menu = 1
            elif input == '#':#Down
                menu = 4
        #Checkout Device
        elif menu == 4:
            lb.display.clear()
            lb.display.show_text("Checkout Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                device_num = validate_device(devices)
                if device_num:
                    #TODO: Print receipt
                    lb.display.clear()
                    lb.display.show_text("Printing Receipt", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock(lb)
                    menu = 1
            elif input == '#':#Down
                menu = 5
        #Display Points
        elif menu == 5:
            lb.display.clear()
            lb.display.show_text(" Display Points", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                device_num = validate_device(devices)
                if device_num:
                    #TODO: Display points
                    #TODO: Display second line

                    menu = 1
            elif input == '#':#Down
                menu = 6
        #Admin Unlock
        elif menu == 6:
            lb.display.clear()
            lb.display.show_text("  Admin Unlock", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                if validate_admin(lb):
                    unlock(lb)
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock(lb)
                else:
                    menu = 1
            elif input == '#':#Down
                menu = 7
        #Display All
        elif menu == 7:
            lb.display.clear()
            lb.display.show_text("Display All")
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            if input == '*':#Enter
                if validate_admin(lb):
                   #TODO:Display devices and points in searchable list
                   pass
                else:
                    menu = 1
            elif input == '#':#Down
                menu = 1
            
if __name__ == "__main__":
    lb = lockbox.Lockbox()
    lb.solenoid.setup()
    lb.display.setup()
    lb.printer.setup()
    lb.keypad.setup()
    print("")

    lb.keypad.on()
    lb.display.on()

    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    menu()
