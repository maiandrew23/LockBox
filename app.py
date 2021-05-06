import lockbox
import time
import sqlite3
import random
import string
import threading
from itertools import cycle
from flask import Flask, redirect, render_template, request


app = Flask(__name__, static_folder='templates')

@app.route("/")
def home():
  print("Home page")
  return app.send_static_file('index.html')

#Admin Pages
@app.route("/admin")
def admin():
  print("Admin")
  #Pass list of events to table on page
  return render_template('admin.html',eventName='Event1', sessionId = 1)

@app.route("/admin/createEvent", methods = ["GET"])
def createEvent():
  #Sends a form to the user to fill out
  return app.send_static_file("createEvent.html")

@app.route("/admin/createEvent", methods = ["POST"])
def createEventPOST():
  #Create an event. Sends user to form page where user enters Event name and date
  eventName = request.form["eventName"]
  date = request.form["date"]
  time = request.form["time"]
  return reidrect("/admin")

@app.route("/admin/deleteEvent/<int:sessionId>")
def deleteEvent():
  #Delete Event name
  #print("delete " + eventName)
  return render_template("admin.html", sessionId = 1, eventName = "deleted")

#Event Pages
@app.route("/admin/event/<int:sessionId>")
def displayEvent():
  #print("View event " + eventName)
  #query eventName
  #search for eventName and render event.html with event info
  #Send list of registered devices under events
  return render_template("event.html", name = "test", device = "device1")

@app.route("/admin/event/edit/<int:sessionId>", methods = ["GET"])
def rename():
  #print("Rename " + eventName)
  #Send form for user to enter new name
  return render_template("eventEdit.html",eventName )

@app.route("/admin/event/edit/<int:sessionId>", methods = ["POST"])
def renamePOST():
  #print("Rename " + eventName)
  return render_template("event.html",name = "test")

@app.route("/admin/deleteDevice/<int:sessionId>/<int:deviceNum>")
def deleteDevice():
  deleteDevice("Delete " + deviceName)
  return render_template("event.html",name = "test")

@app.route("/admin/lockDevice/<int:sessionId>/<int:deviceNum>")
def lock():
  #print("Lock " + deviceName)
  #Close solenoid, log device
  return render_template("event.html")

@app.route("/admin/unlockDevice/<int:sessionId>/<int:deviceNum>")
def unlock():
  print("Unlock " + deviceName)
  #Open solenoid, log device
  #Set saftey timer
  return render_template("event.html", eventName = eventName)

@app.route("/event/checkout/<int:sessionId>/<int:deviceNum>")
def checkout():
  #print("Checkout " + deviceName)

  return render_template("event.html", eventName = eventName)

#Device Pages
@app.route("/event/device/<int:sessionId>/<int:deviceNum>")
def guestDevice():
  #print("GET"+deviceName)
  #query deviceName and get device log info, render in device.html
  return render_template('deviceInfo.html', deviceName = deviceName)

#Guest
@app.route("/guest/login", methods = ["GET"])
def guestLoginGET():
  #print("guest")
  #Pass list of events to table on page
  return app.send_static_file("guestlogin.html")

@app.route("/guest/login", methods = ["POST"])
def guestLoginPOST():
  sessionId = request.form(["sessionId"])
  device = request.form(["device"])
  passcode = request.form(["passcode"])
  return render_template("guestpage.html")


@app.route("/guest/edit/<string:deviceName>", methods = ["GET"])
def guestEditGET():
  return render_template("guestEdit.html",deviceName = deviceName )

@app.route("/guest/edit/<string:name>", methods = ["POST"])
def guestEditPOST():
  deviceName = request.form["deviceName"]
  return app.render_template("guestPage.html")

@app.route("/guest/comment/<string:name>", methods = ["POST"])
def guestCommentEdit():
  comment = request.form["comment"]
  return app.render_template("guestPage.html")

@app.route("/admin/adminUnlock")
def adminUnlock():
  return

@app.route("/admin/adminLock")
def adminLock():
  return

def drop_tables(cursor):
    cursor.execute('''DROP TABLE IF EXISTS session''')
    cursor.execute('''DROP TABLE IF EXISTS device''')
    cursor.execute('''DROP TABLE IF EXISTS event''')
    cursor.execute('''DROP TABLE IF EXISTS score''')
    cursor.execute('''DROP TABLE IF EXISTS feedback''')

