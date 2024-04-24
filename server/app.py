""" app.py - Handles all requests to the backend """

# Import Libraries
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_cors import CORS, cross_origin
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import ImmutableMultiDict
from helpers import *
from dataHelpers import *
from alderaanHelpers import *
from traditional.traditionalHelpers import *
from flask_socketio import SocketIO, send, emit
import yaml
import psycopg
from psycopg.types.composite import CompositeInfo, register_composite

# Get config.yml data
config = {}
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

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

# CORS (Cross Origin Resource Sharing) - Getting requests from backend and frontend alike
link = config["DOMAIN"]
linkTwo = config["CROSS_ORIGIN"]
allowedCORS = [link, f"{link}/chat", f"{link}/game", f"{link}/bet", f"{link}/card", f"{link}/shift", f"{link}/protect", f"{link}/cont", linkTwo, f"{linkTwo}/chat", f"{linkTwo}/game", f"{linkTwo}/bet", f"{linkTwo}/card", f"{linkTwo}/shift", f"{linkTwo}/protect", f"{linkTwo}/cont"]
socketio = SocketIO(app, cors_allowed_origins=allowedCORS)
CORS(app, origins=allowedCORS)


# Connect to database
conn = psycopg.connect(config['DATABASE'])

# Open a cursor to perform database operations
db = conn.cursor()

# create custom types
try:
    db.execute("CREATE TYPE Suit AS ENUM ('flasks','sabers','staves','coins','negative/neutral');")
    db.execute("CREATE TYPE Card AS (val INTEGER, suit SUIT, protected BOOL);")
    db.execute("""
        CREATE TYPE Player AS (
        id INTEGER,
        username TEXT,
        credits INTEGER,
        bet INTEGER,
        hand Card[],
        folded BOOL,
        lastaction TEXT);
    """)
    print('created custom types')
except psycopg.errors.DuplicateObject:
    # print('custom types alr exist')
    conn.rollback()

# register custom types
card_type = CompositeInfo.fetch(conn, 'card')
player_type = CompositeInfo.fetch(conn, 'player')
register_composite(card_type, db)
register_composite(player_type, db)

# create tables
db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)")
db.execute("CREATE TABLE IF NOT EXISTS games (game_id SERIAL PRIMARY KEY, players PLAYER[], hand_pot INTEGER NOT NULL DEFAULT 0, sabacc_pot INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'betting', deck CARD[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, shift BOOL NOT NULL DEFAULT false, completed BOOL NOT NULL DEFAULT false)")

# create test game
deck = [Card(val=n, suit=Suit.COINS) for n in range(1,11)]
hand = [Card(-2, Suit.NEGATIVE_NEUTRAL)] * 2
players = [Player(id=1,username='thrawn',credits=1000,hand=hand,lastAction='bet')]
lastId = db.execute("SELECT game_id FROM games").fetchall()
game = Game(id=(lastId[-1][0]+1 if lastId else 1),players=players,deck=deck,player_turn=1,p_act='trade',hand_pot=5,sabacc_pot=10)
try:
    db.execute("INSERT INTO games VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", game.toDb(card_type, player_type))
    print(f'created game {game.id}')
except:
    print(f'game {game.id} alr exists')
    conn.rollback()

# commit changes
conn.commit()

# close connection
conn.close()


""" REST APIs """

@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    """Log user in"""

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # If the user wants to change their password, do so
    # change = request.json.get("change")
    # if change != None:

    #     # Check that passwords are valid
    #     newPassword = request.json.get("newPassword")
    #     if not newPassword:
    #         return jsonify({"message": "Missing new password"}), 401

    #     passCon = request.json.get("passCon")
    #     if not passCon:
    #         return apology("Missing new password confirmation") # TODO LEFT OFF HERE

    #     if password != passCon:
    #         return apology("New passwords do not match")

    #     # Change user's password
    #     passHash = str(generate_password_hash(password))
    #     db.execute(f"UPDATE users SET hash = ? WHERE username = ?", passHash, username)

    # Remember which user has logged in
    # session["user_id"] = rows[0]["id"]

    # # Set default themes
    # session["dark"] = False
    # session["theme"] = "rebels"

    # User has logged in successfully!
    return jsonify({"message": "Logged in!"}), 200

    
