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
# from traditional.alderaanHelpers import *
import dbConversion
from socketio import Client
from flask_socketio import SocketIO, send, emit, join_room, rooms
import traditional.traditionalHelpers
from traditional.traditionalHelpers import TraditionalGame
import corellian_spike.corellianHelpers
from corellian_spike.corellianHelpers import CorellianSpikeGame
import kessel.kesselHelpers
from kessel.kesselHelpers import KesselGame
import yaml
import psycopg
from psycopg.types.composite import CompositeInfo, register_composite
import signal
from datetime import datetime

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

# links the socketio session to a users username and id
clientUserMap = {}

# Connect to postgresql database
conn = psycopg.connect(config['DATABASE'])
print(conn)

# Open a cursor to perform database operations
db = conn.cursor()

# Create users table
db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)")
conn.commit()

# create custom traditional types

# Create custom TraditionalSuit type
try:
    db.execute("CREATE TYPE TraditionalSuit AS ENUM ('flasks','sabers','staves','coins','negative/neutral');")
    conn.commit()
    print("Created custom PostgreSQL type TraditionalSuit")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type TraditionalSuit already exists")
    conn.rollback()

# Create custom TraditionalCard type
try:
    db.execute("CREATE TYPE TraditionalCard AS (val INTEGER, suit TraditionalSuit, protected BOOL);")
    conn.commit()
    print("Created custom PostgreSQL type TraditionalCard")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type TraditionalCard already exists")
    conn.rollback()

# Create custom TraditionalPlayer type
try:
    db.execute("""
        CREATE TYPE TraditionalPlayer AS (
        id INTEGER,
        username TEXT,
        credits INTEGER,
        bet INTEGER,
        hand TraditionalCard[],
        folded BOOL,
        lastAction TEXT);
    """)
    conn.commit()
    print("Created custom PostgreSQL type TraditionalPlayer")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type TraditionalPlayer already exists")
    conn.rollback()


# register Traditional custom types
traditional.traditionalHelpers.traditionalCardType = CompositeInfo.fetch(conn, 'traditionalcard')
traditional.traditionalHelpers.traditionalPlayerType = CompositeInfo.fetch(conn, 'traditionalplayer')
register_composite(traditional.traditionalHelpers.traditionalCardType, db)
register_composite(traditional.traditionalHelpers.traditionalPlayerType, db)
print("Registered Traditional custom types")

# create Traditional tables
db.execute("CREATE TABLE IF NOT EXISTS traditional_games (game_id SERIAL PRIMARY KEY, players TraditionalPlayer[], hand_pot INTEGER NOT NULL DEFAULT 0, sabacc_pot INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'betting', deck TraditionalCard[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, shift BOOL NOT NULL DEFAULT false, completed BOOL NOT NULL DEFAULT false, settings JSONB NOT NULL DEFAULT '{ \"PokerStyleBetting\" : false, \"SmallBlind\" : 1, \"BigBlind\" : 2, \"HandPotAnte\": 5, \"SabaccPotAnte\": 10, \"StartingCredits\" : 1000 }', created_at TIMESTAMPTZ DEFAULT NOW(), move_history JSONB[]);")
print("Created Traditional table")
conn.commit()

print()

# Create custom Corellian Spike types

# Create custom CorellianSpikeSuit type
try:
    db.execute("CREATE TYPE CorellianSpikeSuit AS ENUM('circle','square','triangle','sylop');")
    conn.commit()
    print("Created custom PostgreSQL type CorellianSpikeSuit")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type CorellianSpikeSuit already exists")
    conn.rollback()

# Create custom CorellianSpikeCard type
try:
    db.execute("CREATE TYPE CorellianSpikeCard AS (val INTEGER, suit CorellianSpikeSuit);")
    conn.commit()
    print("Created custom PostgreSQL type CorellianSpikeCard")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type CorellianSpikeCard already exists")
    conn.rollback()

# Create custom CorellianSpikePlayer type
try:
    db.execute("""
        CREATE TYPE CorellianSpikePlayer AS (
        id INTEGER,
        username TEXT,
        credits INTEGER,
        bet INTEGER,
        hand CorellianSpikeCard[],
        folded BOOL,
        lastAction TEXT);
    """)
    conn.commit()
    print("Created custom PostgreSQL type CorellianSpikePlayer")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type CorellianSpikePlayer already exists")
    conn.rollback()


