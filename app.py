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
import requests
from bs4 import BeautifulSoup

# Configuring Flask
app = Flask(__name__)

# Configuring socketio, something ChatGPT recommended us to use to see live responses and real time updates
socketio = SocketIO(app)
app.debug = True

# Setting a secret key for each session
app.config['SECRET_KEY'] = os.urandom(16)

# Configuring each flask session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Connects to database 
def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

# Render home.html page so user will see the page when website clicked on
@app.route('/')
def index():
    """ Homepage """

    # Connect to database to get users and display on the home page also get all user data
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    count = conn.execute('SELECT COUNT(*) AS user_count FROM users').fetchone()['user_count']
    conn.close()

    return render_template('home.html', data=users, userCount=count)


# Render login.html page
@app.route('/login', methods=["GET", "POST"])
def login():
    """ Login user """

    # Forget any user_id from previous
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Make sure that a username was submitted, otherwise tell user they need one
        if not request.form.get("username"):
            return apology("must provide username", 403)
        
        # Make sure password was submitted, otherwise tell the user to input one
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query database for username and allow user to log in if it is our database
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        conn.close()

        # Make sure that username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        
        # This allows us to remember which user has logged in, and be used in other places
        session["user_id"] = rows[0]["id"]

        flash('Successfully logged in!')

        # Redirect user to home page, but give them the homepage for logged in users.
        return redirect("/landing")

    # Else make user return to login page if user does not do anything
    else:
        return render_template("login.html")