@app.route("/", methods=["POST"])
@cross_origin()
def index():

    """ Get Info for Home Page """

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]
    
    # Get the user's id for later use
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Query the database for all the games
    games = db.execute("SELECT * FROM games")
    newGames = games.copy()

    # IDs of users in games
    user_ids = []

    # Who's turn it is in each game
    player_turns = []

    # Remove games that have been completed and that are not relevant to the player
    for game in games:
        if str(user_id) not in game["player_ids"].split(",") or game["completed"] == True:
            newGames.remove(game)

        else:
            user_ids.append(game["player_ids"].split(","))
            player_turns.append(db.execute("SELECT username FROM users WHERE id = ?", game["player_turn"])[0]["username"])


    # Get all the relevant usernames from the database
    usernames = []
    for set in user_ids:
        s = ""
        for user in set:
            s += str(db.execute("SELECT * FROM users WHERE id = ?", int(user))[0]["username"]) + ", "

        st = s.strip(", ")

        usernames.append(st)

    # Return data
    return jsonify({
        "games": newGames, 
        "usernames": usernames, 
        "gamesLen": len(newGames), 
        "player_turns": player_turns
        }), 200

@app.route("/register", methods=["POST"])
@cross_origin()
def register():
    """Register user"""
        
    # Ensure username was submitted
    username = request.json.get("username")
    if not username:
        return jsonify({"message": "Must provide username"}), 401
    
    if " " in username:
        return jsonify({"message": "Please do not put spaces in your username"}), 401
    
    # Check that username has not already been taken
    if db.execute("SELECT * FROM users WHERE username = ?", username) != []:
        return jsonify({"message": "Username has already been taken"}), 401
    
    # Ensure password is valid
    password = request.json.get("password")
    if not password:
        return jsonify({"message": "Must provide password"}), 401

    # Ensure confirmation password is valid
    confirmation = request.json.get("confirmPassword")

    if not confirmation:
        return jsonify({"message": "Must provide confirmation password"}), 401

    if confirmation != password:
        return jsonify({"message": "Confirmation and password do not match"}), 401
    
    if " " in password:
        return jsonify({"message": "Please do not put spaces in your password"}), 401

    # Complete registration
    passHash = generate_password_hash(password)
    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, str(passHash))

    # Redirect user to home page
    return jsonify({"message": "Registered!"}), 200
    

@app.route("/game", methods=["POST"])
@cross_origin()
def game():
    """ Get game info for game <game_id> """

    # Get username (if any, guests will not have usernames)
    username = request.json.get("username")
    print(request.json.get("username"))
    
    # Get the user's id if the user is in the game
    user_id = -1
    if username != "":
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
    
    # Get game
    game_id = request.json.get("game_id")
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

    # Get list of usernames of players in game
    users = []
    for u in game["player_ids"].split(","):
        users.append(db.execute("SELECT id, username FROM users WHERE id = ?", int(u))[0]["username"])

    # Return game data
    return jsonify({"message": "Good luck!", "gata": game, "users": users, "user_id": int(user_id)}), 200


@app.route("/host", methods=["POST"])
@cross_origin()
def host():
    """ Make a new game of Sabacc """
    
    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Get list of players in the game
    formPlayers = request.json.get("players")

    # Make list of players
    players = []
    players.append(user_id)

    # Make sure there no more than 8 players
    if len(formPlayers) > 8:
        return jsonify({"message": "You can only have a maximum of eight players"}), 401

    # Ensure each submitted player is valid
    for pForm in formPlayers:
        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return jsonify({"message": f"Player {pForm} does not exist"}), 401
            if str(p[0]["id"]) == str(session.get("user_id")):
                return jsonify({"message": "You cannot play with yourself"}), 401
            if p[0]["id"] in players:
                return jsonify({"message": "All players must be different"}), 401
            players.append(p[0]["id"])

    # Pot size variables
    hPot = 0
    sPot = 0

    # Make list of credits
    credits = []
    for i in range(len(players)):
        credits.append(985)
        hPot += 5
        sPot += 10


    # Convert list data to strings
    playersStr = listToStr(players)
    creditsStr = listToStr(credits)

    # Protecteds
    prots = ""
    for i in range(len(players)):
        prots += "0,0;"

    prots = prots.strip(";")

    # Bets
    pBets = ""
    for i in range(len(players) - 1):
        pBets += ","

    # Construct deck and hands
    deckData = constructDeck(len(players))
    deck = deckData["deck"]
    handsStr = listToStr(deckData["hands"], sep=";")

    # Create game in database
    db.execute("INSERT INTO games (player_ids, player_credits, player_bets, hand_pot, sabacc_pot, deck, player_hands, player_protecteds, player_turn, p_act) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", playersStr, creditsStr, pBets, hPot, sPot, deck, handsStr, prots, user_id, "")

    # Get game ID
    game_id = db.execute("SELECT game_id FROM games WHERE player_ids = ? ORDER BY game_id DESC", playersStr)[0]["game_id"]

    # Redirect user to game
    return jsonify({"message": "Game hosted!", "redirect": f"/game/{game_id}"}), 200
    

