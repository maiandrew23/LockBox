import lockbox
import time
import sqlite3
import random
import string
import threading
from itertools import cycle
from flask import Flask, redirect, render_template, request, session

app = Flask(__name__,template_folder='templates', static_folder='static')
app.secret_key = 'some key that you will never guess'
lb = lockbox.Lockbox()


@app.route("/")
def home():
  print("Home page")
  return render_template('index.html')

#Admin login page
@app.route("/admin/login", methods = ['GET'])
def adminLogin():
    return render_template('adminLogin.html')

#Main Admin Page
@app.route("/admin")
def admin():
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  print("Admin")
  #Pass list of events to table on page
  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT * FROM session ORDER BY start_date DESC,start_time DESC''')
  events = cursor.fetchall()
  cursor.close()
  closeDB(connection)
  return render_template('admin.html',events = events)

#Admin login authentication
@app.route("/admin/auth", methods = ['POST'])
def adminAuth():
    passcode = request.form['passcode']
    query = '''SELECT * from admin WHERE passcode = ?'''
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute(query, (passcode,))
    data = cursor.fetchone()
    cursor.close()
    closeDB(connection)

    if not data:
        error = 'Incorrect Passcode!'
        return render_template('adminLogin.html', error=error)
    session['passcode'] = passcode
    return redirect('/admin')

#Sends a form to the user to fill out
@app.route("/admin/createEvent", methods = ["GET"])
def createEvent():
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  return render_template("createEvent.html")

#User inputs from edit form
@app.route("/admin/createEvent", methods = ["POST"])
def createEventPOST():
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  #Create an event. Sends user to form page where user enters Event name and date
  eventName = request.form["eventName"]
  date = request.form["date"]
  time = request.form["time"]
  sessionId = create_session(eventName,date,time,True)

  return redirect("/admin")

#Deleting an event
@app.route("/admin/deleteEvent/<sessionId>")
def deleteEvent(sessionId):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  sessionId = int(sessionId)

  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT active FROM session WHERE ID = ?''',(sessionId,))
  active = cursor.fetchone()[0]
  if active:
      cursor.close()
      closeDB(connection)
      return render_template("deleteError.html")
  cursor.execute('''DELETE FROM session WHERE ID = ?''', (sessionId,))
  cursor.execute('''DELETE FROM device WHERE session_id = ?''', (sessionId,))
  cursor.execute('''DELETE FROM score WHERE session_id = ?''', (sessionId,))
  cursor.execute('''DELETE FROM event WHERE session_id = ?''', (sessionId,))
  cursor.close()
  closeDB(connection)

  return redirect("/admin")

#Event Page
@app.route("/admin/event/<sessionId>")
def displayEvent(sessionId):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT session_id, device_number,name, points
                    FROM device NATURAL JOIN score
                    WHERE session_id = ?''', (sessionId,))
  devices = cursor.fetchall()

  cursor.execute('''SELECT name,comment FROM device NATURAL JOIN feedback WHERE session_id = ? ''', (sessionId,))
  comments = cursor.fetchall()

  cursor.close()
  closeDB(connection)
  return render_template("event.html", devices=devices, comments=comments)

@app.route("/admin/event/edit/<sessionId>", methods = ["GET"])
def rename(sessionId):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT name FROM session WHERE ID = ?''', (sessionId,))
  sessionName = cursor.fetchone()[0]

  return render_template("eventEdit.html",sessionName=sessionName,sessionId = sessionId )

@app.route("/admin/event/edit/<sessionId>", methods = ["POST"])
def renamePOST(sessionId):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  #TODO Edit session in database
  eventName = request.form["eventName"]
  date = request.form["date"]
  time = request.form["time"]

  connection = connectDB()
  cursor = connection.cursor()
  if eventName != "":
    cursor.execute('''UPDATE session SET name = ? WHERE ID = ?''', (eventName, sessionId,))
  if date != "":
    cursor.execute('''UPDATE session SET date = ? WHERE ID = ?''', (date, sessionId,))
  if time != "":
    cursor.execute('''UPDATE session SET name = ? WHERE ID = ?''', (time, sessionId,))
  cursor.close()
  closeDB(connection)
  return redirect("/admin")

