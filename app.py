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
app.secret_key = "SECRET_KEY"

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
    return redirect("/")

# ========================================================================
@app.route("/login_process_", methods = ["POST"])
def login_process_():
    name = request.form.get("name")
    user = db.execute(f"SELECT * FROM human WHERE name = '{name}'").fetchall()
    for u in user:
        password = u.password
        passowrd_check = request.form.get("password")
        if user:
            if password == passowrd_check:
                session["name"] = u.name
                return redirect(f"/homepage/{u.name}")
        else:
            session["name"] = None
            return render_template("error.html", message = "Wrong password!")
    else:
        return render_template("error.html", message = "No such user!")
# =========================================================================

# @app.route("/settings")
# def settings():
#     if not session.get("name"):
#         return redirect("/")
#     name = session["name"]
#     user = db.execute(f"SELECT * FROM human WHERE name = {name}").fetchall()
#     return render_template("settings.html", user = user)

@app.route("/homepage/<string:name>")
def homepage(name):
    if not session.get("name"):
        return redirect("/")
    elif session["name"] == name:
        user = db.execute(f"SELECT * FROM human WHERE name = '{name}'").fetchall()
        for u in user:
            id = u.id
        table = db.execute(f"SELECT * FROM databae WHERE user_id = {id}").fetchall()
        return render_template("table.html", user = user, table = table)
    else:
        return render_template("error.html", message = "You do not have access to this data")

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
    user = db.execute(f"SELECT * FROM human WHERE id = {id}")
    for u in user:
        return redirect(f"homepage/{u.name}")

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect("/")