""" Gameplay REST APIs """

@app.route("/protect", methods=["POST"])
@cross_origin()
def protect():

    """ Protect a card """

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Get game
    game_id = request.json.get("game_id")
    game = db.execute("SELECT * FROM games WHERE game_id = ?", game_id)[0]

    # Get card being protected
    protect = request.json.get("protect")

    # Get username of requester
    uName = db.execute("SELECT username FROM users where id = ?", user_id)[0]["username"]

    # Get requester's index in list of game players
    uDex = game["player_ids"].split(",").index(str(user_id))

    # Get requester's hand
    u_hand = game["player_hands"].split(";")[uDex]


    # Check if card being protected is in hand
    cardDex = -1
    handL = u_hand.split(",")
    for card in handL:
        if card == protect:
            cardDex = handL.index(card)
            break

    if cardDex == -1:
        print("NON-MATCHING USER INPUT")
        return jsonify({"message": "non matching user input"}), 401


    # Create new List of protected cards
    protectedAll = game["player_protecteds"].split(";")
    protsStr = protectedAll[uDex]
    protsList = protsStr.split(",")
    protsList[cardDex] = 1

    # Convert that List to a String
    protsStr = listToStr(protsList)
    protectedAll[uDex] = protsStr

    protAllStr = listToStr(protectedAll, sep=";")

    # Update the database
    db.execute(f"UPDATE games SET player_protecteds = ?, p_act = ? WHERE game_id = {game_id}", protAllStr, f"{uName} protected a card")

    # Return game data
    gata = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    return jsonify({"message": "Card protected", "gata": gata}), 200