@app.route("/admin/event/deleteDevice/<sessionId>/<deviceNum>")
def deleteDevice(sessionId,deviceNum):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''DELETE FROM device WHERE session_id = ? AND device_number = ?''', (sessionId,deviceNum,))
  cursor.execute('''DELETE FROM score WHERE session_id = ? AND device_number = ?''', (sessionId, deviceNum,))
  cursor.execute('''DELETE FROM event WHERE session_id = ? AND device_number = ?''', (sessionId, deviceNum,))
  cursor.close()
  closeDB(connection)
  return redirect("/admin")

@app.route("/admin/event/editDevice/<sessionId>/<deviceNum>")
def editDevice(sessionId,deviceNum):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
    #TODO
  return redirect("/admin/event/" + str(sessionId))

@app.route("/admin/event/checkout/<sessionId>/<deviceNum>")
def checkout(sessionId,deviceNum):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  sessionId = int(sessionId)
  deviceNum = int(deviceNum)
  checkout_device(sessionId, deviceNum)
  finalize_score(sessionId, deviceNum)

  return redirect("/admin/event/" + str(sessionId))

@app.route("/admin/event/devices/<int:sessionId>/<int:deviceNum>")
def guestDevice(sessionId,deviceNum):
  try:
    passcode = session['passcode'] #verify successful login
  except:
      return redirect('/admin/login')
  sessionId = int(sessionId)
  deviceNum = int(deviceNum)

  points = str(check_score(sessionId, deviceNum))

  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT action,datetime FROM event WHERE session_id = ? AND device_number = ?''', (sessionId, deviceNum,))
  actions = cursor.fetchall()

  cursor.execute('''SELECT comment FROM feedback WHERE session_id = ? AND device_number = ?''', (sessionId, deviceNum,))
  comment = cursor.fetchone()
  if comment:
    comment = comment[0]
  else:
    comment  = ""
  cursor.execute('''SELECT name,passcode FROM device where session_id = ? AND device_number = ?''', (sessionId,deviceNum))
  response = cursor.fetchone()
  passcode = response[1]
  deviceName = response[0]
  cursor.close()
  closeDB(connection)
  return render_template('deviceInfo.html',sessionId = sessionId, deviceNum = deviceNum, points = points, actions = actions, comment = comment, passcode = passcode,deviceName = deviceName)

#Guest

@app.route("/guest/login", methods = ["GET"])
def guestLogin():
  return render_template("guestLogin.html")

@app.route("/guest/login/auth", methods = ["POST"])
def guestLoginAuth():
  sessionId = int(request.form["sessionId"])
  deviceNum = int(request.form["deviceNum"])
  passcode = request.form["passcode"]

  if not validate_device_number(sessionId,deviceNum):
      error = 'Unknown Device Number!'
      return render_template("guestLogin.html", error=error)
  elif not validate_device_passcode(sessionId, deviceNum, passcode):
      error = 'Incorrect Passcode!'
      return render_template("guestLogin.html", error=error)
  #else:
  print("Successful Guest Login")
  session['sessionId'] = str(sessionId)
  session['deviceNum'] = str(deviceNum)
  return redirect("/guest/"+str(sessionId) + "/" +str(deviceNum))

