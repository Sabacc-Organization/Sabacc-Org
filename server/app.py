""" app.py - Handles all requests to the backend """

# Import Libraries
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
import dbConversion.dbConversion as dbConversion
from socketio import Client
from flask_socketio import SocketIO, send, emit, join_room, rooms
from traditional.traditionalHelpers import TraditionalGame
from corellian_spike.corellianHelpers import CorellianSpikeGame
from kessel.kesselHelpers import KesselGame
import yaml
import psycopg
import sqlite3
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
conn = sqlite3.connect(config['DATABASE'], check_same_thread=False)
print(conn)


psql_conn = psycopg.connect(config['PSQL_DATABASE'])

# Open a cursor to perform database operations
sqlite_db = conn.cursor()

# Make sure all tables exist in the db
query = ""
with open('schema.sql', 'r') as f:
    query = f.read()

# Execute the query
sqlite_db.executescript(query)
conn.commit()
# conn.close()

# dbConversion.convertPsqlToSqlite(sqlite_db, psql_conn)
# conn.commit()

# psql_db = psql_conn.cursor()

# from dbConversion.psql_helpers.psql_traditionalHelpers import TraditionalGame as psql_TraditionalGame
# from dbConversion.psql_helpers.psql_corellianHelpers import CorellianSpikeGame as psql_CorellianSpikeGame
# from dbConversion.psql_helpers.psql_kesselHelpers import KesselGame as psql_KesselGame

# # register Traditional custom types
# traditionalCardType = CompositeInfo.fetch(psql_conn, 'traditionalcard')
# traditionalPlayerType = CompositeInfo.fetch(psql_conn, 'traditionalplayer')
# register_composite(traditionalCardType, psql_db)
# register_composite(traditionalPlayerType, psql_db)

# print("Registered Traditional custom types")

# # register Corellian custom types
# corellianSpikeCardType = CompositeInfo.fetch(psql_conn, 'corellianspikecard')
# corellianSpikePlayerType = CompositeInfo.fetch(psql_conn, 'corellianspikeplayer')
# register_composite(corellianSpikeCardType, psql_db)
# register_composite(corellianSpikePlayerType, psql_db)

# print("Registered Corellian custom types")

# # register Kessel custom types
# kesselCardType = CompositeInfo.fetch(psql_conn, 'kesselcard')
# kesselPlayerType = CompositeInfo.fetch(psql_conn, 'kesselplayer')
# register_composite(kesselCardType, psql_db)
# register_composite(kesselPlayerType, psql_db)

# print("Registered Kessel custom types")

# psql_users = psql_db.execute("SELECT username, hash FROM users ORDER BY id ASC").fetchall()
# for user in psql_users:
#     sqlite_db.execute("INSERT INTO users (username, hash, created_at) VALUES (?, ?, ?)", [user[0], user[1], None])

# print("Users copied over")

# psql_traditionalGames = psql_db.execute("SELECT * FROM traditional_games ORDER BY game_id ASC").fetchall()
# psql_corellianSpikeGames = psql_db.execute("SELECT * FROM corellian_spike_games ORDER BY game_id ASC").fetchall()
# psql_kesselGames = psql_db.execute("SELECT * FROM kessel_games ORDER BY game_id ASC").fetchall()

# for game in psql_traditionalGames:
#     dbGame = TraditionalGame.fromDict(psql_TraditionalGame.fromDb(game).toDict()).toDb(includeId=False)
#     sqlite_db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

# for game in psql_corellianSpikeGames:
#     dbGame = CorellianSpikeGame.fromDict(psql_CorellianSpikeGame.fromDb(game).toDict()).toDb(includeId=False)
#     sqlite_db.execute("INSERT INTO corellian_spike_games (players, hand_pot, sabacc_pot, phase, deck, discard_pile, player_turn, p_act, cycle_count, shift, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

# for game in psql_kesselGames:
#     dbGame = KesselGame.fromDict(psql_KesselGame.fromDb(game).toDict()).toDb(includeId=False)
#     sqlite_db.execute("INSERT INTO kessel_games (players, phase, dice, positivedeck, negativedeck, positivediscard, negativediscard, activeshifttokens, player_turn, p_act, cycle_count, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

# print("Games copied over")