@app.route("/bet", methods=["POST"])
@cross_origin()
def bet():

    """ Players make bets and other betting actions """

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Get game
    game_id = request.json.get("game_id")
    game = db.execute("SELECT * FROM games WHERE game_id = ?", game_id)[0]

    # Get betting action
    action = request.json.get("action")

    # Get amount player is betting
    amount = request.json.get("amount")

    # Get users in game
    users = game["player_ids"].split(",")

    # Get username of requester
    uName = db.execute("SELECT username FROM users where id = ?", user_id)[0]["username"]

    # Get requester's index in list of game players
    u_dex = game["player_ids"].split(",").index(str(user_id))

    # Get players' credits
    creditsStr = game["player_credits"]

    # Get players' bets
    betsStr = game["player_bets"]

    # Variables that will be set true if the game ends or if someon TODO
    endRound = False
    foldEnd = False

    # If phase is not betting
    if game["phase"] != "betting":
        return

    # Check if requester is player 1
    player = ""
    if users.index(str(user_id)) == 0:
        player = "player1"

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return

    # If player 1 bets or checks
    if action == "bet" and player == "player1":

        # Get player's credits
        pCredits = int(strListRead(creditsStr, 0))

        # Remove money from player's credits
        newCredits = strListMod(creditsStr, 0, pCredits - amount)

        # Update the game bets
        newBets = strListMod(betsStr, 0, amount)

        # Write the proper player action string
        act = uName
        if amount == 0:
            act += " checks"
        elif amount != 0:
            act += f" bets ${amount}"

        # Update game
        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[1]), act)


    elif action == "call":

        # Get player's credits
        pCredits = int(strListRead(creditsStr, u_dex))

        # Remove money from player's credits
        newCredits = strListMod(creditsStr, u_dex, pCredits - amount)

        # Update the game bets
        newBets = strListMod(betsStr, u_dex, amount + readIntValStrList(betsStr, u_dex))

        # Update who's turn it is
        nextPlayer = u_dex + 1

        # If it is the end of the betting phase
        if str(user_id) == users[len(users) - 1]:
            endRound = True


        # If a player raised and it has come back to them
        if endRound == False and readIntValStrList(newBets, nextPlayer) == readIntValStrList(newBets, u_dex):

            # If the player that raised was the last player
            if nextPlayer == len(users) - 1:
                endRound = True

            # Skip over player who previously raised to current bet
            nextPlayer += 1

        if endRound == True:
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[nextPlayer]), f"{uName} calls")

    elif action == "raise":

        # Get player's credits
        pCredits = int(strListRead(creditsStr, u_dex))

        # Remove money from player's credits
        newCredits = strListMod(creditsStr, u_dex, pCredits - amount)

        # Update the game bets
        newBets = strListMod(betsStr, u_dex, amount + readIntValStrList(betsStr, u_dex))

        # After a raise, betting loops around to the starting player
        nextPlayer = 0

        # If player raising was in fact the first player
        if str(user_id) == users[0]:
            nextPlayer = 1

        # Update game
        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[nextPlayer]), f"{uName} raises to ${newBets.split(',')[u_dex]}")


    elif action == "fold":

        # Remove folding player fron player's list, hands list, credits list, etc
        newPlayers = strListPop(game["player_ids"], u_dex)
        newHands = strListPop(game["player_hands"], u_dex, sep=";")
        newProtecteds = strListPop(game["player_protecteds"], u_dex, sep=";")
        newCredits = strListPop(creditsStr, u_dex,)
        newBets = strListPop(betsStr, u_dex)

        # Store folded player and their credits properly
        newFoldedP = strListAppend(game["folded_players"], user_id)
        newFoldedC = strListAppend(game["folded_credits"], int(strListRead(creditsStr, u_dex)) + int(strListRead(betsStr, u_dex, default=0)))

        foldEnd = False

        # If the fold caused for only one player to remain and win
        if len(newPlayers.split(",")) == 1:
            foldEnd = True

        # Next player will be in the index of folding player since the folding player is getting bumped
        nextPlayer = u_dex

        # If the folding player is the last player in the cycle
        if str(user_id) == users[len(users) - 1]:
            endRound = True
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET player_ids = ?, player_credits = ?, player_bets = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, folded_players = ?, folded_credits = ?, p_act = ? WHERE game_id = {game_id}", newPlayers, newCredits, newBets, newHands, newProtecteds, int(newPlayers.split(",")[nextPlayer]), newFoldedP, newFoldedC, f"{uName} folds")

    # Update game variables for foldEnd step
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    creditsStr = game["player_credits"]
    betsStr = game["player_bets"]

    # If the last player in the cycle folded, put their credits from hand to pot
    if foldEnd == True:

        newCredits = creditsStr
        newCredits = strListMod(creditsStr, 0, int(strListRead(creditsStr, 0)) + game["hand_pot"] + int(strListRead(betsStr, 0)))

        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, hand_pot = ?, player_turn = ?, completed = ? WHERE game_id = {game_id}", newCredits, "", 0, int(users[0]), str(int(True)))

    # Update game variables for end round steps
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    creditsStr = game["player_credits"]
    betsStr = game["player_bets"]

    # If all the players have participated in the betting round and it time for the card phase
    if endRound == True:
        
        # Make sum of bets to TODO left off here
        betsSum = 0

        # Make a list of empty bets
        newBets = ""
        for i in range(len(users) - 1):
            newBets += ","

        # # Sum up bets to add to hand pot TODO propably eliminate this less efficient code
        # for i in range(len(users)):

        #     try:
        #         betsSum += int(strListRead(betsStr, i))
        #     # If the last player folded the betsStr will be empty
        #     except ValueError:
        #         pass

        # # If the last player folded the bets have already been summed up
        # if foldEnd == True:
        #     betsSum = 0

        # TODO: Test out more efficient code below
        # Sum up bets to add to hand pot
        for i in range(len(users)):

            try:
                betsSum += int(strListRead(betsStr, i))
            # If the last player folded (foldEnd == True) the betsStr will be empty
            except ValueError:
                betsSum = 0
                break


        # Update game
        db.execute(f"UPDATE games SET player_bets = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", newBets, game["hand_pot"] + betsSum, "card", int(users[0]))

    # Return updated game data
    gata = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    return jsonify({"message": "Bet!", "gata": gata}), 200

