import os
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

# Configuring Flask
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.urandom(16)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Connects to database
def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

# Render home.html page
@app.route('/')
def index():
    """ Homepage """

    # Connects to database to get users and display on home page
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    count = conn.execute('SELECT COUNT(*) FROM users').fetchall()
    conn.close()

    return render_template('home.html', data=users, userCount=count)

# Render login.html page
@app.route('/login', methods=["GET", "POST"])
def login():
    """ Login user """

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        conn.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash('Successfully logged in!')

        # Redirect user to home page, TODO: insert user data from SQL query here
        return redirect("/landing")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Render register.html page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Grab input fields from registration form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensures username is submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensures password is submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensures password and confirmation match
        elif password != confirmation:
            return apology("password and confirmation must match", 400)

        try:
            # Adds new user to database
            connection = sqlite3.connect('harvard.db')
            with open('schema.sql') as f:
                connection.executescript(f.read())
            cur = connection.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",(username, generate_password_hash(password)))
            connection.commit()
            connection.close()
        except ValueError:
            # Returns error if username already taken
            return apology("username taken")

        # Redirects user back to homepage after registering
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/landing", methods=["GET", "POST"])
def landing():
    """ Sends logged-in user to landing dashboard """

    # Query database for username
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchall() # TODO: There is some issue with session --> FIX
    conn.close()
    
    return render_template("landing.html", data=user)

@app.route("/logout")
def logout():
    """ Logs user out """

    # Clears session and forget user_id
    session.clear()
    return redirect("/")

@app.route("/bet", methods=["GET", "POST"])
def bet():
    """ Betting dashboard for logged in user """

    return render_template("bet.html")

if __name__ == '__main__':
    app.run(debug=True)