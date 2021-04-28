import lockbox
import time
import sqlite3
import random
import string
from flask import Flask, redirect, render_template

connection = sqlite3.connect("lockbox.db")
cursor = connection.cursor()

def clear_database():
    cursor.execute('''DROP TABLE session IF EXISTS''')
    cursor.execute('''DROP TABLE device IF EXISTS''')
    cursor.execute('''DROP TABLE event IF EXISTS''')
    cursor.execute('''DROP TABLE score IF EXISTS''')
    cursor.execute('''DROP TABLE feedback IF EXISTS''')

clear_database()

# Create admin table
cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                    passcode varchar(255) NOT NULL,
                    PRIMARY KEY (passcode)
                  )''')

#Default passcode for debugging
cursor.execute('''INSERT INTO admin (passcode) VALUES (1234)''')

# Create session table
cursor.execute('''CREATE TABLE IF NOT EXISTS session (
                    ID integer,
                    name varchar(255) NOT NULL,
                    start_date date NOT NULL,
                    start_time time NOT NULL,
                    end_date date,
                    end_time time,
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
                    event_id integer,
                    session_ID integer,
                    device_number integer,
                    action varchar(255) NOT NULL,
                    datetime datetime NOT NULL,
                    PRIMARY KEY (event_id)
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

def lock_box(lb):
    lb.solenoid.close()

def unlock_box(lb):
    lb.solenoid.open()

def create_session(name):
    #TODO: fix session name
    cursor.execute('''INSERT INTO session (name, start_date,start_time) VALUES (?,DATE(), TIME())''', (name,))
    return cursor.lastrowid

def create_device(session_id, name):
    passcode = ''.join(random.choice(string.digits) for i in range(4))
    cursor.execute('''INSERT INTO device (name,passcode) VALUES (?,?)''', (name,str(passcode),))
    device_number = cursor.lastrowid
    print("Device # = ", device_number)
    print("Passcode = ", passcode)
    cursor.execute('''INSERT INTO score (session_ID, device_number,points)
                        VALUES (?,?,0)''', (session_id,device_number))
    return device_number, passcode

def lock_device(session_id, device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number, action, datetime) 
                        VALUES (?,?,'Locked',DATETIME())''', (session_id, device_num,))

def unlock_device(session_id, device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number, action, datetime) 
                        VALUES (?,?,'Unlocked',DATETIME())''', (session_id, device_num,))

def checkout_device(session_id, device_num):
    cursor.execute('''INSERT INTO event (session_ID, device_number, action, datetime) 
                        VALUES (?,?,'Checked out',DATETIME())''', (session_id, device_num,))

def update_score(session_id, device_num):
    #TODO: make points addition be based on time between last lock and unlock
    points = 10
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_ID = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_ID = ? AND device_number = ?''', (session_id, device_num,))
    print("Current points = ", cursor.fetchone()[0])

def finalize_score(session_id, device_num):
    #TODO: make points addition be based on time between last lock and checkout
    points = 10
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_ID = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_ID = ? AND device_number = ?''', (session_id, device_num,))
    print("Final points = ", cursor.fetchone()[0])

