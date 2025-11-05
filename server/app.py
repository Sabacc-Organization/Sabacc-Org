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
from datetime import datetime, timedelta
import json

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

# important variable to make sure psql doesn't get used
usingPsql = False



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

""" convert PSQL data to sqlite3 """ # Uncomment to run - DO NOT DELETE
# import dbConversion.dbConversion as dbConversion
# psql_conn = psycopg.connect(config['PSQL_DATABASE'])

# usingPsql = True

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

@app.route("/stats", methods=["POST"])
@cross_origin()
def stats():
    """ Get game statistics """
    
    db = conn.cursor()
    
    # Get total number of games for each type
    traditional_total = db.execute("SELECT COUNT(*) FROM traditional_games").fetchone()[0]
    corellian_spike_total = db.execute("SELECT COUNT(*) FROM corellian_spike_games").fetchone()[0]
    kessel_total = db.execute("SELECT COUNT(*) FROM kessel_games").fetchone()[0]
    
    # Get number of completed games
    traditional_completed = db.execute("SELECT COUNT(*) FROM traditional_games WHERE completed = 1").fetchone()[0]
    corellian_spike_completed = db.execute("SELECT COUNT(*) FROM corellian_spike_games WHERE completed = 1").fetchone()[0]
    kessel_completed = db.execute("SELECT COUNT(*) FROM kessel_games WHERE completed = 1").fetchone()[0]
    
    # Get number of active games
    traditional_active = traditional_total - traditional_completed
    corellian_spike_active = corellian_spike_total - corellian_spike_completed
    kessel_active = kessel_total - kessel_completed
    
    # Get total number of unique players
    total_players = db.execute("SELECT COUNT(DISTINCT id) FROM users").fetchone()[0]
    
    # Calculate overall stats
    total_games = traditional_total + corellian_spike_total + kessel_total
    total_completed = traditional_completed + corellian_spike_completed + kessel_completed
    total_active = total_games - total_completed
    
    # Calculate average players per game for each type
    def calculate_avg_players(table_name):
        games = db.execute(f"SELECT players FROM {table_name}").fetchall()
        if not games:
            return 0
        total_players = 0
        for game in games:
            try:
                players_data = json.loads(game[0])
                total_players += len(players_data)
            except:
                continue
        return round(total_players / len(games), 1) if games else 0
    
    traditional_avg_players = calculate_avg_players("traditional_games")
    corellian_avg_players = calculate_avg_players("corellian_spike_games")
    kessel_avg_players = calculate_avg_players("kessel_games")
    
    # Calculate average moves per game for each type (only for games with move_history)
    def calculate_avg_moves(table_name):
        games = db.execute(f"SELECT move_history FROM {table_name} WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchall()
        if not games:
            return 0
        total_moves = 0
        valid_games = 0
        for game in games:
            try:
                moves = json.loads(game[0])
                if moves and len(moves) > 0:
                    total_moves += len(moves)
                    valid_games += 1
            except:
                continue
        return round(total_moves / valid_games, 1) if valid_games > 0 else 0
    
    traditional_avg_moves = calculate_avg_moves("traditional_games")
    corellian_avg_moves = calculate_avg_moves("corellian_spike_games")
    kessel_avg_moves = calculate_avg_moves("kessel_games")
    
    # Calculate overall averages
    overall_avg_players = round((traditional_avg_players * traditional_total + 
                                corellian_avg_players * corellian_spike_total + 
                                kessel_avg_players * kessel_total) / total_games, 1) if total_games > 0 else 0
    
    # For overall average moves, we need to count games with history across all types
    total_games_with_history = (
        db.execute("SELECT COUNT(*) FROM traditional_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0] +
        db.execute("SELECT COUNT(*) FROM corellian_spike_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0] +
        db.execute("SELECT COUNT(*) FROM kessel_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0]
    )
    
    overall_avg_moves = round((traditional_avg_moves * db.execute("SELECT COUNT(*) FROM traditional_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0] +
                              corellian_avg_moves * db.execute("SELECT COUNT(*) FROM corellian_spike_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0] +
                              kessel_avg_moves * db.execute("SELECT COUNT(*) FROM kessel_games WHERE move_history IS NOT NULL AND move_history != '[]' AND move_history != ''").fetchone()[0]) / 
                              total_games_with_history, 1) if total_games_with_history > 0 else 0
    
    # Get recent game activity (games created in the last week)
    one_week_ago = datetime.now() - timedelta(days=7)
    one_month_ago = datetime.now() - timedelta(days=30)
    
    # Recent traditional games
    recent_traditional_week = db.execute(
        "SELECT COUNT(*) FROM traditional_games WHERE datetime(created_at) > datetime(?)", 
        [one_week_ago.isoformat()]
    ).fetchone()[0]
    
    recent_traditional_month = db.execute(
        "SELECT COUNT(*) FROM traditional_games WHERE datetime(created_at) > datetime(?)", 
        [one_month_ago.isoformat()]
    ).fetchone()[0]
    
    # Recent corellian spike games
    recent_corellian_week = db.execute(
        "SELECT COUNT(*) FROM corellian_spike_games WHERE datetime(created_at) > datetime(?)", 
        [one_week_ago.isoformat()]
    ).fetchone()[0]
    
    recent_corellian_month = db.execute(
        "SELECT COUNT(*) FROM corellian_spike_games WHERE datetime(created_at) > datetime(?)", 
        [one_month_ago.isoformat()]
    ).fetchone()[0]
    
    # Recent kessel games  
    recent_kessel_week = db.execute(
        "SELECT COUNT(*) FROM kessel_games WHERE datetime(created_at) > datetime(?)", 
        [one_week_ago.isoformat()]
    ).fetchone()[0]
    
    recent_kessel_month = db.execute(
        "SELECT COUNT(*) FROM kessel_games WHERE datetime(created_at) > datetime(?)", 
        [one_month_ago.isoformat()]
    ).fetchone()[0]
    
    games_this_week = recent_traditional_week + recent_corellian_week + recent_kessel_week
    games_this_month = recent_traditional_month + recent_corellian_month + recent_kessel_month
    
    # Get time series data based on selected time range
    def get_time_series_data(table_name, time_range):
        if time_range == "week":
            return get_daily_game_counts(table_name, 7)
        elif time_range == "month":
            return get_daily_game_counts(table_name, 30)
        elif time_range == "year":
            return get_monthly_game_counts(table_name, 12)
        elif time_range == "lifetime":
            return get_monthly_game_counts_lifetime(table_name)
        else:
            return get_daily_game_counts(table_name, 30)
    
    def get_daily_game_counts(table_name, days):
        daily_counts = {}
        for i in range(days):
            day = datetime.now() - timedelta(days=(days - 1 - i))
            day_str = day.strftime('%Y-%m-%d')
            next_day = day + timedelta(days=1)
            next_day_str = next_day.strftime('%Y-%m-%d')
            
            count = db.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE date(created_at) >= date(?) AND date(created_at) < date(?)",
                [day_str, next_day_str]
            ).fetchone()[0]
            
            daily_counts[day_str] = count
        return daily_counts
    
    def get_monthly_game_counts(table_name, months):
        monthly_counts = {}
        for i in range(months):
            # Calculate the first day of the month
            current_date = datetime.now().replace(day=1)
            target_month = current_date - timedelta(days=32 * (months - 1 - i))
            month_start = target_month.replace(day=1)
            
            # Calculate the first day of next month
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            month_str = month_start.strftime('%Y-%m')
            
            count = db.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE date(created_at) >= date(?) AND date(created_at) < date(?)",
                [month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')]
            ).fetchone()[0]
            
            monthly_counts[month_str] = count
        return monthly_counts
    
    def get_monthly_game_counts_lifetime(table_name):
        # Get the earliest game creation date
        earliest_result = db.execute(f"SELECT MIN(created_at) FROM {table_name}").fetchone()
        if not earliest_result[0]:
            return {}
        
        earliest_date = datetime.fromisoformat(earliest_result[0].replace('Z', '+00:00')).replace(tzinfo=None)
        earliest_month = earliest_date.replace(day=1)
        current_month = datetime.now().replace(day=1)
        
        monthly_counts = {}
        current = earliest_month
        
        while current <= current_month:
            # Calculate the first day of next month
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1)
            else:
                next_month = current.replace(month=current.month + 1)
            
            month_str = current.strftime('%Y-%m')
            
            count = db.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE date(created_at) >= date(?) AND date(created_at) < date(?)",
                [current.strftime('%Y-%m-%d'), next_month.strftime('%Y-%m-%d')]
            ).fetchone()[0]
            
            monthly_counts[month_str] = count
            current = next_month
            
        return monthly_counts
    
    # Get time series data for all time ranges
    def create_time_series_for_range(time_range):
        traditional_series = get_time_series_data("traditional_games", time_range)
        corellian_series = get_time_series_data("corellian_spike_games", time_range)
        kessel_series = get_time_series_data("kessel_games", time_range)
        
        # Calculate total counts for each time period
        dates = list(traditional_series.keys())
        total_series = {}
        for date in dates:
            total_series[date] = (traditional_series.get(date, 0) + 
                                 corellian_series.get(date, 0) + 
                                 kessel_series.get(date, 0))
        
        return {
            "dates": dates,
            "traditional": list(traditional_series.values()),
            "corellianSpike": list(corellian_series.values()),
            "kessel": list(kessel_series.values()),
            "total": list(total_series.values())
        }
    
    # Create time series data for all time ranges
    time_series_data = {
        "week": create_time_series_for_range("week"),
        "month": create_time_series_for_range("month"),
        "year": create_time_series_for_range("year"),
        "lifetime": create_time_series_for_range("lifetime")
    }
    
    return jsonify({
        "totalGames": total_games,
        "gamesCompleted": total_completed,
        "completionRate": round((total_completed / total_games * 100) if total_games > 0 else 0, 1),
        "avgPlayersPerGame": overall_avg_players,
        "avgMovesPerGame": overall_avg_moves,
        "traditionalGames": traditional_total,
        "traditionalCompleted": traditional_completed,
        "traditionalCompletionRate": round((traditional_completed / traditional_total * 100) if traditional_total > 0 else 0, 1),
        "traditionalAvgPlayers": traditional_avg_players,
        "traditionalAvgMoves": traditional_avg_moves,
        "corellianSpikeGames": corellian_spike_total,
        "corellianSpikeCompleted": corellian_spike_completed,
        "corellianSpikeCompletionRate": round((corellian_spike_completed / corellian_spike_total * 100) if corellian_spike_total > 0 else 0, 1),
        "corellianSpikeAvgPlayers": corellian_avg_players,
        "corellianSpikeAvgMoves": corellian_avg_moves,
        "kesselGames": kessel_total,
        "kesselCompleted": kessel_completed,
        "kesselCompletionRate": round((kessel_completed / kessel_total * 100) if kessel_total > 0 else 0, 1),
        "kesselAvgPlayers": kessel_avg_players,
        "kesselAvgMoves": kessel_avg_moves,
        "activeGames": total_active,
        "gamesThisWeek": games_this_week,
        "gamesThisMonth": games_this_month,
        "totalPlayers": total_players,
        "timeSeriesData": time_series_data
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
    if usingPsql:
        psql_conn.close()

    # After cleanup, raise KeyboardInterrupt to allow the normal exit process
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_sigint)