@app.route("/guest/<sessionId>/<deviceNum>")
def renderGuest(sessionId,deviceNum):
  sessionId = 0
  deviceNum = 0
  try:
    sessionId = int(session['sessionId'])
    deviceNum = int(session['deviceNum'])
  except:
      return redirect('/guest/login')

  points = str(check_score(sessionId, deviceNum))

  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''SELECT action,datetime FROM event WHERE session_id = ? AND device_number = ?''', (sessionId, deviceNum,))
  actions = cursor.fetchall()

  cursor.execute('SELECT name FROM device WHERE session_id = ? AND device_number = ?', (sessionId, deviceNum))
  deviceName = cursor.fetchone()[0]
  cursor.close()
  closeDB(connection)

  return render_template("guestPage.html",sessionId = sessionId,deviceNum = deviceNum,points = points, actions=actions, deviceName=deviceName)


@app.route("/guest/edit/<sessionId>/<deviceNum>", methods = ["GET"])
def guestEditGET(sessionId,deviceNum):
  try:
    sessionId = int(session['sessionId'])
    deviceNum = int(session['deviceNum'])
  except:
      return redirect('/guest/login')
  return render_template("guestEdit.html", sessionId = sessionId, deviceNum = deviceNum)

@app.route("/guest/edit/<sessionId>/<deviceNum>", methods = ["POST"])
def guestEditPOST(sessionId,deviceNum):
  try:
    sessionId = int(session['sessionId'])
    deviceNum = int(session['deviceNum'])
  except:
      return redirect('/guest/login')

  deviceName = request.form["deviceName"]

  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''UPDATE device SET name = ? WHERE session_id = ? AND device_number = ?''', (deviceName,sessionId,deviceNum,))
  cursor.close()
  closeDB(connection)
  return redirect("/guest/" + str(sessionId) + "/" + str(deviceNum))

@app.route("/guest/comment/<sessionId>/<deviceNum>", methods = ["POST"])
def guestCommentEdit(sessionId,deviceNum):
  try:
    sessionId = int(session['sessionId'])
    deviceNum = int(session['deviceNum'])
  except:
      return redirect('/guest/login')

  comment = request.form["comment"]

  connection = connectDB()
  cursor = connection.cursor()
  cursor.execute('''INSERT OR REPLACE INTO feedback (session_id, device_number, comment)
                    VALUES (?, ?, ?)''', (sessionId, deviceNum, comment,))
  cursor.close()
  connection.commit()
  connection.close()

  return redirect("/guest/" + str(sessionId) + '/' + str(deviceNum))

@app.route("/admin/adminUnlock")
def adminUnlock():
  unlock_box(lb)
  return redirect("/admin")

@app.route("/admin/adminLock")
def adminLock():
  lock_box(lb)
  return redirect("/admin")

def drop_tables(connection):
    cursor = connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS session''')
    cursor.execute('''DROP TABLE IF EXISTS device''')
    cursor.execute('''DROP TABLE IF EXISTS event''')
    cursor.execute('''DROP TABLE IF EXISTS score''')
    cursor.execute('''DROP TABLE IF EXISTS feedback''')
    cursor.close()

def create_tables(connection):
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
                        start_time time NOT NULL,
                        end_date date,
                        end_time time,
                        active int DEFAULT 0 NOT NULL,
                        sessionOpen int DEFAULT 1 NOT NULL,
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
    cursor.close()


def lock_box(lb):
    lb.solenoid.close()


def unlock_box(lb):
    lb.solenoid.open()
    t1 = threading.Thread(target=autolock)
    t1.start()

def autolock():
    time.sleep(60)
    lb.solenoid.close()





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

# Date: YYYY-MM-DD   Time: HH:MM:SS
def create_session(name, date = "", time = "", flask = False):
    connection = connectDB()
    cursor = connection.cursor()
    #TODO: fix session name
    if flask:
        cursor.execute('''INSERT INTO session (name, start_date, start_time, active) VALUES(?,?,?,0)''', (name,date,time))
    else:
        cursor.execute('''INSERT INTO session (name, start_date,start_time, active) VALUES (?,DATE(), TIME(), 1)''', (name,))
    session_id = cursor.lastrowid
    cursor.close()
    closeDB(connection)
    return session_id

def create_device(session_id, name):
    connection = connectDB()
    cursor = connection.cursor()
    passcode = ''.join(random.choice(string.digits) for i in range(4))
    cursor.execute('''INSERT INTO device (session_id,name,passcode) VALUES (?,?,?)''', (session_id,name,str(passcode),))
    device_number = cursor.lastrowid
    cursor.execute('''INSERT INTO score (session_id, device_number,points)
                        VALUES (?,?,0)''', (session_id,device_number))
    cursor.close()
    closeDB(connection)
    return device_number, passcode

def lock_device(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Locked',DATETIME())''', (session_id, device_num,))
    cursor.close()
    closeDB(connection)