# Render the register.html page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Get the input fields from registration form, and also use this to register the user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Make sure a username is submitted
        if not username:
            return apology("must provide username", 400)

        # Make sure a password is submitted
        elif not password:
            return apology("must provide password", 400)

        # Make sure that the password and confirmation password match
        elif password != confirmation:
            return apology("password and confirmation must match", 400)

        try:

            # Add the new user to the same database used for login, so for future logins, the user will have the account data stored
            conn = sqlite3.connect('site.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:

            # Return an error if username is already taken by someone else
            return apology("username taken", 400)

        # Redirect the user back to homepage after registering for the betting site
        return redirect("/")
    
    # If nothing is submitted, stay on register
    else:
        return render_template("register.html")


@app.route("/landing", methods=["GET", "POST"])
def landing():
    """Sends logged-in user to landing dashboard"""

    # Check if the user is logged in
    if "user_id" not in session:
        # Redirect to login page if no user is logged in
        return redirect("/login")

    # Grab user ID
    user_id = session["user_id"]

    # Query database for the logged-in user's information
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
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
    """Display game stats via redirect."""
    
    # Dictionary of years to URLs
    game_urls = {
        2010: "https://www.espn.com/college-football/game/_/gameId/303240108/yale-harvard",
        2011: "https://www.espn.com/college-football/game/_/gameId/313230043/harvard-yale",
        2012: "https://www.espn.com/college-football/game/_/gameId/323220108/yale-harvard",
        2013: "https://www.espn.com/college-football/game/_/gameId/333270043/harvard-yale",
        2014: "https://www.espn.com/college-football/game/_/gameId/400558443/yale-harvard",
        2015: "https://www.espn.com/college-football/game/_/gameId/400799629/harvard-yale",
        2016: "https://www.espn.com/college-football/game/_/gameId/400871335/yale-harvard",
        2017: "https://www.espn.com/college-football/game/_/gameId/400951036/harvard-yale",
        2018: "https://www.espn.com/college-football/game/_/gameId/401035274/yale-harvard",
        2019: "https://www.espn.com/college-football/game/_/gameId/401128680/harvard-yale",
        2020: None,  # COVID year
        2021: "https://www.espn.com/college-football/game/_/gameId/401344147/harvard-yale",
        2022: "https://www.espn.com/college-football/game/_/gameId/401418602/yale-harvard",
        2023: "https://www.espn.com/college-football/game/_/gameId/401540345/harvard-yale",
        2024: "https://www.espn.com/college-football/game/_/gameId/401644605/yale-harvard",
    }

    embed_url = None
    error = None
    # make sure that the inputted year is valid, and also if year is 2020, describe why the game wasnt played. 
    if request.method == "POST":
        year = request.form.get("year")
        if not year or not year.isdigit():
            error = "Please enter a valid year."
        else:
            year = int(year)
            if year == 2020:
                # Special case for COVID
                error = "No game played in 2020 due to COVID-19."
            elif year in game_urls:
                embed_url = game_urls[year]
            else:
                error = f"No data available for the year {year}."

    return render_template("stats.html", embed_url=embed_url, error=error)



def scrape_game_stats(url, year):
    """Scrape game stats from a given ESPN URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # scraping logic so we can pull to find the ESPN website for users to see
        stats = []
        stats_table = soup.find('table', class_='Table') 
        if stats_table:
            # skip the header row because it doesn't have what we need to query
            for row in stats_table.find_all('tr')[1:]: 
                cells = row.find_all('td')
                stats.append({
                    "Year": year,
                    "Statistic": cells[0].get_text(strip=True),
                    "Harvard": cells[1].get_text(strip=True),
                    "Yale": cells[2].get_text(strip=True),
                })
        return stats
    # debugging, can ignore
    except requests.RequestException as e:
        print(f"Error fetching the page for {year}: {e}")
        return []
    except AttributeError:
        print(f"Could not parse stats table for {year}.")
        return []

@app.route("/live")
def live():
    """Render the live betting page."""
    if "user_id" not in session:
        return redirect("/login")

    # get the user's current balance
    user_id = session["user_id"]
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT cash FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    # let the user know the cash that they hvae
    return render_template("live.html", user_balance=user["cash"])


# socketio is a live server updating app from chatgpt that gave us an idea on how to make our betting application live
@socketio.on("update_odds")
def handle_odds_update(data):
    """Broadcast new odds to all connected clients."""
    emit("odds_update", data, broadcast=True)

@app.route("/add_money", methods=["POST"])
def add_money():
    """Allow users to add money to their balance."""

    # make sure user is signed in
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    amount = float(request.form.get("amount"))

    # make sure that the amount is valid
    if amount <= 0:
        flash("Please enter a valid amount to add!", "danger")
        return redirect("/live")

    # Update the user's balance in the database
    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET cash = cash + ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()

    # tell user how much money is added
    flash(f"Successfully added ${amount:.2f} to your balance!", "success")
    return redirect("/live")


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

    # validate the bet amount by making sure it is not over the money user has, and is non negative
    if bet_amount <= 0:
        flash("Bet amount must be greater than 0!", "danger")
        return redirect("/live")
    if bet_amount > user_balance:
        flash("Insufficient balance to place the bet!", "danger")
        return redirect("/live")

    # Subtract out the beg amount
    cursor.execute("UPDATE users SET cash = cash - ? WHERE id = ?", (bet_amount, user_id))
    cursor.execute(
        "INSERT INTO bets (user_id, bet_option, bet_amount) VALUES (?, ?, ?)",
        (user_id, bet_option, bet_amount),
    )
    conn.commit()
    conn.close()
    
    # tell the user that the bet is sucessful
    flash("Bet placed successfully!", "success")
    return redirect("/live")


def update_odds():
    """Simulate real-time odds updates."""
    while True:
        # odds data for next year currently
        new_odds = {
            "spread1": "-1.5",
            "spread2": "+1.5",
            "money1": "-120",
            "money2": "+120",
            "total": "46.5"
        }
        # broadcast the odds to all clients
        socketio.emit("odds_update", new_odds, to=None)
      
        # update odds every 10 seconds
        time.sleep(10)  

# atart the odds updater thread
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
    # if the user is not in the session to bet, then redirect them
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("site.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT users.username, bets.bet_option, bets.bet_amount, bets.timestamp "
        "FROM bets JOIN users ON bets.user_id = users.id ORDER BY bets.timestamp DESC"
    )

    # make the bets get all
    all_bets = cursor.fetchall()
    conn.close()

    return render_template('bets.html', bets=all_bets)

def generate_betting_lines():
    try:
        while True:
            # betting line generation for lines in 2025
            betting_lines = {
                "team1": "Harvard",
                "team2": "Yale",
                "spread1": "-1.5",
                "spread2": "+1.5",
                "money1": "-120",
                "money2": "+120",
                "total_over": "46.5",
                "total_under": "46.5",
            }
            socketio.emit("update_lines", betting_lines)
            time.sleep(1)
    except Exception as e:
        print(f"Error in generate_betting_lines thread: {e}")

# make it so the fake buy be made so that you can submit form
@app.route('/eventcontract', methods=["POST"])
def eventcontract():
    """ Flash bought message"""
    if request.method == "POST":
        contract_count = request.form.get("contract-count")

        # display bought
        flash("Bought " + str(contract_count) + " event contracts!")
        # return back to landing
        return redirect("/landing")
    
    # stay without refreshing
    else:
        return render_template("landing.html")


# Start a background thread to generate betting lines
threading.Thread(target=generate_betting_lines, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
