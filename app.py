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
def hello():
    return app.send_static_file('html/index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
