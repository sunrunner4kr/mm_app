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

index_blueprint = Blueprint("index", __name__)

counter = 0
life = 100
comms = 100
shields = 100
hydro = 100
interval = 2 # minutes
increment = 5 # percent


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
            time.sleep(15)



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



def getSystemsPercent(system: str):
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
    if newPercent == 100:
        runningSystems.append(system)
    elif newPercent == 0:
        runningSystems.remove(system)

    if system == "life":
        life = newPercent
    elif system == "comms":
        comms = newPercent
    elif system == "shields":
        shields = newPercent
    elif system == "hydro":
        hydro = newPercent