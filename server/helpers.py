from flask import redirect, render_template, request, session, jsonify
from functools import wraps
import random
from flask_socketio import emit
import psycopg
from dataHelpers import *
from cs50 import SQL
from werkzeug.security import check_password_hash
import yaml
from abc import ABC, abstractmethod # allows abstract classes/methods
import copy

# Get config.yml data
config = {}
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

# Connect to database
conn = psycopg.connect(config['DATABASE'])
db = conn.cursor()

class Suit:
    DEFAULT = "NONE"

class Card:
    def __init__(self, val:int, suit:str):
        self.val = val
        self.suit = suit
    def __str__(self) -> str:
        return f'{addPlusBeforeNumber(self.val)} {self.suit}'
    def __eq__(self, other:object) -> bool:
        return self.val == other.val and self.suit == other.suit
    def toDict(self) -> dict:
        return {
            'val': self.val,
            'suit': self.suit
        }
    @staticmethod
    def fromDict(card:dict) -> object:
        return Card(val=card['val'], suit=card['suit'])
    
    def toDb(self, cardType):
        return cardType.python_type(self.val, self.suit)
    @staticmethod
    def fromDb(card):
        return Card(card.val, card.suit)

class Deck:
    def __init__(self, cards:list=[]):
        self.cards = cards.copy()
    def __str__(self) -> str:
        return f'[{listToStr(self.cards)}]'
    
    def toDb(self, card_type):
        return [card.toDb(card_type) for card in self.cards]
    @staticmethod
    def fromDb(deck) -> object:
        return Deck([Card.fromDb(card) for card in deck])

    def toDict(self) -> list:
        return [card.toDict() for card in self.cards]
    @staticmethod
    def fromDict(dict) -> object:
        return Deck([Card.fromDict(card) for card in dict])

    def shuffle(self):
        random.shuffle(self.cards)

    # remove a number of cards from the top (end) of the deck and return them
    def draw(self, numCards=1):
        # check there are enuf cards left in deck
        if len(self.cards) < numCards:
            print(f"ERROR: trying to draw from deck but not enough cards left")
            return None

        if numCards == 1:
            return self.cards.pop()
        else:
            drawnCards = []
            for i in range(numCards):
                drawnCards.append(self.cards.pop())
            return drawnCards

class Hand:
    def __init__(self, cards=[]):
        self.cards: list = cards.copy()
        self.sort()
    
    def __eq__(self, other:object) -> bool:
        if len(self.cards) != len(other.cards):
            return False
        for i in range(len(self.cards)):
            if self.cards[i] != other.cards[i]:
                return False
        return True

    def __str__(self) -> str:
        self.sort()
        return f'[{listToStr(self.cards)}]'
    
    @staticmethod
    def fromDb(hand) -> object:
        return Hand([Card.fromDb(card) for card in hand])
    def toDict(self) -> list:
        return [card.toDict() for card in self.cards]
    @staticmethod
    def fromDict(hand) -> object:
        return Hand([Card.fromDict(card) for card in hand])

    def append(self, card:Card):
        self.cards.append(card)
    def pop(self, index:int) -> object:
        return self.cards.pop(index)
    
    def getListOfVals(self) -> list:
        return [card.val for card in self.cards]
    
    def getTotal(self) -> int:
        return sum(self.getListOfVals())
    
    # sort hand by value (selection sort)
    def sort(self):
        if self.cards == []:
            return
        self.cards.sort(key=(lambda x: x.val))