# register CorellianSpike custom types
corellian_spike.corellianHelpers.corellianSpikeCardType = CompositeInfo.fetch(conn, 'corellianspikecard')
corellian_spike.corellianHelpers.corellianSpikePlayerType = CompositeInfo.fetch(conn, 'corellianspikeplayer')
register_composite(corellian_spike.corellianHelpers.corellianSpikeCardType, db)
register_composite(corellian_spike.corellianHelpers.corellianSpikePlayerType, db)
print("Registered CorellianSpike custom types")

# create CorellianSpike tables
db.execute("CREATE TABLE IF NOT EXISTS corellian_spike_games (game_id SERIAL PRIMARY KEY, players CorellianSpikePlayer[], hand_pot INTEGER NOT NULL DEFAULT 0, sabacc_pot INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'card', deck CorellianSpikeCard[], discard_pile CorellianSpikeCard[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, shift BOOL NOT NULL DEFAULT false, completed BOOL NOT NULL DEFAULT false, settings JSONB NOT NULL DEFAULT '{ \"PokerStyleBetting\" : false, \"SmallBlind\" : 1, \"BigBlind\" : 2, \"HandPotAnte\": 5, \"SabaccPotAnte\": 10, \"StartingCredits\": 1000, \"HandRanking\": \"Wayne\", \"DeckDrawCost\": 5, \"DiscardDrawCost\": 10, \"DeckTradeCost\": 10, \"DiscardTradeCost\": 15, \"DiscardCosts\": [15, 20, 25] }', created_at TIMESTAMPTZ DEFAULT NOW(), move_history JSONB[]);")
print("Created CorellianSpike table")
conn.commit()

# Create custom Kessel types

# Create custom KesselShiftToken type
try:
    db.execute("CREATE TYPE KesselShiftToken AS ENUM('freeDraw', 'refund', 'extraRefund', 'embezzlement', 'majorFraud', 'generalTariff', 'targetTariff', 'generalAudit', 'immunity', 'exhaustion', 'directTransaction', 'embargo');")
    conn.commit()
    print("Created custom PostgreSQL type KesselShiftToken")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type KesselShiftToken already exists")
    conn.rollback()

# Create custom KesselSuit type
try:
    db.execute("CREATE TYPE KesselSuit AS ENUM('imposter', 'basic', 'sylop');")
    conn.commit()
    print("Created custom PostgreSQL type KesselSuit")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type KesselSuit already exists")
    conn.rollback()

# Create custom KesselCard type
try:
    db.execute("CREATE TYPE KesselCard AS (val INTEGER, suit KesselSuit);")
    conn.commit()
    print("Created custom PostgreSQL type KesselCard")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type KesselCard already exists")
    conn.rollback()

# Create custom KesselPlayer type
try:
    db.execute("""
        CREATE TYPE KesselPlayer AS (
        id INTEGER,
        username TEXT,
        chips INTEGER,
        usedChips INTEGER,
        positiveCard KesselCard,
        negativeCard KesselCard,
        shiftTokens KesselShiftToken[],
        outOfGame BOOL,
        lastAction TEXT);
    """)
    conn.commit()
    print("Created custom PostgreSQL type KesselPlayer")
except psycopg.errors.DuplicateObject:
    print("Custom PostgreSQL type KesselPlayer already exists")
    conn.rollback()


# register Kessel custom types
kessel.kesselHelpers.kesselShiftTokenType = CompositeInfo.fetch(conn, 'kesselshifttoken')
kessel.kesselHelpers.kesselCardType = CompositeInfo.fetch(conn, 'kesselcard')
kessel.kesselHelpers.kesselPlayerType = CompositeInfo.fetch(conn, 'kesselplayer')
register_composite(kessel.kesselHelpers.kesselShiftTokenType, db)
register_composite(kessel.kesselHelpers.kesselCardType, db)
register_composite(kessel.kesselHelpers.kesselPlayerType, db)

print("Registered Kessel custom types")

# create Kessel tables
db.execute("CREATE TABLE IF NOT EXISTS kessel_games (game_id SERIAL PRIMARY KEY, players KesselPlayer[], phase TEXT NOT NULL DEFAULT 'shiftTokenSelect', dice INTEGER[2] NOT NULL DEFAULT '{ 1, 1 }', positiveDeck KesselCard[], negativeDeck KesselCard[], positiveDiscard KesselCard[], negativeDiscard KesselCard[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, completed BOOL NOT NULL DEFAULT false, settings JSONB NOT NULL DEFAULT '{ \"startingChips\" : 8 }', created_at TIMESTAMPTZ DEFAULT NOW(), move_history JSONB[]);")
print("Created Kessel table")
conn.commit()