@app.route("/card", methods=["POST"])
@cross_origin()
def card():


    """ Any card phase actions """ 

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Get game
    game_id = request.json.get("game_id")
    game = db.execute("SELECT * FROM games WHERE game_id = ?", game_id)[0]

    # Action information
    action = request.json.get("action")
    tradeCard = request.json.get("trade")

    # Players list
    users = game["player_ids"].split(",")

    # Username of requester
    uName = db.execute("SELECT username FROM users where id = ?", user_id)[0]["username"]

    # The index of ther user in the list of users
    u_dex = game["player_ids"].split(",").index(str(user_id))

    # Deck
    deckStr = game["deck"]

    # Hands and protected cards
    handsStr = game["player_hands"]
    handsList = handsStr.split(";")
    protsStr = game["player_protecteds"]
    protsList = protsStr.split(";")

    # Hand pot
    handPot = game["hand_pot"]

    # Credits
    creditsStr = game["player_credits"]

    # Indicators of if the card phase and/or game end after an action
    endRound = False
    endGame = False

    # If the game phase is incorrect
    if game["phase"] != "card" and game["phase"] != "alderaan":
        return

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return
    
    if action == "draw":

        # Update deck and hands list according to draw
        drawData = drawCard(deckStr)
        newDeck = drawData["deck"]
        newCard = drawData["card"]
        handsList[u_dex] += "," + newCard
        newHands = listToStr(handsList, sep=";")

        # Update protected cards according to draw
        protsList[u_dex] += ",0"
        newProts = listToStr(protsList, sep=";")

        # Update next player
        nextPlayer = u_dex + 1

        # If this action was from the last player
        if str(user_id) == users[len(users) - 1]:
            endRound = True
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", newDeck, newHands, newProts, int(users[nextPlayer]), f"{uName} draws")

    elif action == "trade":

        # The index of the card that is being traded
        tradeDex = handsList[u_dex].split(",").index(tradeCard)

        # Draw a card and replace the card being traded with it
        drawData = drawCard(deckStr)
        newDeck = drawData["deck"]
        newCard = drawData["card"]
        handsList[u_dex] = strListMod(handsList[u_dex], tradeDex, newCard)
        newHands = listToStr(handsList, sep=";")

        # Update protected cards list
        protsList[u_dex] = strListMod(protsList[u_dex], tradeDex, "0")
        newProts = listToStr(protsList, sep=";")

        # Update next player
        nextPlayer = u_dex + 1

        # If this action was from the last player
        if str(user_id) == users[len(users) - 1]:
            endRound = True
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", newDeck, newHands, newProts, int(users[nextPlayer]), f"{uName} trades")

    elif action == "stand":

        # Pass turn to next player
        nextPlayer = u_dex + 1

        # If this action was from the last player
        if str(user_id) == users[len(users) - 1]:
            endRound = True
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET player_turn = ?, p_act = ? WHERE game_id = {game_id}", int(users[nextPlayer]), f"{uName} stands")


    elif action == "alderaan" and game["cycle_count"] != 0:

        # Pass turn to next player
        nextPlayer = u_dex + 1

        # If this action was from the last player
        if str(user_id) == users[len(users) - 1]:
            endGame = True
            nextPlayer = 0

        # Update game
        db.execute(f"UPDATE games SET phase = ?, player_turn = ?, p_act = ? WHERE game_id = {game_id}", "alderaan", int(users[nextPlayer]), f"{uName} calls Alderaan")


    # Update game data variables
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    handsStr = game["player_hands"]
    handsList = handsStr.split(";")
    protsStr = game["player_protecteds"]
    protsList = protsStr.split(";")
    deckStr = game["deck"]

    # If the action just made was the last one of the card phase
    if endRound == True:

        # Increasing the cycle count
        newCycleCount = game["cycle_count"] + 1

        # If someone had called alderaan, end the game
        if game["phase"] == "alderaan":
            endGame = True

        else:

            # Sabacc Shift procedure

            
            db.execute(f"UPDATE games SET phase = ?, player_turn = ?, cycle_count = ? WHERE game_id = {game_id}", "shift", int(users[0]), newCycleCount)


    # Someone called Alderaan and everyone has done their turn
    if endGame == True:

        # Get end of game data (Winner, winning hand, players that bombed out, etc.)
        alderaanData = alderaanEnd(handsList, deckStr, protsList, False)

        # New card data
        newHands = listToStr(alderaanData["handsList"], sep=";")
        newDeck = listToStr(alderaanData["deck"])
        newProtecteds = listToStr(alderaanData["protsList"], sep=";")

        # Index of the winner in the list of hands
        winnerDex = alderaanData["winner"]

        # The winning hand value
        winnerVal = alderaanData["winnerVal"]

        # Hand values
        handVals = alderaanData["handVals"]

        # Array to store the indexes of hands that bombed out
        bombOutDexes = []

        # Iterate through handVals to find hands that bombed out
        for val in handVals:
            if (val == 0 or abs(val) > 23) and val != winnerVal and val != 230:
                bombOutDexes.append(handVals.index(val))

        # Enact the bomb out transactions for all players that bombed out
        newSabaccPot = game["sabacc_pot"]
        bombOutPrice = int(round((handPot * 0.1)))
        for b in bombOutDexes:
            creditsStr = strListMod(creditsStr, b, int(strListRead(creditsStr, b)) - bombOutPrice)
            newSabaccPot += bombOutPrice

        # String that shows the winner
        winStr = ""

        # If someone one (i.e. not everyone bombed out)
        if winnerDex != -1:
            # Give winner Hand Pot
            creditsStr = strListMod(creditsStr, winnerDex, int(strListRead(creditsStr, winnerDex)) + handPot)

            # Give winner Sabacc Pot it they had a Sabacc
            if abs(winnerVal) == 23 or winnerVal == 230:
                creditsStr = strListMod(creditsStr, winnerDex, int(strListRead(creditsStr, winnerDex)) + newSabaccPot)
                newSabaccPot = 0

            # Update game and winner string
            winner = db.execute(f"SELECT username FROM users where id = {int(users[winnerDex])}")[0]["username"]
            winStr = f"{winner} wins!"

        # If no one won (i.e. everyone bombed out)
        elif winnerDex == -1:
            # Hand pot gets added to Sabacc Pot
            newSabaccPot += handPot

            # Update winStr
            winStr = "Everyone bombs out and loses!"
            
        # Update game
        db.execute(f"UPDATE games SET player_credits = ?, hand_pot = ?, sabacc_pot = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, p_act = ?, completed = ? WHERE game_id = {game_id}", creditsStr, 0, newSabaccPot, newDeck, newHands,  newProtecteds, int(users[0]), winStr, str(int(True)))

    # Return new game data
    gata = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    return jsonify({"message": "Card!", "gata": gata}), 200