def check_score(session_id, device_num):
    #TODO: Add points earned up until the current time
    cursor.execute('''SELECT points FROM score WHERE session_ID = ? AND device_number = ?''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    print("Current points: ", str(points))
    return points

def validate_admin_passcode(passcode):
    cursor.execute('''SELECT * FROM admin WHERE passcode = ?''', (passcode,))
    if cursor.fetchone():
        return True
    return False

def validate_device_number(device_num):
    pass

def validate_device_passcode(device_num, passcode):
    cursor.execute('''SELECT * FROM device WHERE deivice_number = ? AND passcode = ?''', (device_num, passcode,))
    if cursor.fetchone():
        return True
    return False

def validate_admin():
    lb.display.clear()
    lb.display.show_text("Enter Passcode", 1)
    lb.display.show_text("     * Done", 2)
    passcode = ""
    input = lb.keypad.read_key()
    time.sleep(0.2) # To prevent bounce
    while input != "*":
        passcode = passcode + input
        input = lb.keypad.read_key()
        time.sleep(0.2) # To prevent bounce
    if validate_admin_passcode(passcode):
        return True
    else:
        lb.display.clear()
        lb.display.show_text("Wrong Passcode!", 1)
        lb.display.show_text("*Try Again #Back", 2)
        input = lb.keypad.read_key()
        time.sleep(0.2) # To prevent bounce
        if input == "*":#Try Again selected
            pass
        elif input == "#":#Back to Main Menu
            return False
    return False

def validate_device():
    lb.display.clear()
    lb.display.show_text("Enter Device #", 1)
    lb.display.show_text("     * Done", 2)
    device_num = ""
    input = lb.keypad.read_key()
    time.sleep(0.2) # To prevent bounce
    while input != "*":
        device_num = device_num + input
        input = lb.keypad.read_key()
        time.sleep(0.2) # To prevent bounce
    if validate_device_number(device_num):#Valid Device Number
        count = 0
        while count < 2:
            lb.display.clear()
            lb.display.show_text("Enter Passcode", 1)
            lb.display.show_text("     * Done", 2)
            passcode = ""
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            while input != "*":
                passcode = passcode + input
                input = lb.keypad.read_key()
                time.sleep(0.2) # To prevent bounce
            if validate_device_passcode(device_num, passcode):#Correct passcode
               return device_num
            else:#Incorrect passcode
                lb.display.clear()
                lb.display.show_text("Wrong Passcode", 1)
                lb.display.show_text("*Try Again #Back", 2)
                if count == 0:
                    #TODO: Display second line
                    input = lb.keypad.read_key()
                    time.sleep(0.2) # To prevent bounce
                    if input == "*":#Try Again selected
                        count += 1
                    elif input == "#":#Back to Main Menu
                        return None
                else:
                    #TODO: Display second line
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    return None
    else:
        lb.display.clear()
        lb.display.show_text("Device Not Found",1)
        lb.display.show_text("  * Main Menu", 2)
        input = ""
        while input != "*":#Back to Main Menu
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce

def menu():
    menu = 0
    session_id = 0
    while(True):
        #Create Session
        if menu == 0:
            lb.display.clear()
            lb.display.show_text("    Welcome!", 1)
            lb.display.show_text("* Create Session", 2)
            input = ""
            while input != "*":#Create session
                input = lb.keypad.read_key()
                time.sleep(0.2) # To prevent bounce
            #TODO: Setup session
            session_id = create_session("Party")
            menu = 1
        #Register New Device
        if menu == 1:
            lb.display.clear()
            lb.display.show_text("Register Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                lb.display.clear()
                lb.display.show_text(" Are You Sure?", 1)
                lb.display.show_text("* Yes       # No", 2)
                input = lb.keypad.read_key()
                time.sleep(0.2) # To prevent bounce
                if input == '*':#Yes
                    #TODO: Print receipt
                    device_num, passcode = create_device(session_id, "N/A")
                    lb.display.clear()
                    lb.display.show_text("Device #: " + str(device_num), 1)
                    lb.display.show_text("Passcode: " + passcode, 2)
                    time.sleep(5)
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
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                device_num = validate_device()
                if device_num:
                    unlock_box(lb)
                    lb.display.clear()
                    lb.display.show_text(" Insert Device", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = lb.keypad.read_key()
                    time.sleep(0.2) # To prevent bounce
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    lock_device(session_id, device_num)
                    lock_box(lb)
                    lb.display.clear()
                    lb.display.show_text("    Locked!", 1)
                    lb.display.show_text("  * Main Menu", 2)
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    menu = 1
            elif input == '#':#Down
                menu = 3
        #Take Out Device
        elif menu == 3:
            lb.display.clear()
            lb.display.show_text("Take Out Device", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                device_num = validate_device()
                if device_num:
                    #Unlock device and update score
                    unlock_device(session_id, device_num)
                    update_score(session_id, device_num)
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
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
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                device_num = validate_device()
                if device_num:
                    #Checkout device and finalize score
                    checkout_device(session_id, device_num)
                    finalize_score(session_id, device_num)
                    #TODO: Print receipt
                    lb.display.clear()
                    lb.display.show_text("Printing Receipt", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
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
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter  
                device_num = validate_device()
                if device_num:
                    points = check_score(session_id, device_num)
                    lb.display.clear()
                    lb.display.show_text("Points: " + str(points), 1)
                    lb.display.show_text("  * Main Menu", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    menu = 1
            elif input == '#':#Down
                menu = 6
        #Admin Unlock
        elif menu == 6:
            lb.display.clear()
            lb.display.show_text("  Admin Unlock", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                if validate_admin():
                    unlock_box(lb)
                    lb.display.clear()
                    lb.display.show_text("   Unlocked!", 1)
                    lb.display.show_text("    * Lock    ", 2)
                    input = ""
                    while input != "*":#Lock
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
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
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                if validate_admin():
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

    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    menu()
