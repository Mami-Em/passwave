import os
from types import MethodDescriptorType
import psycopg2

from flask import Flask, render_template, redirect, url_for, request, session
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
        id = u.id
        passowrd_check = request.form.get("password")
        if user:
            if password == passowrd_check:
                session["name"] = u.name
                session["password"] = passowrd_check
                session["id"] = id
                return redirect(f"/homepage/{u.name}")
        else:
            session["name"] = None
            return render_template("error.html", message = "Wrong password!")
    else:
        return render_template("error.html", message = "No such user!")
# =========================================================================

@app.route("/settings")
def settings():
    if not session.get("name"):
        return redirect("/")
    return render_template("settings.html")

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

@app.route("/insert_data", methods = ["POST"])
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

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get("name"):
        return redirect('/')
    delete = db.execute(f"SELECT * FROM databae WHERE id = {id}").fetchall()
    return render_template("deleting.html", delete = delete)

@app.route('/deleting_process/<int:id>', methods = ["GET","POST"])
def deleting_process(id):
    if not session.get("name"):
        return redirect('/')
    password_check = request.form.get("password")
    password = session["password"]
    if request.method == "POST":    
        user = session["name"]
        if password_check == password :
            db.execute(f"DELETE FROM databae WHERE id = {id}")
            db.commit()
            return redirect(url_for("homepage", name = f'{user}', message="successfully deleted!"))
        else :
            session.pop("name", None)
            return render_template("error.html", message = "Wrong password! Please reconnect again, Your session has closed!")

@app.route("/update/<int:id>")
def update(id):
    if not session.get("name"):
        return redirect("/")
    databae = db.execute(f"SELECT * FROM databae WHERE id = {id}").fetchall()
    return render_template("updating.html", databae = databae)

@app.route("/updating_process/<int:id>", methods = ["GET","POST"])
def updating_process(id):
    if not session.get("name"):
        return redirect("/")
    if request.method == "POST":
        appname = request.form.get("appName")
        nameused = request.form.get("nameUsed")
        passwordused = request.form.get("passwordUsed")
        password_check = request.form.get("password")
        password = session["password"]
        if request.method == "POST":    
            user = session["name"]
            password = db.execute(f"SELECT * FROM human WHERE name = '{user}'").fetchall()
            for pas in password:
                if password_check == pas.password :
                    db.execute(f"UPDATE databae SET appname = '{appname}', nameused = '{nameused}', passwordused = '{passwordused}' WHERE id = {id}")
                    db.commit()
                    return redirect(url_for("homepage", name = f'{user}', message="successfully updated!"))
                else :
                    session.pop("name", None)
                    return render_template("error.html", message = "Wrong password! Please reconnect again, Your session has closed!")
    

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect("/")
