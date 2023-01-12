# HBT tracker

<p align="center">
    <a href="https://habit-tracker-l6h0.onrender.com">
        <img src="./static/assets/banner.png" width="600" />
    </a>
</p>

<p align="center"><img src="https://i.imgur.com/qospQMX.gif" width="600" /></p>
<p align="center"><img src="https://i.imgur.com/b8Ptkzb.gif" width="600" /></p>
<p align="center"><img src="https://i.imgur.com/kOJz7Ab.gif" width="600" /></p>

## How to run

### Prerequisites

Before you start, you need to have [Python](https://www.python.org/downloads/) 3.8 (or higher version) installed on your machine.

### Running

```bash
# clone this repository
$ git clone <https://github.com/plhrsl/habit-tracker>

# enter the project folder
$ cd habit-tracker

# start a virtual environment (here i'm using pipenv)
$ pipenv shell

# install the requirements to run the project
$ pip install -r requirements.txt

# start the web server
$ python -m flask run

# the development server will start at http://localhost:5000/
```

## Technologies

- HTML, CSS and Javascript with Bootstrap
- Pyhton with Flask
- SQLite

## Details

### Usage

To use the app the first step is to create an account and log in. Once logged in, the user can start adding habits by giving a name and its frequency. In the home page the user can keep weekly track of their habits, by checking when concluded on that particular day of the week. It is also possible to edit and delete existing habits.

### Implementation overview

The frontend was build with HTML, CSS, JavaScript and the Bootstrap framework.

Flask was used in the backend of the application to implement its funtionalities:

- user registration and login
- habits _CRUD_ - create, read, update and delete
- track progress of the week

To access the funtionalities of the app, the user must be registered and logged in. To ensure that, Flask sessions was used.

The database used was SQLite, with the SQLAlchemy library.

There are three tables in the database: user, habit and checkbox. The last one is updated dinamically using JavaScript POST requests to keep track of the habits checkboxes.

### Going through the files

- templates folder

  This folder contains every `html` file of the application, such as the `base.html` - that is the base template for all pages.

- static folder

  This folder contains:

  - `styles.css` - which is really short, given that virtually all stylization was done through Bootstrap classes.
  - `script.js` - which dynamically sends POST requests every time there is a change in one of the checkboxes of habits or the "clear" button is clicked. It also highlights the current day of the week in the homepage table and calculates the current percentage of the progress bar.
  - assets folder - where is the `logo.png`

- `app.py`

  This is the main file of the application, in which all of the website funtionalities is implemented.

  This file also defines the database - `habit_tracker.db` -, as well as its tables - user, habit and checkbox -, through SQLAlchemy's object-relational mapping.

  The routes determine the functioning of each of the pages through Python functions. The routes of this app are:

  - `"/register"`, `"/login"` and `"/logout"`: which, respectively, inserts new users into the database, starts a new session if the user has provided valid credentials, and ends the session.

  - `"/new-habit"`, `"/habits"`, `"/edit"` and `"/delete"`: which, respectively, inserts new habits into the database, returns the already existing habits of the logged user, updates and deletes especifics habits given its id.

  - `"/"`: thats the `index.html` route, in which a table with the habits and checkboxes in the days of the week corresponding to its frequency is displayed. For that, the route needs to return data from the checkbox and habit tables corresponding to the user of the current session. In addition, the logged in user's name and the current date are also provided as parameters.

#### Video demo: https://youtu.be/_cSq8iq5VMQ

_My name is Luana, and this was my final project for CS50!_