class Player:
    def __init__(self, id:int, username:str, credits:int, bet:int, hand:object, folded:bool, lastAction:str):
        self.id = id
        self.username = username
        if type(credits) == int:
            self.credits = credits
        else:
            print(f"ERROR: type of credits is {type(credits)}, not int")
        if type(bet) == int or bet == None:
            self.bet = bet
        else:
            print(f"ERROR: bet is not int or none, it's {type(bet)}")
        self.hand = copy.deepcopy(hand)
        self.folded = folded
        self.lastAction = lastAction
        
    def addToHand(self, cards):
        if not isinstance(cards, list):
            cards = [cards]
        self.hand.cards.extend(cards)

    def discard(self, discardCardIndex:int):
        try:
            return self.hand.pop(discardCardIndex)
        except IndexError:
            print("ERROR: invalid index for discard card")
    
    def getIndexOfCard(self, targetCard:Card) -> int:
        for i in range(len(self.hand)):
            if self.hand[i] == targetCard:
                return i
        return -1
    
    def getBet(self) -> int:
        return self.bet if self.bet != None else 0
        
    def fold(self, pokerStyle=False):
        if pokerStyle:
            self.credits += self.getBet()
        self.bet = None
        self.folded = True
        self.lastAction = "folded"
    
    def makeBet(self, creditAmount: int, absolute: bool = True):
        if absolute:
            self.credits -= creditAmount - self.getBet()
            self.bet = creditAmount
        else:
            self.bet = self.bet if creditAmount == 0 else self.getBet()
            self.credits -= creditAmount
            if not self.bet:
                self.bet = 0
            self.bet += creditAmount

        if creditAmount != 0:
            self.lastAction = f'bets {creditAmount}'
        else:
            self.lastAction = f'checks'

class Game:
    def __init__(self, players:list, id:int=None, player_turn:int=None, p_act='', deck:Deck=None, phase='betting', cycle_count=0, completed=False, shift=False, settings={ "PokerStyleBetting": False }):
        self.players = players
        self.id = id
        self.player_turn = player_turn
        self.p_act = p_act
        self.deck = deck
        self.phase = phase
        self.cycle_count = cycle_count
        self.completed = completed
        self.shift = shift
        self.settings = settings

    @staticmethod
    @abstractmethod
    def newGame(playerIds:list, playerUsernames:list, startingCredits=1000, db=None):
        pass

    # shuffle deck
    def shuffleDeck(self):
        self.deck.shuffle()

    # roll shift
    def rollShift(self):
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        self.shift = roll1 == roll2
        return self.shift
        
    def getActivePlayers(self):
        activePlayers = []
        for player in self.players:
            if not player.folded:
                activePlayers.append(player)
        return activePlayers
    
    def getPreviousPlayer(self, player):
        return self.getActivePlayers()[(self.getActivePlayers().index(player) - 1) % len(self.getActivePlayers())]
    
    def getNextPlayer(self, player):
        return self.getActivePlayers()[(self.getActivePlayers().index(player) + 1) % len(self.getActivePlayers())]

    def getPlayerDex(self, username:str=None, id:int=None):
        for i in range(len(self.players)):
            player = self.players[i]
            if player.username == username or player.id == id:
                return i
        return -1
    def getPlayer(self, username:str=None, id:int=None):
        dex = self.getPlayerDex(username=username, id=id)
        return None if dex == -1 else self.players[dex]
    def containsPlayer(self, username:str=None, id:int=None) -> bool:
        return self.getPlayer(username=username, id=id) != None
    
    def getGreatestBet(self):
        maxBet = 0
        for player in self.getActivePlayers():
            if player.getBet() > maxBet:
                maxBet = player.getBet()
        return maxBet
    
    def playerFold(self, player):
        if self.settings["PokerStyleBetting"]:
            self.handPot += player.getBet()
        player.fold(self.settings["PokerStyleBetting"])
    
    def deckToDb(self, card_type):
        return self.deck.toDb(card_type=card_type)
    
    # abstract method for card actions (draw, trade, etc.)
    # each sub game class must override
    @abstractmethod
    def action(self, action, actionParams):
        pass

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

# if the number is positive, it adds a plus in front of it (otherwise just returns the number)
def addPlusBeforeNumber(n:int) -> str:
    return ('+' if n > 0 else '') + str(n)

def bothOrAll(num:int):
    return 'both' if num == 2 else 'all'
