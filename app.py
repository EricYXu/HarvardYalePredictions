import os
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, emit
from threading import Thread
import time
import random
import threading
from helpers import apology

# Configuring Flask
app = Flask(__name__)
socketio = SocketIO(app)
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

    # Connect to database to get users and display on the home page
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    count = conn.execute('SELECT COUNT(*) AS user_count FROM users').fetchone()['user_count']
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
        if not username:
            return apology("must provide username", 400)

        # Ensures password is submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensures password and confirmation match
        elif password != confirmation:
            return apology("password and confirmation must match", 400)

        try:
            # Adds new user to the same database used for login
            conn = sqlite3.connect('site.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            # Returns error if username is already taken
            return apology("username taken", 400)

        # Redirects user back to homepage after registering
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/landing", methods=["GET", "POST"])
def landing():
    """Sends logged-in user to landing dashboard"""

    # Check if the user is logged in
    if "user_id" not in session:
        # Redirect to login page if no user is logged in
        return redirect("/login")

    # Query database for the logged-in user's information
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()

    # Pass user data to the template
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


@app.route("/stats", methods=["GET", "POST"])
def stats():
    """Display or filter game statistics."""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Default query
    query = "SELECT * FROM GameData"
    params = []

    # If user submits filters
    if request.method == "POST":
        year = request.form.get("year")
        winner = request.form.get("winner")

        # Build the query dynamically based on filters
        filters = []
        if year:
            filters.append("Year = ?")
            params.append(year)
        if winner:
            filters.append("Winner = ?")
            params.append(winner)

        if filters:
            query += " WHERE " + " AND ".join(filters)

    # Execute the query
    data = cursor.execute(query, params).fetchall()
    conn.close()

    return render_template("stats.html", data=data)

@app.route("/live")
def live():
    """Render the live betting page."""
    if "user_id" not in session:
        return redirect("/login")

    # Fetch the user's current balance
    user_id = session["user_id"]
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template("live.html", user_balance=user["cash"])


# socketio is a live server updating app from chatgpt that gave us an idea on how to make our betting application live
@socketio.on("update_odds")
def handle_odds_update(data):
    """Broadcast new odds to all connected clients."""
    emit("odds_update", data, broadcast=True)

@app.route("/place_bet", methods=["POST"])
def place_bet():
    """Handle user bet placement."""
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    bet_option = request.form.get("bet_option")
    bet_amount = float(request.form.get("bet_amount"))

    # Connect to the database
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch user's current balance
    cursor.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found!", "danger")
        return redirect("/live")

    user_balance = user["cash"]

    # Validate the bet amount
    if bet_amount <= 0:
        flash("Bet amount must be greater than 0!", "danger")
        return redirect("/live")
    if bet_amount > user_balance:
        flash("Insufficient balance to place the bet!", "danger")
        return redirect("/live")

    # Deduct the bet amount and log the bet
    cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (bet_amount, user_id))
    cursor.execute(
        "INSERT INTO bets (user_id, bet_option, bet_amount) VALUES (?, ?, ?)",
        (user_id, bet_option, bet_amount),
    )
    conn.commit()
    conn.close()

    flash("Bet placed successfully!", "success")
    return redirect("/live")


def update_odds():
    """Simulate real-time odds updates."""
    while True:
        # Example odds data
        new_odds = {
            "spread1": "-1.5",
            "spread2": "+1.5",
            "money1": "-120",
            "money2": "+120",
            "total": "46.5"
        }
        # Broadcast the odds to all clients
        socketio.emit("odds_update", new_odds, to=None)
        time.sleep(10)  # Update odds every 10 seconds

# Start the odds updater thread
Thread(target=update_odds).start()

def get_match_data(match_id):
    """Fetch match data from the database."""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM Matches WHERE id = ?"
    match = cursor.execute(query, (match_id,)).fetchone()
    conn.close()
    return match

@app.route('/bets')
def bets():
    """Display bets and live betting lines."""
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT users.username, bets.bet_option, bets.bet_amount, bets.timestamp "
        "FROM bets JOIN users ON bets.user_id = users.id ORDER BY bets.timestamp DESC"
    )
    all_bets = cursor.fetchall()
    conn.close()

    return render_template('bets.html', bets=all_bets)

def generate_betting_lines():
    while True:
        betting_lines = {
            "team1": "Harvard",
            "team2": "Yale",
            "spread1": f"{random.uniform(-3.5, 3.5):.1f}",
            "spread2": f"{random.uniform(-3.5, 3.5):.1f}",
            "money1": f"{random.randint(-200, 200)}",
            "money2": f"{random.randint(-200, 200)}",
            "total_over": f"{random.uniform(40.0, 50.0):.1f}",
            "total_under": f"{random.uniform(40.0, 50.0):.1f}"
        }
        socketio.emit("update_lines", betting_lines)  # Send betting lines to all connected clients
        time.sleep(1)  # Update every second

# Start a background thread to generate betting lines
threading.Thread(target=generate_betting_lines, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)