# conn.commit()

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

    db = conn.cursor()

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(db, username, password)
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

    db = conn.cursor()

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(db, username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get the user's id for later use
    db.execute("SELECT id FROM users WHERE username = ?", [username])
    user_id = getDictsForDB(db)[0]["id"]

    traditionalPlayerTurnUsernames = []

    # Query the database for all the Traditional games
    allTraditionalGames = [TraditionalGame.fromDb(game) for game in db.execute("SELECT * FROM traditional_games").fetchall()]
    traditionalGames = []

    # Remove games that are not relevant to the player
    for game in allTraditionalGames:
        if game.containsPlayer(id=user_id):
            traditionalGames.append(game)
            traditionalPlayerTurnUsernames.append(game.getPlayer(id=game.player_turn).username)

    corellianSpikePlayerTurnUsernames = []

    # Query the database for all the CorellianSpike games
    allCorellianSpikeGames = [CorellianSpikeGame.fromDb(game) for game in db.execute("SELECT * FROM corellian_spike_games").fetchall()]
    corellianSpikeGames = []

    # Remove games that are not relevant to the player
    for game in allCorellianSpikeGames:
        if game.containsPlayer(id=user_id):
            corellianSpikeGames.append(game)
            corellianSpikePlayerTurnUsernames.append(game.getPlayer(id=game.player_turn).username)

    kesselPlayerTurnUsernames = []
    print("made it")
    # Query the database for all the Kessel games
    allKesselGames = [KesselGame.fromDb(game) for game in db.execute("SELECT * FROM kessel_games").fetchall()]
    kesselGames = []

    # Remove games that are not relevant to the player
    for game in allKesselGames:
        if game.containsPlayer(id=user_id):
            kesselGames.append(game)
            kesselPlayerTurnUsernames.append(game.getPlayer(id=game.player_turn).username)

    # Return data
    return jsonify({
        "traditional_games": [game.toDict() for game in traditionalGames],
        "traditional_player_turn_usernames": traditionalPlayerTurnUsernames,
        "corellian_spike_games": [game.toDict() for game in corellianSpikeGames],
        "corellian_spike_player_turn_usernames": corellianSpikePlayerTurnUsernames,
        "kessel_games": [game.toDict() for game in kesselGames],
        "kessel_player_turn_usernames": kesselPlayerTurnUsernames
        }), 200

@app.route("/register", methods=["POST"])
@cross_origin()
def register():
    """Register user"""

    db = conn.cursor()

    # Ensure username was submitted
    username = request.json.get("username")
    if not username:
        return jsonify({"message": "Must provide username"}), 401

    if " " in username:
        return jsonify({"message": "Please do not put spaces in your username"}), 401

    # Check that username has not already been taken
    if db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall() != []:
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
    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", [username, str(passHash)])
    conn.commit()

    # Redirect user to home page
    return jsonify({"message": "Registered!"}), 200

def getGameFromDb(game_variant, game_id):

    db = conn.cursor()

    if game_variant == 'traditional':
        return TraditionalGame.fromDb(db.execute("SELECT * FROM traditional_games WHERE game_id = ?", [int(game_id)]).fetchall()[0])
    elif game_variant == 'corellian_spike':
        return CorellianSpikeGame.fromDb(db.execute("SELECT * FROM corellian_spike_games WHERE game_id = ?", [int(game_id)]).fetchall()[0])
    elif game_variant == 'kessel':
        return KesselGame.fromDb(db.execute("SELECT * FROM kessel_games WHERE game_id = ?", [int(game_id)]).fetchall()[0])
    else:
        return None

# this is caled manually by clients when they first open the page, and it sends the game information only to them, aswell as joining them into a room
@socketio.on('getGame')
def getGameClientInfo(clientInfo):

    db = conn.cursor()

    user_id = -1
    if clientInfo["username"] != "":
        db.execute("SELECT id FROM users WHERE username = ?", [clientInfo["username"]])
        user_id = getDictsForDB(db)[0]["id"]

    game_id = clientInfo['game_id']
    game_variant = clientInfo['game_variant']
    join_room(room=f'gameRoom:{game_variant}/{game_id}')

    clientUserMap[request.sid] = (user_id, clientInfo["username"])
    game = getGameFromDb(game_variant, game_id)
    # print(game.getClientData(user_id, clientInfo["username"]))

    emit('clientUpdate', game.getClientData(user_id, username=clientInfo["username"]))

@app.route("/host", methods=["POST"])
@cross_origin()
def host():
    """ Make a new game of Sabacc """

    db = conn.cursor()

    # Authenticate User
    username = request.json.get("username")
    password = request.json.get("password")
    check = checkLogin(db, username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    # Get User ID
    db.execute("SELECT id FROM users WHERE username = ?", [username])
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
            db.execute("SELECT * FROM users WHERE username = ?", [pForm])
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

    db = conn.cursor()

    # Authenticate User
    username = clientInfo["username"]
    password = clientInfo["password"]
    check = checkLogin(db, username, password)
    if check["status"] != 200:
        return jsonify({"message": check["message"]}), check["status"]

    user_id = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchone()

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

    db = conn.cursor()

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
    psql_conn.close()

    # After cleanup, raise KeyboardInterrupt to allow the normal exit process
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_sigint)
