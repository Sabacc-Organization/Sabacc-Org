from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
from flask_socketio import SocketIO, send, emit
import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app, cors_allowed_origins=["https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws", "https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/chat", "https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/game", "https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/bet", "https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/card", "https://ide-cc53314679134f648784a767fd9887a4-8080.cs50.ws/shift"])

# Declare dictionary to store key-value pairs of user ids and session ids
users = {}

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///sabacc.db")


@app.route("/")
def index():
    """Show home page"""

    # Get the user's id for later use
    user_id = session.get("user_id")

    games = db.execute(f"SELECT * FROM games WHERE (player1_id = ? OR player2_id = ?) AND completed = 0 ORDER BY game_id DESC", user_id, user_id)
    users = db.execute("SELECT * FROM users")
    usernames = {}
    for user in users:
        usernames[user["id"]] = user["username"]

    # Render the home page with the user's active game data
    return render_template("index.html", games=games, usernames=usernames)


@socketio.on("message", namespace="/chat")
def handleMessage(msg):
    send(msg, broadcast=True)

@app.route("/chat")
@login_required
def chat():
    """Global Chat using Socket.IO"""

    user_id = session.get("user_id")
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]
    return render_template("chat.html", user=user)

@app.route("/host", methods=["GET", "POST"])
@login_required
def host():
    """Make a new game of Sabacc"""

    if request.method == "GET":
        return render_template("host.html")

    elif request.method == "POST":
        player2Username = request.form.get("player2")
        player2 = db.execute(f"SELECT * FROM users WHERE username = ?", player2Username)
        if len(player2) == 0:
            return apology("Invalid player 2 username")

        deckData = constructDeck()
        deck = deckData["deck"]
        player1_hand = deckData["player1_hand"]
        player2_hand = deckData["player2_hand"]

        db.execute("INSERT INTO games (player1_id, player2_id, player1_credits, player2_credits, hand_pot, sabacc_pot, deck, player1_hand, player2_hand, player_turn) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", session.get("user_id"), player2[0]["id"], 985, 985, 10, 20, deck, player1_hand, player2_hand, session.get("user_id"))
        game_id = db.execute("SELECT game_id FROM games WHERE player2_id = ? ORDER BY game_id DESC", player2[0]["id"])[0]["game_id"]
        return redirect(f"/game/{game_id}")


@socketio.on("game", namespace="/game")
def game_connect():
    user_id = session.get("user_id")
    if not user_id:
        return
    sid = request.sid
    users[user_id] = sid

