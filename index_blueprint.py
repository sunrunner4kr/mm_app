from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    current_app,
)
from threading import Timer
from flask import current_app as app
from random import randrange
import time
import csv
import os.path

index_blueprint = Blueprint("index", __name__)

counter: int = 0
life: int = 100
comms: int = 100
shields: int = 100
hydro: int = 100
interval: int = 2 # minutes
increment: int = 5 # percent


runningSystems = ["life", "comms", "shields", "hydro"]


def processTimer():
    global counter
    counter = counter + interval

    systemName = runningSystems[randrange(len(runningSystems)) - 1]
    decrementSystemsPercent(systemName, increment)

    print("another " + str(interval) + " min - " + str(systemName) + ": " + str(globals()[systemName]))



def display(msg):
    print(msg + " " + time.strftime("%H:%M:%S"))



class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            print(" ")
            processTimer()
            # How often it runs is set here
            # time.sleep(interval * 60)
            # use the above for the final scenario, using below for dev
            time.sleep(5)
            



def systemsDown():
    global life, comms, shields, hydro
    if life + comms + shields + hydro == 0:
        return True
    else:
        return False



t = RepeatTimer(1, display, ["repeating.."])
t.daemon = True



def startTimer(t):
    global counter
    counter = 0
    # t = RepeatTimer(1, display, ["repeating.."])
    # t.daemon = True
    time.sleep(15)
    t.start()
    print("starting timer")
    time.sleep(10)
    if systemsDown():
        print("finished timer")
        t.cancel



@index_blueprint.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("index.dashboard"))



@index_blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        return redirect(url_for("index.dashboard"))
    elif request.method == "GET":
        return render_template(
            "dashboard.html",
            page="dashboard",
            life=life,
            comms=comms,
            shields=shields,
            hydro=hydro,
        )



@index_blueprint.route("/config", methods=["GET", "POST"])
def config():
    global life, comms, shields, hydro
    if request.method == "POST":
        if "start" in request.form:
            readFromFile()
            startTimer(t)
        elif "stop" in request.form:
            t.cancel()

        elif "decrement" in request.form:
            decrementSystemsPercent(request.form["decrement"], increment)
        elif "increment" in request.form:
            decrementSystemsPercent(request.form["increment"], increment)
        elif "sabotage" in request.form:
            setSystemsPercent(request.form["sabotage"], 0)
        elif "restore" in request.form:
            setSystemsPercent(request.form["restore"], 100)
        return redirect(url_for("index.config"))
    elif request.method == "GET":
        time_format = time.strftime("%H:%M", time.gmtime(counter * 60))
        return render_template(
            "config.html",
            page="config",
            life=life,
            comms=comms,
            shields=shields,
            hydro=hydro,
            increment=increment,
            counter=time_format,
        )



@index_blueprint.get("/update")
def update():
    global hydro, life, comms, shields
    # total = str(hydro) + "%"  ## replace this with what you want to send

    return [str(life), str(comms), str(shields), str(hydro)]



def incrementSystemsPercent(system: str, additionPercent: int):
    newPercent = getSystemsPercent(system) + additionPercent
    if newPercent > 100:
        setSystemsPercent(system, 100)
    else:
        setSystemsPercent(system, newPercent)



def decrementSystemsPercent(system: str, decrementPercent: int):
    newPercent = getSystemsPercent(system) - decrementPercent
    if newPercent < 0:
        setSystemsPercent(system, 0)
    else:
        setSystemsPercent(system, newPercent)



def getSystemsPercent(system: str) -> int:
    if system == "life":
        return life
    elif system == "comms":
        return comms
    elif system == "shields":
        return shields
    elif system == "hydro":
        return hydro



def setSystemsPercent(system: str, newPercent: int):
    global runningSystems, life, comms, shields, hydro

    # Update the currently running systems
    if runningSystems.count(system) == 0 & newPercent == 100:
        runningSystems.append(system)
    elif runningSystems.count(system) == 1 & newPercent == 0:
        runningSystems.remove(system)

    if system == "life":
        life = newPercent
    elif system == "comms":
        comms = newPercent
    elif system == "shields":
        shields = newPercent
    elif system == "hydro":
        hydro = newPercent

    updateFile()


def updateFile():
    with open('systems.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["life", "comms", "shields", "hydro"])
        writer.writerow([life, comms, shields, hydro])



def readFromFile():
    global life, comms, shields, hydro
    if os.path.isfile('systems.csv'): 
        with open('systems.csv', 'r') as file:
            reader = csv.reader(file)
            # Header
            header = next(reader)
            # First (and only) line
            row = next(reader)
            life = int(row[0])
            comms = int(row[1])
            shields = int(row[2])
            hydro = int(row[3])
