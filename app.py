import os

from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from time import strftime

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habit_tracker.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(14), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Habit %r>' % self.id


class Checkbox(db.Model):
    id = db.Column(db.String(4), primary_key=True)
    value = db.Column(db.String(8), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Check %r>' % self.id

with app.app_context():     
    db.create_all()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


days = {
    0: "Sun",
    1: "Mon",
    2: "Tues",
    3: "Wed",
    4: "Thurs",
    5: "Fri",
    6: "Sat",
}


def habit_table(habits):
    return [
        {
            "id": habit.id,
            "name": habit.description,
            "frequency": [int(day) for day in habit.frequency.split()]
        } for habit in habits
    ]


def checkboxes(checks):
    return {check.id: check.value for check in checks}


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") is None:
        return redirect("/login")

    name = User.query.filter_by(id=session["user_id"]).first().name
    habits = habit_table(Habit.query.filter_by(
        user_id=session["user_id"]).all())
    formatted_date = date.today().strftime("%d %B, %Y")
    

    if request.method == "POST":
        if request.json.get("type") == "clear":
            checks = Checkbox.query.filter_by(user_id=session["user_id"]).all()
            for checkbox in checks:
                checkbox.value = ""
        else:
            checkbox = Checkbox.query.get_or_404(request.json.get("id"))
            checkbox.value = request.json.get("value")
        db.session.commit()
        
    checks = checkboxes(Checkbox.query.filter_by(user_id=session["user_id"]).all())
    return render_template('index.html', name=name, days=days, habits=habits, date=formatted_date, checks=checks)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            flash("Must provide username and password...")
            return redirect("/login")
        user = User.query.filter_by(
            username=request.form.get("username")).first()
        if user is None or not check_password_hash(user.hash, request.form.get("password")):
            flash("Invalid username and/or password...")
            return redirect("/login")
        session["user_id"] = user.id
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if not request.form.get("name") or not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("All fields must be filled...")
            return redirect("/register")
        usernameNotAvailable = User.query.filter_by(
            username=request.form.get("username")).first()
        if usernameNotAvailable != None:
            flash("Username not available...")
            return redirect("/register")
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords did not match...")
            return redirect("/register")
        user = User(name=request.form.get("name"), username=request.form.get(
            "username"), hash=generate_password_hash(request.form.get("password")))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect("/")
    else:
        return render_template("register.html")


def habits_display(habits):
    return [
        {
            "id": habit.id,
            "name": habit.description,
            "frequency": " - ".join([days[int(day)] for day in habit.frequency.split()])
        } for habit in habits
    ]


@app.route("/habits")
def habits():
    if session.get("user_id") is None:
        return redirect("/login")
    hab_dis = habits_display(Habit.query.filter_by(
        user_id=session["user_id"]).all())
    return render_template("habits.html", habits=hab_dis)


@app.route("/new-habit", methods=["POST", "GET"])
def new_habit():
    if session.get("user_id") is None:
        return redirect("/login")
    if request.method == "POST":
        if not request.form.get("name") or not request.form.getlist("frequency"):
            flash("Invalid name and/or frequency...")
            return redirect("/new-habit")
        frequency_str = " ".join(request.form.getlist("frequency"))
        habit = Habit(description=request.form.get("name"),
                      frequency=frequency_str, user_id=session["user_id"])
        db.session.add(habit)
        db.session.flush()
        db.session.refresh(habit)
        for day in days:
            checkbox = Checkbox(id=str(day)+" "+str(habit.id), value="", user_id=session["user_id"])
            db.session.add(checkbox)
        db.session.commit()
        
        return redirect("/")
    else:
        return render_template("new-habit.html", days=days)


def habit_edit(habit):
    return {
        "id": habit.id,
        "name": habit.description,
        "frequency": ["checked" if str(i) in habit.frequency.split() else "" for i in range(7)]
    }


@app.route("/edit/<int:id>", methods=["POST", "GET"])
def edit(id):
    if session.get("user_id") is None:
        return redirect("/login")
    habit = Habit.query.get_or_404(id)
    if request.method == "POST":
        if not request.form.get("name") or not request.form.getlist("frequency"):
            flash("Invalid name and/or frequency...")
            return redirect("/edit/"+str(id))
        habit.description = request.form.get("name")
        frequency_str = " ".join(request.form.getlist("frequency"))
        habit.frequency = frequency_str
        try:
            db.session.commit()
            return redirect("/")
        except:
            flash("There was an error editing the habit...")
            return redirect("/")
    else:
        return render_template("edit.html", habit=habit_edit(habit), days=days)


@app.route("/delete/<int:id>")
def delete(id):
    if session.get("user_id") is None:
        return redirect("/login")
    habit = Habit.query.get_or_404(id)
    search = "% "+str(id)
    try:
        db.session.delete(habit)
        for i in range(7):
            check = Checkbox.query.get_or_404(str(i)+" "+str(id))
            db.session.delete(check) 
        db.session.commit()
        return redirect("/habits")
    except:
        flash("There was an error deleting the habit...")
        return redirect("/habits")
    
    
@app.route("/logout")
def logout():
    if session.get("user_id") is None:
        return redirect("/login")
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)