def create_tables(cursor):
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
                        start_time time NOT NULL,
                        end_date date,
                        end_time time,
                        PRIMARY KEY (ID)
                    )''')

    # Create device table
    cursor.execute('''CREATE TABLE IF NOT EXISTS device (
                        session_id integer,
                        device_number integer,
                        name varchar(255) NOT NULL,
                        passcode varchar(255) NOT NULL,
                        PRIMARY KEY (device_number),
                        UNIQUE (session_id,device_number)
                    )''')

    # Create event table
    cursor.execute('''CREATE TABLE IF NOT EXISTS event (
                        event_id integer,
                        session_id integer,
                        device_number integer,
                        action varchar(255) NOT NULL,
                        datetime datetime NOT NULL,
                        PRIMARY KEY (event_id)
                    )''')

    # Create score table
    cursor.execute('''CREATE TABLE IF NOT EXISTS score (
                        session_id integer,
                        device_number integer,
                        points integer NOT NULL,
                        PRIMARY KEY (session_id, device_number)
                    )''')

    # Create feedback table
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        session_id integer,
                        device_number integer,
                        comment varchar(255) NOT NULL,
                        PRIMARY KEY (session_id, device_number)
                    )''')


def lock_box(lb):
    lb.solenoid.close()

def lock_safety():
    time.sleep(10)
    lb.solenoid.close()

def unlock_box(lb):
    lb.solenoid.open()
    #lock_safety()    #run this in a thread




def create_admin_passcode(connection, passcode):
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM admin WHERE passcode = ?''', (passcode,))
    if cursor.fetchone() == None:
        cursor.execute('''INSERT INTO admin (passcode) VALUES (?)''', (passcode,))
        connection.commit()

def setup_admin_passcode(connection):
    lb.display.clear()
    lb.display.show_text("Admin Passcode", 1)
    lb.display.show_text("     * Done", 2)
    passcode = ""
    input = lb.keypad.read_key()
    time.sleep(0.2) # To prevent bounce
    while input != "*":
        passcode = passcode + input
        input = lb.keypad.read_key()
        time.sleep(0.2) # To prevent bounce
    create_admin_passcode(connection, passcode)

def create_session(connection, name):
    cursor = connection.cursor()
    #TODO: fix session name
    cursor.execute('''INSERT INTO session (name, start_date,start_time) VALUES (?,DATE(), TIME())''', (name,))
    session_id = cursor.lastrowid
    cursor.close()
    return session_id

def create_device(connection, session_id, name):
    cursor = connection.cursor()
    passcode = ''.join(random.choice(string.digits) for i in range(4))
    cursor.execute('''INSERT INTO device (session_id,name,passcode) VALUES (?,?,?)''', (session_id,name,str(passcode),))
    device_number = cursor.lastrowid
    print("Device # = ", device_number)
    print("Passcode = ", passcode)
    cursor.execute('''INSERT INTO score (session_id, device_number,points)
                        VALUES (?,?,0)''', (session_id,device_number))
    cursor.close()
    return device_number, passcode

def lock_device(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Locked',DATETIME())''', (session_id, device_num,))

def unlock_device(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Unlocked',DATETIME())''', (session_id, device_num,))
    cursor.close()

def checkout_device(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Checked out',DATETIME())''', (session_id, device_num,))
    cursor.close()

