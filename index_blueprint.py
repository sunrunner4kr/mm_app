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


system = ["life", "comms", "shields", "hydro"]


def incrementDown():
    global counter, life, comms, shields, hydro
    counter = counter + 15
    # print(randrange(4))

    systemVal = 0
    while systemVal == 0:
        systemName = system[randrange(4)]
        # print(systemName)
        # print(globals()[systemName])
        systemVal = globals()[systemName]

    if systemVal < 15:
        globals()[systemName] = 0
    else:
        globals()[systemName] = globals()[systemName] - 15
    print("another 15min - " + str(systemName) + ": " + str(globals()[systemName]))


def display(msg):
    print(msg + " " + time.strftime("%H:%M:%S"))


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            print(" ")
            incrementDown()
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
            if request.form["decrement"] == "life":
                if life > 14:
                    life = life - 15
            elif request.form["decrement"] == "comms":
                if comms > 14:
                    comms = comms - 15
            elif request.form["decrement"] == "shields":
                if shields > 14:
                    shields = shields - 15
            elif request.form["decrement"] == "hydro":
                if hydro > 14:
                    hydro = hydro - 15
        elif "increment" in request.form:
            if request.form["increment"] == "life":
                if life < 86:
                    life = life + 15
            elif request.form["increment"] == "comms":
                if comms < 86:
                    comms = comms + 15
            elif request.form["increment"] == "shields":
                if shields < 86:
                    shields = shields + 15
            elif request.form["increment"] == "hydro":
                if hydro < 86:
                    hydro = hydro + 15
        elif "sabotage" in request.form:
            if request.form["sabotage"] == "life":
                life = 0
            elif request.form["sabotage"] == "comms":
                comms = 0
            elif request.form["sabotage"] == "shields":
                shields = 0
            elif request.form["sabotage"] == "hydro":
                hydro = 0
        elif "restore" in request.form:
            if request.form["restore"] == "life":
                life = 100
            elif request.form["restore"] == "comms":
                comms = 100
            elif request.form["restore"] == "shields":
                shields = 100
            elif request.form["restore"] == "hydro":
                hydro = 100
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
