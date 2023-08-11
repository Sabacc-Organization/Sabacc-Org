from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import ImmutableMultiDict
from helpers import *
from dataHelpers import *
from flask_socketio import SocketIO, send, emit
import yaml

# Get config.yaml data
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

# Socket.IO message links
link = config["DOMAIN"]
linkTwo = config["DOMAINTWO"]
socketio = SocketIO(app, cors_allowed_origins=[link, f"{link}/chat", f"{link}/game", f"{link}/bet", f"{link}/card", f"{link}/shift", f"{link}/protect", f"{link}/cont", linkTwo, f"{linkTwo}/chat", f"{linkTwo}/game", f"{linkTwo}/bet", f"{linkTwo}/card", f"{linkTwo}/shift", f"{linkTwo}/protect", f"{linkTwo}/cont"])

# Declare dictionary to store key-value pairs of user ids and session ids
users = {}

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///sabacc.db")


@app.route("/")
def index():
    """Show home page"""

    # Get the user's id for later use
    user_id = session.get("user_id")

    games = db.execute("SELECT * FROM games")
    newGames = games.copy()
    user_ids = []
    player_turns = []
    for game in games:
        if str(user_id) not in game["player_ids"].split(","):
            newGames.remove(game)

        else:
            user_ids.append(game["player_ids"].split(","))
            player_turns.append(db.execute("SELECT username FROM users WHERE id = ?", game["player_turn"])[0]["username"])


    usernames = []
    for set in user_ids:
        s = ""
        for user in set:
            s += str(db.execute("SELECT * FROM users WHERE id = ?", int(user))[0]["username"]) + ", "

        st = s.strip(", ")

        usernames.append(st)

    # Render the home page with the user's active game data
    return render_template("index.html", games=newGames, usernames=usernames, gamesLen=len(newGames), player_turns=player_turns)


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

        # Make list of players
        players = []
        players.append(session.get("user_id"))

        pForm = request.form.getlist("player2")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player3")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player4")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player5")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player6")[0]

        if pForm:
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player7")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
            players.append(p[0]["id"])

        pForm = request.form.getlist("player8")[0]

        if pForm != "":
            p = db.execute(f"SELECT * FROM users WHERE username = ?", pForm)
            if len(p) == 0:
                return apology(f"Player {pForm} does not exist")
            if str(p[0]["id"]) == str(session.get("user_id")):
                return apology("You cannot play with yourself")
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
        db.execute("INSERT INTO games (player_ids, player_credits, player_bets, hand_pot, sabacc_pot, deck, player_hands, player_protecteds, player_turn) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", playersStr, creditsStr, pBets, hPot, sPot, deck, handsStr, prots, session.get("user_id"))

        # Get game ID
        game_id = db.execute("SELECT game_id FROM games WHERE player_ids = ? ORDER BY game_id DESC", playersStr)[0]["game_id"]

        return redirect(f"/game/{game_id}")


@socketio.on("game", namespace="/game")
def game_connect():
    user_id = session.get("user_id")
    if not user_id:
        return
    sid = request.sid
    users[user_id] = sid

@socketio.on("protect", namespace="/protect")
def protect(data):

    # Set some variables for the whole function
    game_id = data["game_id"]
    protect = data["protect"]
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    user_id = session.get("user_id")
    uDex = game["player_ids"].split(",").index(str(user_id))
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
        return
    
    # Card is confirmed to be in hand


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
    db.execute(f"UPDATE games SET player_protecteds = ? WHERE game_id = {game_id}", protAllStr)

    # Force Reload players
    data = {
        "cmd": "reload",
        "g_id": game_id
    }
    send(data, broadcast=True)

