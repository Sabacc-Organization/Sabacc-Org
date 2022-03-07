from flask import redirect, render_template, request, session
from functools import wraps
import random
from flask_socketio import emit


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

def constructDeck():
    deck = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17"
    deckList = list(deck.split(","))
    player1_hand = ""
    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player1_hand == "":
            player1_hand = deckList[randDex]
        else:
            player1_hand = player1_hand + "," + deckList[randDex]
        deckList.pop(randDex)
    player2_hand = ""
    for i in range(2):
        randDex = random.randint(0, len(deckList) - 1)
        if player2_hand == "":
            player2_hand = deckList[randDex]
        else:
            player2_hand = player2_hand + "," + deckList[randDex]
        deckList.pop(randDex)
    deck = ""
    for card in deckList:
        if deck == "":
            deck = card
        else:
            deck = deck + "," + card

    data = {"deck": deck, "player1_hand": player1_hand, "player2_hand": player2_hand}
    return data

def reshuffleDeck(game, outCards):
    deckList = list(game["deck"].split(","))
    print(deckList)
    for card in outCards:
        deckList.remove(card)
    return deckList

def emitGame(game, users):
    try:
        emit("bet", game, room=users[game["player1_id"]])
    except KeyError:
        pass

    try:
        emit("bet", game, room=users[game["player2_id"]])
    except KeyError:
        pass