def unlock_device(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Unlocked',DATETIME())''', (session_id, device_num,))
    cursor.close()
    closeDB(connection)

def checkout_device(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO event (session_id, device_number, action, datetime)
                        VALUES (?,?,'Checked out',DATETIME())''', (session_id, device_num,))
    cursor.close()
    closeDB(connection)

def update_score(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    if points == None:
        points = 0
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_id = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    print("Current points = ", cursor.fetchone()[0])
    cursor.close()
    closeDB(connection)

def finalize_score(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    if points == None:
        points = 0
    cursor.execute('''UPDATE score SET points = points + ?
                      WHERE session_id = ? AND device_number = ?''', (points, session_id, device_num,))
    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    print("Final points = ", cursor.fetchone()[0])
    cursor.close()
    closeDB(connection)

def check_score(session_id, device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT action FROM event WHERE session_id = ? AND device_number = ? ORDER BY datetime ASC''',(session_id, device_num,))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.close()
        closeDB(connection)
        return 0
    elif data[len(data) - 1][0] != 'Locked':
        cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
        points = cursor.fetchone()[0]
        cursor.close()
        closeDB(connection)
        return int(points)

    cursor.execute('''SELECT points FROM score WHERE session_id = ? AND device_number = ?''', (session_id, device_num,))
    points = cursor.fetchone()[0]
    cursor.execute('''SELECT ROUND((JULIANDAY(DATETIME()) - JULIANDAY(t)) * 86400)
                      FROM (SELECT MAX(datetime) as t
                            FROM event
                            WHERE session_id = ? AND device_number = ? AND action = \'Locked\')''', (session_id, device_num,))
    additional_points = cursor.fetchone()[0]
    cursor.close()
    closeDB(connection)
    if additional_points:
        points += additional_points
    print("Current points: ", str(int(points)))
    return int(points)

def check_all_scores(session_id):
    connection = connectDB()
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
        #cursor.close() was here
        if result2[0]:
            all_points.append((int(row[0]), int(result2[0])))
        else:
            all_points.append((int(row[0]), 0))

    cursor.close()
    closeDB(connection)
    return all_points

def get_winner(session_id):
    connection = connectDB()
    cursor = connection.cursor()
    #TODO: will return name if needed
    cursor.execute('''SELECT device_number,MAX(points) FROM score WHERE session_id = ?''', (session_id,))
    result = cursor.fetchone()
    cursor.close()
    closeDB(connection)
    if result[0]:
        return result
    return None

def get_last_action(session_id, device_number):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute(''' SELECT action, MAX(datetime) FROM event WHERE session_id = ? AND device_number = ? ''', (session_id,device_number,))
    lastAction = cursor.fetchone()[0]
    cursor.close()
    closeDB(connection)
    return lastAction

