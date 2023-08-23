from flask import redirect, render_template, request, session
from functools import wraps
import random
from flask_socketio import emit
from dataHelpers import *

DECK = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17"

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

def constructDeck(playerCount):
    deck = DECK
    deckList = list(deck.split(","))
    hands = []

    for i in range(playerCount):
        player_hand = ""
        for i in range(2):
            randDex = random.randint(0, len(deckList) - 1)
            if player_hand == "":
                player_hand = deckList.pop(randDex)
            else:
                player_hand = player_hand + "," + deckList.pop(randDex)

        hands.append(player_hand)

    deck = listToStr(deckList)

    data = {"deck": deck, "hands": hands}
    return data

def drawCard(deckStr):

    deckList = deckStr.split(",")

    randDex = random.randint(0, len(deckList) - 1)
    card = deckList.pop(randDex)

    deck = listToStr(deckList)

    data = {"deck": deck, "card": card}
    return data

def rollShift():
    dieOne = random.randint(1, 6)
    dieTwo = random.randint(1, 6)
    
    if dieOne == dieTwo:
        return True
    else:
        return False








def shuffleDeck(outCards):
    deckList = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17".split(",")
    for card in outCards:
        deckList.remove(card)
    return listToStr(deckList)