def update_score(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_id = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    print("Current points = ", cursor.fetchone()[0])
    cursor.close()

def finalize_score(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_id = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    print("Final points = ", cursor.fetchone()[0])
    cursor.close()

def check_score(connection, session_id, device_num):
    cursor = connection.cursor()
    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    additional_points = cursor.fetchone()[0]
    cursor.close()
    if additional_points:
        points += additional_points
    print("Current points: ", str(int(points)))
    return int(points)

def check_all_scores(connection,session_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT device_number,points FROM score WHERE session_id = ?''', (session_id,))
    result1 = cursor.fetchall()
    all_points = []
    for row in result1:
        cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                        FROM (SELECT MAX(datetime) as t
                                FROM event
                                WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, row[0],))
        result2 = cursor.fetchone()
        cursor.close()
        if result2[0]:
            all_points.append((int(row[0]), int(result2[0])))
        else:
            all_points.append((int(row[0]), 0))
    return all_points

def get_winner(connection, session_id):
    cursor = connection.cursor()
    #TODO: will return name if needed
    cursor.execute('''SELECT device_number,MAX(points) FROM score WHERE session_id = ?''', (session_id,))
    result = cursor.fetchone()
    cursor.close()
    print("Result: ", result)
    if result[0]:
        return result
    return None

def validate_admin_passcode(connection, passcode):
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM admin WHERE passcode = ?''', (passcode,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    return False

def validate_device_number(connection, session_id,device_num):
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM device WHERE session_id = ? AND device_number = ?''', (session_id,device_num,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    return False

def validate_device_passcode(connection, session_id, device_num, passcode):
    cursor = connection.cursor()
    cursor.execute('''SELECT *
                      FROM device
                      WHERE session_id = ? AND device_number = ? AND passcode = ?''', (session_id,device_num, passcode,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    return False

def validate_admin(connection):
    while True:
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
        if validate_admin_passcode(connection, passcode):
            return True
        else:
            lb.display.clear()
            lb.display.show_text("Wrong Passcode!", 1)
            lb.display.show_text("*Try Again #Back", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == "*":#Try Again selected
                continue
            elif input == "#":#Back to Main Menu
                return False
        return False

def validate_device(connection, session_id,device_num_only=False):
    while True:
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
        if validate_device_number(connection,session_id,device_num):#Valid Device Number
            if device_num_only:
                return device_num
            while True:
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
                if validate_device_passcode(connection,session_id, device_num, passcode):#Correct passcode
                    return device_num
                else:#Incorrect passcode
                    lb.display.clear()
                    lb.display.show_text("Wrong Passcode", 1)
                    lb.display.show_text("*Try Again #Back", 2)
                    input = lb.keypad.read_key()
                    time.sleep(0.2) # To prevent bounce
                    if input == "*":#Try Again selected
                        continue
                    elif input == "#":#Back to Main Menu
                        return None
        else:
            lb.display.clear()
            lb.display.show_text("Device Not Found",1)
            lb.display.show_text("*Try Again #Back", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == "*":#Try Again selected
                continue
            elif input == "#":#Back to Main Menu
                return None

def menu():
    connection = sqlite3.connect("lockbox.db")
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM admin''')
    if cursor.fetchone() == None:
        setup_admin_passcode(connection)
    cursor.close()

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
            session_id = create_session(connection, "Party")
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
                    device_num, passcode = create_device(connection,session_id, "N/A")
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
                device_num = validate_device(connection, session_id)
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
                    lock_device(connection, session_id, device_num)
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
                device_num = validate_device(connection, session_id)
                if device_num:
                    #Unlock device and update score
                    unlock_device(connection, session_id, device_num)
                    update_score(connection, session_id, device_num)
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
                device_num = validate_device(connection, session_id)
                if device_num:
                    #Checkout device and finalize score
                    checkout_device(connection, session_id, device_num)
                    finalize_score(connection, session_id, device_num)
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
                device_num = validate_device(connection, session_id,device_num_only=True)
                if device_num:
                    points = check_score(connection, session_id, device_num)
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
                if validate_admin(connection):
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
            lb.display.show_text("Display All Pnts", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                rows = check_all_scores(connection, session_id)
                row_cycle = cycle(rows)
                lb.display.clear()
                lb.display.show_text("  *Next  #Back  ", 2)
                while input == "*":
                    if len(rows) != 0:
                        row = next(row_cycle)
                        lb.display.show_text("D#: " + str(row[0]) + " Pts: " + str(row[1]), 1)
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                        if input == "#":#Back to Main Menu
                            menu = 1
                    else:
                        while input != "#":
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                            if input == "#":#Back to Main Menu
                                menu = 1
            elif input == '#':#Down
                menu = 8
        elif menu == 8:# End Session
            lb.display.clear()
            lb.display.show_text("  End Session", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                if validate_admin(connection):
                    #TODO: Print cumulative receipt
                    row = get_winner(connection, session_id)
                    connection.commit()
                    lb.display.clear()
                    if row:
                        lb.display.show_text("*D#: " + str(row[0]) + " Pts: " + str(row[1]), 1)
                    lb.display.show_text("  * Main Menu", 2)
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    menu = 0
                else:#Back to Main Menu
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
    x = threading.Thread(target=menu)
    x.start()
    x.join()