def validate_admin_passcode(passcode):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM admin WHERE passcode = ?''', (passcode,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    closeDB(connection)
    return False

def validate_device_number(session_id,device_num):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM device WHERE session_id = ? AND device_number = ?''', (session_id,device_num,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    closeDB(connection)
    return False

def validate_device_passcode(session_id, device_num, passcode):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT *
                      FROM device
                      WHERE session_id = ? AND device_number = ? AND passcode = ?''', (session_id,device_num, passcode,))
    if cursor.fetchone():
        cursor.close()
        return True
    cursor.close()
    closeDB(connection)
    return False

def validate_admin():
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
        if validate_admin_passcode(passcode):
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

def validate_device(session_id,device_num_only=False):
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
        if validate_device_number(session_id,device_num):#Valid Device Number
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
                if validate_device_passcode(session_id, device_num, passcode):#Correct passcode
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

def print_registration(session_id, device_num, passcode):
    lb.printer.print_text("Welcome to LockBox!")
    lb.printer.print_text("")
    lb.printer.print_text("Session ID: " + str(session_id))
    lb.printer.print_text("Device Number: " + str(device_num))
    lb.printer.print_text("Passcode: " + passcode)
    lb.printer.print_text("")
    lb.printer.print_text("")
    lb.printer.print_text("Please do not lose your receipt")
    lb.printer.print_text("")
    lb.printer.print_text

def print_checkout(session_id, device_num, points, name = False):
    lb.printer.print_text("Thank you for using LockBox!")
    lb.printer.print_text("")
    lb.printer.print_text("")
    lb.printer.print_text("Session ID: " + str(session_id))
    lb.printer.print_text("Device Number: " + str(device_num))
    if name:
        lb.printer.print_text("Device Name: " + name)
    lb.printer.print_text("Points: " + str(points))
    lb.printer.print_text("\n \n \n \n")


def print_display_all(session_id):
    connection = connectDB()
    cursor = connection.cursor()
    cursor.execute('''SELECT device_number,points FROM score WHERE session_id = ?''', (session_id,))
    devices = cursor.fetchall()
    cursor.close()
    closeDB(connection)
    lb.printer.print_text("All Registered Devices")
    lb.printer.print_text("")
    lb.printer.print_text("Session # " + str(session_id))
    lb.printer.print_text("")
    lb.printer.print_text("Device #  |  Points")
    lb.printer.print_text("")
    for device in devices:
        lb.printer.print_text(str(device[0]) + "   " + str(device[1]))
    lb.printer.print_text("")
    lb.printer.print_text("")
    lb.printer.print_text("")
    lb.printer.print_text("")
    lb.printer.print_text("")

def connectDB():
    connection = sqlite3.connect("lockbox.db")
    return connection

def closeDB(connection):
    connection.commit()
    connection.close()

def menu():
    connection = connectDB()
    drop_tables(connection)
    create_tables(connection)
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM admin''')
    if cursor.fetchone() == None:
        setup_admin_passcode(connection)
    cursor.close()
    closeDB(connection)
    menu = 0
    session_id = 0
    while(True):
        #Create Session
        if menu == 0:
            lb.display.clear()
            lb.display.show_text("    Welcome!", 1)
            lb.display.show_text("* Select Events", 2)
            input = ""
            while input != "*":#Create session
                input = lb.keypad.read_key()
                time.sleep(0.2) # To prevent bounce
            menu = 10
        #Event Select Menu
        elif menu == 10:
            connection = connectDB()
            cursor = connection.cursor()
            cursor.execute('''SELECT ID,name FROM session WHERE sessionOpen = 1''')
            selections = cursor.fetchall()
            selections.insert(0,(0,"Create Event"))
            closeDB(connection)
            selected = False
            ind = 0
            while(selected == False):
                selectedName = selections[ind][1]
                lb.display.clear()
                lb.display.show_text(selectedName, 1)
                lb.display.show_text("* Start   # Down", 2)
                input = lb.keypad.read_key()
                time.sleep(0.2) # To prevent bounce
                if input == '*': #Selected Event
                    selected = True
                    if ind == 0:
                        session_id = create_session("Party")
                        selected = True
                        menu = 1
                    else:
                        session_id = selections[ind][0]
                        connection = connectDB()
                        cursor = connection.cursor()
                        cursor.execute('''UPDATE session SET active = 1 WHERE ID = ?''', (session_id,))
                        closeDB(connection)
                        menu = 1
                elif input == '#':
                    ind = (ind + 1)%(len(selections))
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
                    device_num, passcode = create_device(session_id, "N/A")
                    lb.display.clear()
                    lb.display.show_text("Device #: " + str(device_num), 1)
                    lb.display.show_text("Passcode: " + passcode, 2)
                    print_registration(session_id, device_num, passcode)
                    time.sleep(3)
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
                device_num = validate_device(session_id)
                if device_num:
                    lastAction = get_last_action(session_id, device_num)
                    if lastAction == 'Locked':
                        lb.display.clear()
                        lb.display.show_text("  Already Locked ", 1)
                        lb.display.show_text("  * Main Menu", 2)
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                        while input != "*":#Lock
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                        menu = 1
                    elif lastAction == 'Checked out':
                        lb.display.clear()
                        lb.display.show_text("  Checked Out   ", 1)
                        lb.display.show_text("  * Main Menu", 2)
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                        while input != "*":#Lock
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                        menu = 1
                    else:
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
                device_num = validate_device(session_id)
                if device_num:
                    lastAction = get_last_action(session_id,device_num)
                    if lastAction == 'Unlocked':
                        lb.display.clear()
                        lb.display.show_text("Already Unlocked", 1)
                        lb.display.show_text("  * Main Menu", 2)
                        input = ""
                        while input != "*":#Back to Main Menu
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                        menu = 1

                    elif lastAction == 'Checked out':
                        lb.display.clear()
                        lb.display.show_text("  Checked Out   ", 1)
                        lb.display.show_text("  * Main Menu", 2)
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                        while input != "*":#Lock
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                        menu = 1
                    else:
                        #Unlock device and update score
                        unlock_device(session_id, device_num)
                        unlock_box(lb)
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
                device_num = validate_device(session_id)
                if device_num:
                    if lastAction == 'Checked out':
                        lb.display.clear()
                        lb.display.show_text("  Checked Out   ", 1)
                        lb.display.show_text("  * Main Menu", 2)
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                        while input != "*":#Lock
                            input = lb.keypad.read_key()
                            time.sleep(0.2) # To prevent bounce
                        menu = 1
                    else:
                        #Checkout device and finalize score
                        checkout_device(session_id, device_num)
                        finalize_score(session_id, device_num)

                        connection = connectDB()
                        cursor = connection.cursor()
                        cursor.execute('''SELECT points from score WHERE session_id = ? AND device_number = ?''', (session_id, device_num))
                        points = cursor.fetchone()[0]
                        cursor.close()
                        closeDB(connection)
                        print_checkout(str(session_id), str(device_num), str(points))
                        unlock_box(lb)
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
                device_num = validate_device(session_id,device_num_only=True)
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
            lb.display.show_text("Display All Pnts", 1)
            lb.display.show_text("* Enter   # Down", 2)
            input = lb.keypad.read_key()
            time.sleep(0.2) # To prevent bounce
            if input == '*':#Enter
                rows = check_all_scores(session_id)
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
                if validate_admin():
                    connection = connectDB()
                    cursor = connection.cursor()
                    cursor.execute('''SELECT device_number FROM device WHERE session_id = ?''', (session_id,))
                    data = cursor.fetchall()
                    cursor.close()
                    closeDB(connection)
                    for row in data:
                        if get_last_action(session_id,row[0]) != 'Checked out':
                            checkout_device(session_id,row[0])
                            finalize_score(session_id,row[0])
                    row = get_winner(session_id)
                    print_display_all(session_id)
                    lb.display.clear()
                    if row:
                        lb.display.show_text("*D#: " + str(row[0]) + " Pts: " + str(row[1]), 1)
                    lb.display.show_text("  * Main Menu", 2)
                    input = ""
                    while input != "*":#Back to Main Menu
                        input = lb.keypad.read_key()
                        time.sleep(0.2) # To prevent bounce
                    menu = 0

                    connection = connectDB()
                    cursor = connection.cursor()
                    cursor.execute('''UPDATE session SET active = ? WHERE ID = ?''', (0, session_id,))
                    cursor.execute('''UPDATE session SET sessionOPEN = ? WHERE ID = ?''', (0, session_id,))
                    cursor.close()
                    closeDB(connection)
                    menu = 0
                else:#Back to Main Menu
                    menu = 1
            elif input == '#':#Down
                menu = 1



def run_flask():
    app.run(host='0.0.0.0', port=80, debug= False, threaded=True)

if __name__ == "__main__":
    lb.solenoid.setup()
    lb.display.setup()
    lb.printer.setup()
    lb.keypad.setup()
    print("")

    lb.keypad.on()
    lb.display.on()

    t1 = threading.Thread(target=menu)
    t2 = threading.Thread(target=run_flask)
    t1.start()
    t2.start()

    t1.join()
    t2.join()
