from flask import redirect, render_template, request, session, jsonify
from functools import wraps
import random
from flask_socketio import emit
import psycopg
from dataHelpers import *
from cs50 import SQL
from werkzeug.security import check_password_hash
import yaml

# Get config.yml data
config = {}
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

# Connect to database
conn = psycopg.connect(config['DATABASE'])
db = conn.cursor()

# Global deck constant
DECK = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17"

# For getting a list of dictionaries for rows in a database.
def getDictsForDB(cursor: psycopg.Cursor):
    rows = cursor.fetchall()
    columns = cursor.description

    returnList = []
    for row in rows:
        rowDict = {}
        for i, col in enumerate(columns):
            rowDict[col.name] = row[i]
        returnList.append(rowDict)
    
    return returnList

# Deprecated function for returning error pages to users
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# Deprecated decorated function for requiring users to login on certain pages
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Attempt to Authenticate User
def checkLogin(username, password):
    # If username is none
    if not username:
        return {"message": "Must provide username", "status": 401}

    # If password is none
    if not password:
        return {"message": "Must provide password", "status": 401}
    
    # Attempt to find the password hash of this user
    orHash = None
    try:
        db.execute("SELECT * FROM users WHERE username = %s", [username])
        orHash = getDictsForDB(db)[0]["hash"]
    except IndexError:
        # If user does not exist
        return {"message": f"User {username} does not exist", "status": 401}

    # Check if password is correct using password hashes
    if check_password_hash(orHash, password) == False:
        return {"message": f"Incorrect password", "status": 401}
    
    # User authenticated!
    return {"message": "Logged in!", "status": 200}

# Draw a card
def drawCard(deckStr):

    # Turn deck into a list
    deckList = deckStr.split(",")

    # Draw the card
    randDex = random.randint(0, len(deckList) - 1)
    card = deckList.pop(randDex)

    # Turn deck back into string
    deck = listToStr(deckList)

    # Return deck and card drawn
    data = {"deck": deck, "card": card}
    return data

# Roll the Shift dice
def rollShift():
    # Roll the dice
    dieOne = random.randint(1, 6)
    dieTwo = random.randint(1, 6)
    
    # If doubles, shift
    if dieOne == dieTwo:
        return True
    else:
        return False