@app.route("/shift", methods=["POST"])
@cross_origin()
def shift():
    """ Shift phase """

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Set some variables for the whole function
    game_id = request.json.get("game_id")
    game = db.execute("SELECT * FROM games WHERE game_id = ?", game_id)[0]
    users = game["player_ids"].split(",")
    handsStr = game["player_hands"]
    handsList = handsStr.split(";")
    protsStr = game["player_protecteds"]
    protsList = protsStr.split(";")
    deckStr = game["deck"]

    # verify that the current phase is the shift phase
    if game['phase'] != 'shift':
        return
    
    # verify that the user is player 1
    if int(user_id) != game["player_turn"]:
        return
    
    # New hands and protected cards variables
    newHands = handsStr
    newProtecteds = protsStr

    # Roll the shift
    shift = rollShift()

    if shift == True:

        # The amount of cards every player will need to draw due to the shift
        drawCounts = []

        # The cards that are preserved due to protection
        hCards = []

        # Iterate through every hand in the hands list
        for k in range(len(handsList)):

            # The amount of cards that will need to be drawn by this hand
            drawCount = 0

            # New hands and protected lists
            newHandList = handsList[k].split(",")
            newProtsList = protsList[k].split(",")

            # Iterate through protection list to check if each card is protected or not
            for p in range(len(protsList[k].split(","))):

                # If unprotected, it is lost and removed from the hand and protected list.
                if protsList[k].split(",")[p] == "0":
                    newHandList.remove(handsList[k].split(",")[p])
                    newProtsList.remove(protsList[k].split(",")[p])
                    # The player has to draw a card to replace this one
                    drawCount += 1
                # If protected, it is kept and put in the hCards list
                else:
                    hCards.append(handsList[k].split(",")[p])

            # Insert new hand and protected data into lists of all hands and protected cards
            newHands = strListMod(newHands, k, listToStr(newHandList), sep=";")
            newProtecteds = strListMod(newProtecteds, k, listToStr(newProtsList), sep=";")

            # Append the amount of cards that need to be drawn to the list
            drawCounts.append(drawCount)

        # Reshuffle the deck EXCEPT for cards that were protected
        deckStr = shuffleDeck(hCards)

        # Update hands and protecteds lists
        handsList = newHands.split(";")
        protsList = newProtecteds.split(";")

        # Iterate through every hand
        for i in range(len(handsList)):

            # Draw the correct amount of cards into each hand
            for c in range(drawCounts[i]):
                drawData = drawCard(deckStr)
                deckStr = drawData["deck"]
                newCard = drawData["card"]
                handsList[i] += "," + newCard
                handsList[i] = handsList[i].strip(",")
                newHands = listToStr(handsList, sep=";")

                # Add new card to protection list
                protsList[i] += ",0"
                protsList[i] = protsList[i].strip(",")
                newProtecteds = listToStr(protsList, sep=";")

    # Set the Shift message
    shiftStr = ""
    if shift == True:
        shiftStr = "Sabacc shift!"
    elif shift == False:
        shiftStr = "No shift!"

    # Update game
    db.execute(f"UPDATE games SET phase = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, shift = ?, p_act = ? WHERE game_id = {game_id}", "betting", deckStr, newHands, newProtecteds, int(users[0]), str(int(shift)), shiftStr)