@socketio.on("bet", namespace="/bet")
def bet(data):

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    amount = 0
    try:
        amount = data["amount"]
    except KeyError:
        pass
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    creditsStr = game["player_credits"]
    betsStr = game["player_bets"]
    users = game["player_ids"].split(",")
    user_id = session.get("user_id")
    u_dex = users.index(str(user_id))

    endRound = False
    foldEnd = False

    if game["phase"] != "betting":
        return

    player = ""
    if users.index(str(user_id)) == 0:
        player = "player1"

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return

    # If player 1 bets or checks
    if action == "bet" and player == "player1":

        pCredits = int(strListRead(creditsStr, 0))
        newCredits = strListMod(creditsStr, 0, pCredits - amount)

        newBets = strListMod(betsStr, 0, amount)

        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[1]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "call":

        pCredits = int(strListRead(creditsStr, u_dex))
        newCredits = strListMod(creditsStr, u_dex, pCredits - amount)

        newBets = strListMod(betsStr, u_dex, amount + readIntValStrList(betsStr, u_dex))

        nextPlayer = u_dex + 1

        if str(user_id) == users[len(users) - 1]:
            endRound = True


        if endRound == False and readIntValStrList(newBets, nextPlayer) == readIntValStrList(newBets, u_dex):

            if nextPlayer == len(users) - 1:
                endRound = True

            nextPlayer += 1

        if endRound == True:
            nextPlayer = 0

        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "raise":

        pCredits = int(strListRead(creditsStr, u_dex))
        newCredits = strListMod(creditsStr, u_dex, pCredits - amount)

        newBets = strListMod(betsStr, u_dex, amount + readIntValStrList(betsStr, u_dex))

        nextPlayer = 0

        if str(user_id) == users[0]:
            nextPlayer = 1

        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, player_turn = ? WHERE game_id = {game_id}", newCredits, newBets, int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "fold":

        newPlayers = strListPop(game["player_ids"], u_dex)
        newHands = strListPop(game["player_hands"], u_dex, sep=";")
        newProtecteds = strListPop(game["player_protecteds"], u_dex, sep=";")
        newCredits = strListPop(creditsStr, u_dex,)
        newBets = strListPop(betsStr, u_dex)

        newFoldedP = strListAppend(game["folded_players"], user_id)

        newFoldedC = strListAppend(game["folded_credits"], int(strListRead(creditsStr, u_dex)) + int(strListRead(betsStr, u_dex, default=0)))

        foldEnd = False

        if len(newPlayers.split(",")) == 1:
            foldEnd = True
            # TODO END GAME BY FOLDING!! VERY IMPORTANT!! DO NOT FORGET!!

        nextPlayer = u_dex

        if str(user_id) == users[len(users) - 1]:
            endRound = True

        if endRound == True:
            nextPlayer = 0

        db.execute(f"UPDATE games SET player_ids = ?, player_credits = ?, player_bets = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, folded_players = ?, folded_credits = ? WHERE game_id = {game_id}", newPlayers, newCredits, newBets, newHands, newProtecteds, int(newPlayers.split(",")[nextPlayer]), newFoldedP, newFoldedC)

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    creditsStr = game["player_credits"]
    betsStr = game["player_bets"]

    if foldEnd == True:

        newCredits = creditsStr
        newCredits = strListMod(creditsStr, 0, int(strListRead(creditsStr, 0)) + game["hand_pot"] + int(strListRead(betsStr, 0)))

        db.execute(f"UPDATE games SET player_credits = ?, player_bets = ?, hand_pot = ?, player_turn = ?, completed = ? WHERE game_id = {game_id}", newCredits, "", 0, int(users[0]), True)

    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    creditsStr = game["player_credits"]
    betsStr = game["player_bets"]

    if endRound == True:
        
        betsSum = 0

        newBets = ""
        for i in range(len(users) - 1):
            newBets += ","

        for i in range(len(users)):

            betsSum += int(strListRead(betsStr, i))

        if foldEnd == True:
            betsSum = 0

        db.execute(f"UPDATE games SET player_bets = ?, hand_pot = ?, phase = ?, player_turn = ? WHERE game_id = {game_id}", newBets, game["hand_pot"] + betsSum, "card", int(users[0]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    return

@socketio.on("card", namespace="/card")
def card(data):

    # Set some variables for the whole function
    game_id = data["game_id"]
    action = data["action"]
    tradeCard = ""
    try:
        tradeCard = data["trade"]
    except KeyError:
        pass
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    user_id = session.get("user_id")
    u_dex = users.index(str(user_id))
    deckStr = game["deck"]
    handsStr = game["player_hands"]
    handsList = handsStr.split(";")
    protsStr = game["player_protecteds"]
    protsList = protsStr.split(";")
    handPot = game["hand_pot"]
    creditsStr = game["player_credits"]

    endRound = False
    endGame = False

    if game["phase"] != "card" and game["phase"] != "alderaan":
        return

    player = ""
    if users.index(str(user_id)) == 0:
        player = "player1"

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return
    
    if action == "draw":
        drawData = drawCard(deckStr)
        newDeck = drawData["deck"]
        newCard = drawData["card"]
        handsList[u_dex] += "," + newCard
        newHands = listToStr(handsList, sep=";")

        protsList[u_dex] += ",0"
        newProts = listToStr(protsList, sep=";")

        nextPlayer = u_dex + 1

        if str(user_id) == users[len(users) - 1]:
            endRound = True

        if endRound == True:
            nextPlayer = 0


        db.execute(f"UPDATE games SET deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ? WHERE game_id = {game_id}", newDeck, newHands, newProts, int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "trade":

        handsList[u_dex] = strListRemove(handsList[u_dex], tradeCard)
        protsList[u_dex] = strListPop(protsList[u_dex], u_dex)

        drawData = drawCard(deckStr)
        newDeck = drawData["deck"]
        newCard = drawData["card"]
        handsList[u_dex] += "," + newCard
        newHands = listToStr(handsList, sep=";")

        protsList[u_dex] += ",0"
        newProts = listToStr(protsList, sep=";")

        nextPlayer = u_dex + 1

        if str(user_id) == users[len(users) - 1]:
            endRound = True

        if endRound == True:
            nextPlayer = 0


        db.execute(f"UPDATE games SET deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ? WHERE game_id = {game_id}", newDeck, newHands, newProts, int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "stand":

        nextPlayer = u_dex + 1

        if str(user_id) == users[len(users) - 1]:
            endRound = True

        if endRound == True:
            nextPlayer = 0


        db.execute(f"UPDATE games SET player_turn = ? WHERE game_id = {game_id}", int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    elif action == "alderaan":

        nextPlayer = u_dex + 1

        if str(user_id) == users[len(users) - 1]:
            endGame = True

        if endGame == True:
            nextPlayer = 0


        db.execute(f"UPDATE games SET phase = ?, player_turn = ? WHERE game_id = {game_id}", "alderaan", int(users[nextPlayer]))

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    users = game["player_ids"].split(",")
    handsStr = game["player_hands"]
    handsList = handsStr.split(";")
    protsStr = game["player_protecteds"]
    protsList = protsStr.split(";")
    deckStr = game["deck"]

    if endRound == True:

        if game["phase"] == "alderaan":
            endGame = True

        else:

            newHands = handsStr
            newProtecteds = protsStr
            newDeck = deckStr


            shift = rollShift()

            if shift == True:
                drawCounts = []
                hCards = []
                for k in range(len(handsList)):
                    drawCount = 0
                    newHandList = handsList[k].split(",")
                    newProtsList = protsList[k].split(",")

                    for p in range(len(protsList[k].split(","))):

                        if protsList[k].split(",")[p] == "0":
                            newHandList.remove(handsList[k].split(",")[p])
                            newProtsList.remove(protsList[k].split(",")[p])
                            drawCount += 1
                        else:
                            hCards.append(handsList[k].split(",")[p])

                    newHands = strListMod(newHands, k, listToStr(newHandList), sep=";")
                    newProtecteds = strListMod(newProtecteds, k, listToStr(newProtsList), sep=";")
                    drawCounts.append(drawCount)

                newDeck = shuffleDeck(hCards)

                handsList = newHands.split(";")
                
                protsList = newProtecteds.split(";")

                for i in range(len(handsList)):

                    for c in range(drawCounts[i]):
                        drawData = drawCard(deckStr)
                        newDeck = drawData["deck"]
                        newCard = drawData["card"]
                        handsList[i] += "," + newCard
                        handsList[i] = handsList[i].strip(",")
                        newHands = listToStr(handsList, sep=";")

                        protsList[i] += ",0"
                        protsList[i] = protsList[i].strip(",")
                        newProtecteds = listToStr(protsList, sep=";")

                        deckStr = newDeck




            db.execute(f"UPDATE games SET phase = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, shift = ? WHERE game_id = {game_id}", "betting", deckStr, newHands, newProtecteds, int(users[0]), shift)

            # Force Reload players
            data = {
                "cmd": "reload",
                "g_id": game_id
            }

            send(data, broadcast=True)


    if endGame == True:
        handVals = []

        for hand in handsList:
            v = 0
            for card in hand.split(","):
                v += int(card)

            if hand.split(",").sort() == ["0", "2", "3"]:
                v = 230

            elif hand.split(",") == ["-2", "-2"]:
                v = -22

            handVals.append(v)

        bestVal = 0

        bestDexes = []

        bombOutDexes = []

        for val in handVals:
            if val == 230:
                bestVal = val
                break

            elif val == 0 or abs(val) > 23:
                bombOutDexes.append(handVals.index(val))

            elif abs(val) > abs(bestVal):
                bestVal = val

            elif abs(val) == abs(bestVal):
                if val > bestVal: #aka if this new val is positive and the old one is negative
                    bestVal = val

        for val in handVals:
            if val == bestVal:
                bestDexes.append(handVals.index(val))


        newDeck = deckStr
        newHands = handsStr
        newProtecteds = protsStr

        newSabaccPot = game["sabacc_pot"]
        

        # One winner, probable case
        if len(bestDexes) == 1:

            for b in bombOutDexes:
                creditsStr = strListMod(creditsStr, b, int(strListRead(creditsStr, b)) - round((handPot * 0.1)))
                newSabaccPot += round(handPot) * 0.1

            creditsStr = strListMod(creditsStr, bestDexes[0], int(strListRead(creditsStr, bestDexes[0])) + handPot)
            if abs(bestVal) == 23 or bestVal == 230:
                creditsStr = strListMod(creditsStr, bestDexes[0], int(strListRead(creditsStr, bestDexes[0])) + newSabaccPot)
                newSabaccPot = 0

        # Tie, improbable TODO Probably super buggy, too lazy to test
        elif len(bestDexes) > 1:
            for i in bestDexes:

                drawData = drawCard(deckStr)
                newDeck = drawData["deck"]
                newCard = drawData["card"]
                handsList[i] += "," + newCard
                handsList[i] = handsList[i].strip(",")
                newHands = listToStr(handsList, sep=";")

                protsList[i] += ",0"
                protsList[i] = protsList[i].strip(",")
                newProtecteds = listToStr(protsList, sep=";")

                deckStr = newDeck

            handVals = []

            for hand in handsList:
                v = 0
                for card in hand.split(","):
                    v += int(card)

                if hand.split(",").sort() == ["0", "2", "3"]:
                    v = 230

                elif hand.split(",") == ["-2", "-2"]:
                    v = -22

                handVals.append(v)

            bestVal = 0

            bestDexes = []

            bombOutDexes = []

            for val in handVals:
                if val == 230:
                    bestVal = val
                    break

                elif val == 0 or abs(val) > 23:
                    bombOutDexes.append(handVals.index(val))

                elif abs(val) > abs(bestVal):
                    bestVal = val

                elif abs(val) == abs(bestVal):
                    if val > bestVal: #aka if this new val is positive and the old one is negative
                        bestVal = val

            for val in handVals:
                if val == bestVal:
                    bestDexes.append(handVals.index(val))

            for b in bombOutDexes:
                creditsStr = strListMod(creditsStr, b, int(strListRead(creditsStr, b)) - round((handPot * 0.1)))
                newSabaccPot += round(handPot) * 0.1

            creditsStr = strListMod(creditsStr, bestDexes[0], int(strListRead(creditsStr, bestDexes[0])) + handPot)
            if abs(bestVal) == 23 or bestVal == 230:
                creditsStr = strListMod(creditsStr, bestDexes[0], int(strListRead(creditsStr, bestDexes[0])) + newSabaccPot)
                newSabaccPot = 0


        db.execute(f"UPDATE games SET player_credits = ?, hand_pot = ?, sabacc_pot = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, completed = ? WHERE game_id = {game_id}", creditsStr, 0, newSabaccPot, newDeck, newHands,  newProtecteds, int(users[0]), True)

        # Force Reload players
        data = {
            "cmd": "reload",
            "g_id": game_id
        }

        send(data, broadcast=True)

        return


@socketio.on("cont", namespace="/cont")
def cont(data):

    # Set some variables for the whole function
    game_id = data["game_id"]

    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]
    creditsStr = game["player_credits"]
    users = game["player_ids"].split(",")
    user_id = session.get("user_id")

    if game["completed"] != True:
        return

    # If it is not this player's turn
    if game["player_turn"] != int(user_id):
        return
    
    newPlayers = game["player_ids"]
    if game["folded_players"] != None:
        newPlayers += "," + game["folded_players"]

    newPlayers = newPlayers.strip(",")
    users = newPlayers.split(",")

    newCredits = creditsStr
    if game["folded_credits"] != None:
        newCredits += "," + game["folded_credits"]

    newCredits = newCredits.strip(",")
    creditsList = newCredits.split(",")

    for c in creditsList:
        creditsList[creditsList.index(c)] = str(int(c) - 15)
    
    newCredits = listToStr(creditsList)

    hPot = 5 * len(users)
    sPot = game["sabacc_pot"] + (10 * len(users))

    # Protecteds
    prots = ""
    for i in range(len(users)):
        prots += "0,0;"

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
    db.execute(f"UPDATE games SET player_ids = ?, player_credits = ?, player_bets = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, deck = ?, player_hands = ?, player_protecteds = ?, player_turn = ?, folded_players = ?, folded_credits = ?, completed = ? WHERE game_id = {game_id}", newPlayers, newCredits, pBets, hPot, sPot, "betting", deck, handsStr, prots, int(users[0]), None, None, False)

    # Force Reload players
    data = {
        "cmd": "reload",
        "g_id": game_id
    }

    send(data, broadcast=True)


@app.route("/game/<game_id>")
@login_required
def game(game_id):
    """Play Sabacc!"""

    user_id = session.get("user_id")
    game = db.execute(f"SELECT * FROM games WHERE game_id = {game_id}")[0]

    yours = False
    for id in game["player_ids"].split(","):
        if id == str(user_id):
            yours = True
            break

    if yours == False:
        return apology("This is not one of your games")

    users = []
    for u in game["player_ids"].split(","):
        users.append(db.execute("SELECT id, username FROM users WHERE id = ?", int(u))[0]["username"])

    return render_template("game.html", game=game, users=users, user_id=int(session.get("user_id")))


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

        # Ensure password is valid
        if not request.form.get("password"):
            return apology("must provide password", 403)

        orHash = db.execute(f"SELECT * FROM users WHERE username = ?", username)[0]["hash"]
        if check_password_hash(orHash, request.form.get("password")) == False:
            return apology("invalid password")

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
