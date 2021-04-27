import lockbox
import time
import sqlite3
import random
import string
from flask import Flask, redirect, render_template

connection = sqlite3.connect("lockbox.db")
cursor = connection.cursor()

# Create admin table
cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                    passcode varchar(255) NOT NULL,
                    PRIMARY KEY (passcode)
                  )''')

# Create session table
cursor.execute('''CREATE TABLE IF NOT EXISTS session (
                    ID integer,
                    name varchar(255) NOT NULL,
                    start_date date NOT NULL,
                    start_time time (0) NOT NULL,
                    end_date date NOT NULL,
                    end_time time (0) NOT NULL,
                    PRIMARY KEY (ID)
                  )''')

# Create device table
cursor.execute('''CREATE TABLE IF NOT EXISTS device (
                    device_number integer,
                    name varchar(255) NOT NULL,
                    passcode varchar(255) NOT NULL,
                    PRIMARY KEY (device_number)
                  )''')

# Create event table
cursor.execute('''CREATE TABLE IF NOT EXISTS event (
                    session_ID integer,
                    device_number integer,
                    action varchar(255) NOT NULL,
                    datetime datetime NOT NULL,
                    PRIMARY KEY (session_ID, device_number)
                  )''')

# Create score table
cursor.execute('''CREATE TABLE IF NOT EXISTS score (
                    session_ID integer,
                    device_number integer,
                    points integer NOT NULL,
                    PRIMARY KEY (session_ID, device_number)
                  )''')

# Create feedback table
cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    session_ID integer,
                    device_number integer,
                    comment varchar(255) NOT NULL,
                    PRIMARY KEY (session_ID, device_number)
                  )''')

def clear_database():
    cursor.execute('''DROP TABLE session''')
    cursor.execute('''DROP TABLE device''')
    cursor.execute('''DROP TABLE event''')
    cursor.execute('''DROP TABLE score''')
    cursor.execute('''DROP TABLE feedback''')

app = Flask(__name__, static_folder='html')

@app.route("/")
def home():
  print("Home page")
  return app.send_static_file('index.html')

#Admin Pages
@app.route("/admin")
def admin():
  print("Admin")
  #Pass list of events to table on page
  return app.render_template("admin.html", events = events)

@app.route("/createEvent")
def createEvent():
  #Create an event. Sends user to form page where user enters Event name and date
  return app.send_static_file("create.html")

@app.route("/createEventPOST")
def createEventPOST():
  #Create an event. Sends user to form page where user enters Event name and date
  return app.render_template("admin.html", events = events)

@app.route("/deleteEvent/<string:eventName>")
def deleteEvent():
  #Delete Event name
  return app.render_template("admin.html", events = events)

#Event Pages
@app.route("/event/<string:eventName>")
def displayEvent():
  print("Event")
  #query eventName
  #search for eventName and render event.html with event info
  #Send list of registered devices under events
  return app.render_template("event.html", eventName = eventName)

@app.route("/event/rename/<string:eventName>")
def rename():
  print("Rename " + eventName)
  #Send form for user to enter new name
  return app.send_static_file("rename.html")
  
@app.route("/event/renamePOST/<string:eventName>")
def renamePOST():
  print("Rename " + eventName)
  return app.render_template("event.html", eventName = eventName)

@app.route("/event/deleteDevice/<string:eventName>/<string:deviceName>")
def deleteDevice():
  deleteDevice("Delete " + deviceName)
  return app.render_template("event.html", eventName = eventName)

@app.route("/event/lockDevice/<string:eventName>/<string:deviceName>")
def lock():
  print("Lock " + deviceName)
  #Close solenoid, log device
  return app.render_template("event.html", eventName = eventName)

@app.route("/event/unlockDevice/<string:eventName>/<string:deviceName>")
def unlock():
  print("Unlock " + deviceName)
  #Open solenoid, log device
  #Set saftey timer
  return app.render_template("event.html", eventName = eventName)

@app.route("/event/checkout/<string:eventName>/<string:deviceName>")
def checkout():
  print("Checkout " + deviceName)

  return app.render_template("event.html", eventName = eventName)

#Device Pages
@app.route("/event/device/<string:eventName>/<string:deviceName>")
def guestDevice():
  print("GET"+deviceName)
  #query deviceName and get device log info, render in device.html
  return app.render_template('device.html', deviceName = deviceName)

#Guest
@app.route("/guest/login")
def guestLogin():
  print("guest")
  #Pass list of events to table on page
  return app.send_static_file("guestlogin.html")

@app.route("/guest/loginPOST")
def guestLoginPOST():
  #gathers POST data and query deviceName
  return app.render_template('guestDevice.html', deviceName = deviceName)



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

def lock_box(lb):
    lb.solenoid.close()

def unlock_box(lb):
    lb.solenoid.open()

def create_session(name):
    #TODO: fix session name
    cursor.execute('''INSERT INTO session (%s, start_date,start_time) VALUES (Party,CURDATE(), CURTIME())''', (name))

def create_device():
    passcode = ''.join(random.choice(string.digits) for i in range(4))
    cursor.execute('''INSERT INTO device (passcode) VALUES (%s)''', (passcode))
    cursor.execute('''INSERT INTO score (session_ID, device_number,points)
                        VALUES ((SELECT LAST_INSERT_ID() FROM session),(SELECT LAST_INSERT_ID() FROM device),0)''')

def lock_device(device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number,action, datetime) 
                        VALUES ((SELECT LAST_INSERT_ID() FROM session),%s,'Locked',CURDATETIME())''', (device_num))

def unlock_device(device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number,action, datetime) 
                        VALUES ((SELECT LAST_INSERT_ID() FROM session),%s,'Unlocked',CURDATETIME())''', (device_num))

def checkout_device(device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number,action, datetime) 
                        VALUES ((SELECT LAST_INSERT_ID() FROM session),%s,'Checked out',CURDATETIME())''', (device_num))

def update_score(device_num):
    #TODO: make points addition be based on time between last lock and unlock
    points = 10
    cursor.execute('''UPDATE score SET points = points + %s
                      WHERE session_ID = (SELECT LAST_INSERT_ID() FROM session) AND device_number = %s)''', (points), (device_num))

def finalize_score(device_num):
    #TODO: make points addition be based on time between last lock and checkout
    points = 10
    cursor.execute('''UPDATE score SET points = points + %s
                      WHERE session_ID = (SELECT LAST_INSERT_ID() FROM session) AND device_number = %s)''', (points), (device_num))

def menu():
    menu = 0
    while(True):
        #Create Event
        if menu == 0:
            lb.display.clear()
            lb.display.show_text("    Welcome!", 1)
            lb.display.show_text(" * Create Session", 2)
            input = ""
            while input != "*":#Create session
                input = lb.keypad.read_key()
            #TODO: Setup session
            create_session(cursor, "Party")
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
                    #TODO: Print receipt
                    create_device()
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
                    unlock_box(lb)
                    lb.display.clear()
                    lb.display.show_text(" Insert Device", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = lb.keypad.read_key()
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock_device(device_num)
                    lock_box(lb)
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
                    #Unlock device and update score
                    unlock_device(device_num)
                    update_score(device_num)
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock_box(lb)
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
                    #Checkout device and finalize score
                    checkout_device(device_num)
                    finalize_score(device_num)
                    #TODO: Print receipt
                    lb.display.clear()
                    lb.display.show_text("Printing Receipt", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock_box(lb)
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
                    unlock_box(lb)
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                    lock_box(lb)
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