@app.route("/cont", methods=["POST"])
@cross_origin()
def cont():

    """ Request to play again """

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

    # Set some variables for the whole function
    game_id = request.json.get("game_id")
    game = db.execute("SELECT * FROM games WHERE game_id = ?", game_id)[0]

    # Players' credits
    creditsStr = game["player_credits"]

    # Players
    users = game["player_ids"].split(",")

    if game["completed"] != True:
        return

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return
    
    # If any players folded throughout the game, bring them back in
    newPlayers = game["player_ids"]
    if game["folded_players"] != None:
        newPlayers += "," + game["folded_players"]

    # Remove any trailing commas
    newPlayers = newPlayers.strip(",")
    users = newPlayers.split(",")

    # Rotate "Dealer"
    users = shiftList(users)
    newPlayers = listToStr(users)

    # If any players folded throughout the game, bring their credits back in
    newCredits = creditsStr
    if game["folded_credits"] != None:
        newCredits += "," + game["folded_credits"]

    # Remove any trailing commas
    newCredits = newCredits.strip(",")
    creditsList = newCredits.split(",")

    # Rotate "Dealer" credits
    creditsList = shiftList(creditsList)
    newCredits = listToStr(creditsList)

    # Make users pay Sabacc and Hand pot Antes
    for c in creditsList:
        creditsList[creditsList.index(c)] = str(int(c) - 15)
    
    # Update credits variable
    newCredits = listToStr(creditsList)

    # Update pots
    hPot = 5 * len(users)
    sPot = game["sabacc_pot"] + (10 * len(users))

    # Protecteds
    prots = ""
    for i in range(len(users)):
        prots += "0,0;"

    # Remove trailing semicolons
    prots = prots.strip(";")

    # Bets
    pBets = ""
    for i in range(len(users) - 1):
        pBets += ","

    # Construct deck and hands
    deckData = constructDeck(len(users))
    deck = deckData["deck"]
    handsStr = listToStr(deckData["hands"], sep=";")

    # Create game in database
    db.execute(f"UPDATE games SET player_ids = ?, player_credits = ?, player_bets = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, folded_players = ?, folded_credits = ?, cycle_count = ?, p_act = ?, completed = ? WHERE game_id = {game_id}", newPlayers, newCredits, pBets, hPot, sPot, "betting", deck, handsStr, prots, int(users[0]), None, None, 0, "", str(int(False)))

    # Return game
    gata = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    return jsonify({"message": "Card!", "gata": gata}), 200



""" Old Socket Stuff - May be brought back in the future"""

@socketio.on("message", namespace="/chat")
def handleMessage(msg):

    """ GalactiChat """

    # Broadcast the recieved message to all chatters
    send(msg, broadcast=True)

@app.route("/chat")
@login_required
def chat():

    """Global Chat using Socket.IO"""

    # Tell the client what their username is
    user_id = session.get("user_id")
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}")[0]


    return render_template("chat.html", user=user)


@socketio.on("game", namespace="/game")
def game_connect():

    """ Establish Game Socket Connection """

    user_id = session.get("user_id")
    if not user_id:
        return
    sid = request.sid
    # users[user_id] = sid

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return str(e)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
