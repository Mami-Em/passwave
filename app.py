import os
from types import MethodDescriptorType
import psycopg2

from flask import Flask, render_template, redirect, request, session
from werkzeug.utils import redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registering", methods = ["POST"])
def registering():
    name = request.form.get("name")
    password = request.form.get("password")
    db.execute(f"INSERT INTO human (name, password) VALUES ('{name}', '{password}')")
    db.commit()
    return redirect("login")

@app.route("/login")
def login():
    return render_template("login.html")

# ========================================================================
@app.route("/login_process_", methods = ["POST"])
def login_process_():
    name = request.form.get("name")
    user = db.execute(f"SELECT * FROM human WHERE name = '{name}'").fetchall()
    if user:
        return render_template("passcheck.html", user = user)
    else:
        return render_template("error.html", message = "No such user!")
# ========================================================================
# to update
@app.route("/loin_process__", methods = ["POST"])
def login_process__():
    password = request.form.get("password")
    user = db.execute(f"SELECT * FROM human WHERE password = '{password}'").fetchall()
    for u in user:
        session["name"] = u.name
        return redirect(f"/homepage/{u.name}")
# =========================================================================

@app.route("/homepage/<string:name>")
def homepage(name):
    if not session.get("name"):
        return redirect("/")
    user = db.execute(f"SELECT * FROM human WHERE name = '{name}'").fetchall()
    return render_template("home.html", user = user)

@app.route("/insert_data0", methods = ["POST"])
def insert_data():
    if not session.get("name"):
        return redirect("/")
    appName = request.form.get("appName")
    nameUsed = request.form.get("nameUsed")
    passwordUsed = request.form.get("passwordUsed")
    id = request.form.get("id")
    db.execute(f"INSERT INTO databae (user_id, appName, nameUsed, passwordUsed) VALUES ({id},'{appName}','{nameUsed}','{passwordUsed}')")
    db.commit()
    table = db.execute(f"SELECT * FROM databae WHERE user_id = {id}")
    return render_template("table.html", table = table)

@app.route("/list")
def list():
    return render_template("table.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