""" DB Conversions: """

""" copy over sqlite3 data """ # Uncomment to run - DO NOT DELETE
# dbConversion.convertSqliteToPsql(db=db, card_type=traditional.traditionalHelpers.traditionalCardType, player_type=traditional.traditionalHelpers.traditionalPlayerType)
# conn.commit()

""" transfer traditional games data from games to traditional_games table """ # Uncomment to run - DO NOT DELETE
""" when using this, types in table must be traditional types, not generic types """
# dbConversion.transferTraditionalGames(db, traditional.traditionalHelpers.traditionalCardType, traditional.traditionalHelpers.traditionalPlayerType)
# conn.commit()

""" transfer old games which did not have settings or timestamps to new tables """ # Uncomment to run - DO NOT DELETE
# dbConversion.convertPreSettingsToPostSettings(db, traditional.traditionalHelpers.traditionalCardType, traditional.traditionalHelpers.traditionalPlayerType, corellian_spike.corellianHelpers.corellianSpikeCardType, corellian_spike.corellianHelpers.corellianSpikePlayerType)
# conn.commit()

""" convert games created_at columns from TIMESTAMP to TIMESTAMPTZ """ # Uncomment to run - DO NOT DELETE
# dbConversion.convertDBToTimestamptz(db, alterTables=True)
# conn.commit()

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
        print(f'error was here, {check}')
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
    #     db.execute(f"UPDATE users SET hash = %s WHERE username = %s", passHash, username)

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
    db.execute("SELECT id FROM users WHERE username = %s", [username])
    user_id = getDictsForDB(db)[0]["id"]

    traditionalPlayerTurnUsernames = []

    # Query the database for all the Traditional games
    allTraditionalGames = [TraditionalGame.fromDb(game) for game in db.execute("SELECT * FROM traditional_games").fetchall()]
    traditionalGames = []

    # Remove games that have been completed and that are not relevant to the player
    for game in allTraditionalGames:
        if game.containsPlayer(id=user_id):
            traditionalGames.append(game)
            traditionalPlayerTurnUsernames.append(game.getPlayer(id=game.player_turn).username)

    corellianSpikePlayerTurnUsernames = []

    # Query the database for all the CorellianSpike games
    allCorellianSpikeGames = [CorellianSpikeGame.fromDb(game) for game in db.execute("SELECT * FROM corellian_spike_games").fetchall()]
    corellianSpikeGames = []

    # Remove games that have been completed and that are not relevant to the player
    for game in allCorellianSpikeGames:
        if game.containsPlayer(id=user_id):
            corellianSpikeGames.append(game)
            corellianSpikePlayerTurnUsernames.append(game.getPlayer(id=game.player_turn).username)


    # Return data
    return jsonify({
        "traditional_games": [game.toDict() for game in traditionalGames],
        "traditional_player_turn_usernames": traditionalPlayerTurnUsernames,
        "corellian_spike_games": [game.toDict() for game in corellianSpikeGames],
        "corellian_spike_player_turn_usernames": corellianSpikePlayerTurnUsernames
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
    if db.execute("SELECT * FROM users WHERE username = %s", [username]).fetchall() != []:
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
    db.execute("INSERT INTO users (username, hash) VALUES(%s, %s)", [username, str(passHash)])
    conn.commit()

    # Redirect user to home page
    return jsonify({"message": "Registered!"}), 200

def getGameFromDb(game_variant, game_id):
    if game_variant == 'traditional':
        return TraditionalGame.fromDb(db.execute("SELECT * FROM traditional_games WHERE game_id = %s", [int(game_id)]).fetchall()[0])
    elif game_variant == 'corellian_spike':
        return CorellianSpikeGame.fromDb(db.execute("SELECT * FROM corellian_spike_games WHERE game_id = %s", [int(game_id)]).fetchall()[0])
    elif game_variant == 'kessel':
        return KesselGame.fromDb(db.execute("SELECT * FROM kessel_games WHERE game_id = %s", [int(game_id)]).fetchall()[0])
    else:
        return None

# this is caled manually by clients when they first open the page, and it sends the game information only to them, aswell as joining them into a room
@socketio.on('getGame')
def getGameClientInfo(clientInfo):
    user_id = -1
    if clientInfo["username"] != "":
        db.execute("SELECT id FROM users WHERE username = %s", [clientInfo["username"]])
        user_id = getDictsForDB(db)[0]["id"]

    game_id = clientInfo['game_id']
    game_variant = clientInfo['game_variant']
    join_room(room=f'gameRoom:{game_variant}/{game_id}')

    clientUserMap[request.sid] = (user_id, clientInfo["username"])
    game = getGameFromDb(game_variant, game_id)
    # print(game.getClientData(user_id, clientInfo["username"]))

    emit('clientUpdate', game.getClientData(user_id, clientInfo["username"]))

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
    db.execute("SELECT id FROM users WHERE username = %s", [username])
    user_id = getDictsForDB(db)[0]["id"]

    # Get list of players in the game
    formPlayers = request.json.get("players")

    game_variant = request.json.get("game_variant")

    # Make list of players
    playerIds = [user_id]
    playerUsernames = [username]

    # Ensure each submitted player is valid
    for pForm in formPlayers:
        if pForm != "":
            db.execute("SELECT * FROM users WHERE username = %s", [pForm])
            p = getDictsForDB(db)
            if len(p) == 0:
                return jsonify({"message": f"Player {pForm} does not exist"}), 401
            if str(p[0]["id"]) == str(user_id):
                return jsonify({"message": "You cannot play with yourself"}), 401
            if p[0]["id"] in playerIds:
                return jsonify({"message": "All players must be different"}), 401

            playerIds.append(p[0]["id"])
            playerUsernames.append(p[0]["username"])


    game = None

    if not game_variant in ('traditional', 'corellian_spike', 'kessel'):
        return jsonify({"message": "Invalid game variant"}), 401

    # Create new game
    if game_variant == "traditional":
        game = TraditionalGame.newGame(playerIds=playerIds, playerUsernames=playerUsernames, db=db, settings=request.json.get("settings"))
    elif game_variant == "corellian_spike":
        game = CorellianSpikeGame.newGame(playerIds=playerIds, playerUsernames=playerUsernames, db=db, settings=request.json.get("settings"))
    elif game_variant == "kessel":
        game = KesselGame.newGame(playerIds=playerIds, playerUsernames=playerUsernames, db=db, settings=request.json.get("settings"))

    if not game:
        return jsonify({"message": "Invalid game variant"}), 401

    if type(game) == str:
        return jsonify({"message": game}), 401

    # Create game in database
    conn.commit()

    print(game_variant)

    # Get game ID
    game_id = db.execute(f"SELECT game_id FROM {game_variant}_games ORDER BY game_id DESC").fetchone()[0]

    # Redirect user to game
    return jsonify({"message": "Game hosted!", "redirect": f"/game/{game_variant.replace('_', '-')}/{game_id}"}), 200

""" Gameplay REST APIs """

@socketio.on("gameAction")
def gameAction(clientInfo):
    """ Perform an action in a game """

    # Authenticate User
    username = clientInfo["username"]
    password = clientInfo["password"]
    check = checkLogin(username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    user_id = db.execute("SELECT id FROM users WHERE username = %s", [username]).fetchone()

    if not user_id:
        return jsonify({"message": "User does not exist"}), 401

    # Get game info
    game_variant = clientInfo["game_variant"]
    game_id = clientInfo["game_id"]

    game = getGameFromDb(game_variant, game_id)

    if not game.getPlayer(username=username):
        return jsonify({"message": "You are not in this game"}), 401

    response = game.action(clientInfo, db)

    if isinstance(response, str):
        return jsonify({"message": response}), 401

    conn.commit()

    game = getGameFromDb(game_variant, game_id)
    clients = socketio.server.manager.get_participants("/", f'gameRoom:{game_variant}/{game_id}')
    for i in clients:
        emit('gameUpdate', game.getClientData(clientUserMap[i[0]][0]), to=i[0])

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
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchall()[0]


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

# cleanup code
def handle_sigint(signum, frame):
    print("\nCleaning up resources before shutdown...")

    # close db connection
    conn.close()

    # After cleanup, raise KeyboardInterrupt to allow the normal exit process
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_sigint)
