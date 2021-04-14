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