@socketio.on("bet", namespace="/bet")
def bet(data):

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    amount = data["amount"]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    user_id = session.get("user_id")
    
    if game["phase"] != "betting":
        return

    player = ""
    opponent = ""
    if user_id == game["player1_id"]:
        player = "player1"
        opponent = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent = "player1"
    else:
        return

    # If player 1 bets or checks
    if action == "bet" and player == "player1" and game["player_turn"] == game["player1_id"] and amount >= 0 and amount <= game["player1_credits"]:

        db.execute(f"UPDATE games SET player1_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, player_turn = ? WHERE game_id = {game_id}", game["player1_credits"] - amount, amount, None, game["hand_pot"] + amount, game["player2_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame(game, users)

    elif action == "call" and player == "player2" and game["player_turn"] == game["player2_id"] and amount >= 0 and amount <= game["player2_credits"]:

        db.execute(f"UPDATE games SET player2_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", game["player2_credits"] - amount, None, None, game["hand_pot"] + amount, "card", game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame(game, users)
        
    elif action == "call" and player == "player1" and game["player_turn"] == game["player1_id"] and amount >= 0 and amount <= game["player1_credits"]:
        
        db.execute(f"UPDATE games SET player1_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", game["player1_credits"] - amount, None, None, game["hand_pot"] + amount, "card", game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame(game, users)

    elif action == "fold" and player == "player2" and game["player_turn"] == game["player2_id"]:

        player1_hand = ""
        player2_hand = ""
        deckList = []
        if len(deckList) < 4:
            outCards = list(game["player1_hand"].split(",")) + list(game["player2_hand"].split(","))
            print(outCards)
            deckList = reshuffleDeck(game, outCards)
        
        deck = ""

        for i in range(2):
            randDex = random.randint(0, len(deckList) - 1)
            if player1_hand == "":
                player1_hand = deckList[randDex]
            else:
                player1_hand = player1_hand + "," + deckList[randDex]
            deckList.pop(randDex)

        for i in range(2):
            randDex = random.randint(0, len(deckList) - 1)
            if player2_hand == "":
                player2_hand = deckList[randDex]
            else:
                player2_hand = player2_hand + "," + deckList[randDex]
            deckList.pop(randDex)

        for card in deckList:
            if deck == "":
                deck = card
            else:
                deck = deck + "," + card


        db.execute(f"UPDATE games SET player1_credits = ?, player2_credits = ?, player1_bet = ?, player2_bet = ?, hand_pot = ?, phase = ?, deck = ?, player1_hand = ?, player2_hand = ?, player_turn = ? WHERE game_id = {game_id}", game["player1_credits"] + game["hand_pot"] - 5, game["player2_credits"] - 5, None, None, 10, "betting", deck, player1_hand, player2_hand, game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame(game, users)
        
    elif action == "raise" and player == "player2" and game["player_turn"] == game["player2_id"] and amount >= game["player1_bet"] and amount <= game["player2_credits"]:
        
        db.execute(f"UPDATE games SET player2_credits = ?, player2_bet = ?, hand_pot = ?, player_turn = ? WHERE game_id = {game_id}", game["player2_credits"] - amount, amount, game["hand_pot"] + amount, game["player1_id"])

        game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

        emitGame(game, users)
    return

@app.route("/game/<game_id>")
@login_required
def game(game_id):
    """Play Sabacc!"""

    user_id = session.get("user_id")
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    player = ""
    opponent = {}

    if user["id"] == game["player1_id"]:
        player = "player1"
        opponent["player"] = "player2"
    elif user_id == game["player2_id"]:
        player = "player2"
        opponent["player"] = "player1"
    else:
        return apology("This is not one of your games")

    opponent["username"] = db.execute("SELECT username FROM users WHERE id = ?", game[opponent["player"] + "_id"])[0]["username"]
    opponent["cards"] = len(list(game[opponent["player"] + "_hand"].split(",")))
    opponent["credits"] = game[opponent["player"] + "_credits"]

    return render_template("game.html", game=game, player=player, opponent=opponent, username=user["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check that username is valid
        if len(rows) == 0:
            return apology("Invalid username")

        # If the user wants to change their password, do so
        change = request.form.get("change")
        if change != None:

            # Check that passwords are valid
            password = request.form.get("pass")
            if not password:
                return apology("Missing new password")

            passCon = request.form.get("passCon")
            if not passCon:
                return apology("Missing new password confirmation")

            if password != passCon:
                return apology("New passwords do not match")

            # Change user's password
            passHash = str(generate_password_hash(password))
            db.execute(f"UPDATE users SET hash = ? WHERE username = ?", passHash, username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Check that username is inputted
        username = request.form.get("username")
        if not username:
            return apology("Missing username", 400)

        # Check passwords are there and match
        password = request.form.get("password")

        if not password:
            return apology("Missing password", 400)

        confirmation = request.form.get("confirmation")

        if not confirmation:
            return apology("Missing confirmation password", 400)

        if confirmation != password:
            return apology("Confirmation and password do not match")

        # Make sure that username is not a duplicate of an old one
        usernames = db.execute("SELECT username FROM users")
        duplicate = False
        for u in usernames:
            if username == u["username"]:
                duplicate = True
                return apology("Someone else already took that username", 400)

        # Complete registration
        username = request.form.get("username")
        password = request.form.get("password")
        passHash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, str(passHash))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    elif request.method == "GET":
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
