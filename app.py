import os
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3

from helpers import apology

app = Flask(__name__)
app.debug = True

# Connects to database
def get_db_connection():
    conn = sqlite3.connect('harvard.db')
    conn.row_factory = sqlite3.Row
    return conn

# Render home.html page
@app.route('/')
def index():
    """ Homepage """

    # Connects to database to get users
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('home.html', data=users)

# Render login.html page
@app.route('/login', methods=["GET", "POST"])
def login():
    """ Login user """
    return render_template('./login.html')

# Render register.html page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Step 1: Grab input fields
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Step 2: Validate fields
        # Ensures username is submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensures password is submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensures password and confirmation match
        elif password != confirmation:
            return apology("password and confirmation must match", 400)

        # Tries to insert the user info into database
        try:
            id = db.execute("INSERT INTO users (username,hash) VALUES(?,?)", username, generate_password_hash(password))
        except ValueError:
            return apology("username taken")

        # Redirects user back to homepage after registering
        return redirect("/")

    else:
        return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)