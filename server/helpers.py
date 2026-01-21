from flask import redirect, render_template, request, session, jsonify
from functools import wraps
import random
from flask_socketio import emit
# import psycopg
from dataHelpers import *
import sqlite3
from werkzeug.security import check_password_hash
import yaml
from abc import ABC, abstractmethod # allows abstract classes/methods
import copy
import json
from typing import Union
from enum import Enum

# Get config.yml data
config = {}
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

# Connect to database
# conn = sqlite3.connect(config['DATABASE'])
# db = conn.cursor()

"""Do not change these from the names they have in the db tables. . . Would have disastrous consequences!"""
class Game_Variant(Enum):
    TRADITIONAL = "traditional"
    CORELLIAN_SPIKE = "corellian_spike"
    KESSEL = "kessel"

class Suit:
    DEFAULT = "NONE"

class Card:
    def __init__(self, val:int, suit:str):
        self.val = val
        self.suit = suit
    def __str__(self) -> str:
        return f'{addPlusBeforeNumber(self.val)} {self.suit}'
    def __eq__(self, other:object) -> bool:
        try:
            return self.val == other.val and self.suit == other.suit
        except AttributeError:
            return False
    def toDict(self) -> dict:
        return {
            'val': self.val,
            'suit': self.suit
        }
    @staticmethod
    def fromDict(card:dict) -> object:
        return Card(val=card['val'], suit=card['suit']) if card is not None else None
    
    def toDb(self):
        return json.dumps(self.toDict())
    @staticmethod
    def fromDb(card: Union[str, dict]) -> object:
        if isinstance(card, str):
            return Card.fromDict(json.loads(card))
        if isinstance(card, dict):
            return Card.fromDict(card)

class Deck:
    def __init__(self, cards:list=[]):
        self.cards = cards.copy()
    def __str__(self) -> str:
        return f'[{listToStr(self.cards)}]'
    
    def toDb(self):
        return json.dumps(self.toDict())
    @staticmethod
    def fromDb(deck: Union[str, list]) -> object:
        if isinstance(deck, str):
            return Deck.fromDict(json.loads(deck))
        if isinstance(deck, list):
            return Deck.fromDict(deck)

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
    def fromDb(hand: Union[str, list]) -> object:
        if isinstance(hand, str):
            return Hand.fromDict(json.loads(hand))
        if isinstance(hand, list):
            return Hand.fromDict(hand)
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

    @abstractmethod
    def getVariant(self) -> Game_Variant:
        pass
        
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
        if not pokerStyle:
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
    def __init__(self,
        players:list,
        id:int=None,
        player_turn:int=None,
        p_act='',
        deck:Deck=None,
        phase='betting',
        cycle_count=0,
        completed=False,
        shift=False,
        settings={
            "PokerStyleBetting": False,
            "SmallBlind": 1,
            "BigBlind": 2
        }, created_at = None,
        move_history = []):


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
        self.created_at = created_at
        self.move_history = move_history

    @staticmethod
    @abstractmethod
    def newGame(playerIds:list, playerUsernames:list, startingCredits=1000, db=None):
        pass

    def getClientData(self, user_id = None, username = None):
        player: Player = self.getPlayer(username, user_id)

        gameDict = self.toDict()
        gameDict.pop('deck')
        users = [i.username for i in self.getActivePlayers()]

        if player is None:
            return {"message": "Spectating", "gata": gameDict, "users": users, "user_id": -1, "username": ""}

        return {"message": "Good luck!", "gata": gameDict, "users": users, "user_id": int(player.id), "username": player.username}
    
    # sets up for next round
    def nextRound(self, rotateDealer=True):
        if rotateDealer:
            # rotate dealer (1st in list is always dealer) - move 1st player to end
            self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= (self.settings["HandPotAnte"] + self.settings["SabaccPotAnte"]) # Make users pay Sabacc and Hand pot Antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action

        # Variant specific stuff
        if self.getVariant() == Game_Variant.TRADITIONAL:
            self.startFirstBettingPhase()
            self.deck = TraditionalDeck()
            self.phase = "betting"
        elif self.getVariant() == Game_Variant.CORELLIAN_SPIKE:
            self.deck = CorellianSpikeDeck()
            self.discardPile = [self.drawFromDeck()]
            self.phase = "card"
            self.player_turn = self.players[0].id

        self.shuffleDeck()
        self.dealHands()

        self.cycle_count = 0
        self.p_act = ""
        self.completed = False

    def dealHands(self):
        for player in self.players:
            player.hand.cards = [self.drawFromDeck(), self.drawFromDeck()]

    def startFirstBettingPhase(self): # blinds and antes
        # Antes (Pots)
        self.hand_pot = self.settings["HandPotAnte"] * len(self.getActivePlayers())
        self.sabacc_pot += self.settings["SabaccPotAnte"] * len(self.getActivePlayers())

        # Player turn (not PokerStyleBetting)
        self.player_turn = self.players[0].id

        # Blinds
        if self.settings["PokerStyleBetting"]:
            activePlayers = self.getActivePlayers()

            smallBlind = activePlayers[1 % len(activePlayers)]
            smallBlind.bet = self.settings["SmallBlind"]
            smallBlind.credits -= self.settings["SmallBlind"]

            bigBlind = activePlayers[2 % len(activePlayers)]
            bigBlind.bet = self.settings["BigBlind"]
            bigBlind.credits -= self.settings["BigBlind"]

            self.player_turn = activePlayers[3 % len(activePlayers)].id
    
    def getGameData(self):

        gameDict = self.toDict()
        if self.getVariant() != Game_Variant.KESSEL:
            gameDict.pop('deck')
        users = [i.username for i in self.getActivePlayers()]

        return {"message": "Good luck!", "gata": gameDict, "users": users}

    # shuffle deck
    def shuffleDeck(self):
        self.deck.shuffle()

    def drawFromDeck(self):
        # if deck is empty, reshuffle
        if len(self.deck.cards) == 0:
            self._reshuffle()
        return self.deck.draw()
    
    @abstractmethod
    def _reshuffle(self):
        pass

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
        for player in (self.players[:self.players.index(player)] + self.players[self.players.index(player) + 1:]).reversed():
            if not player.folded:
                return player
    
    def getNextPlayerInPhase(self, player):

        simpleNextPlayer = None
        players = self.getActivePlayers()

        if players.index(player) < len(players) - 1:
            simpleNextPlayer = players[players.index(player) + 1]

        if self.phase == "betting":
            nextPlayer = None
            if not self.settings["PokerStyleBetting"]:
                betAmount = [i.getBet() for i in self.players]
                betAmount.append(0)
                betAmount = max(betAmount)
                for i in players:
                    iBet = i.bet if i.bet != None else -1
                    if iBet < betAmount:
                        nextPlayer = i
                        break
            elif self.settings["PokerStyleBetting"]:
                if simpleNextPlayer == None:
                    simpleNextPlayer = players[0]
                if simpleNextPlayer.getBet() < self.getGreatestBet() or simpleNextPlayer.bet == None:
                    nextPlayer = simpleNextPlayer

            return nextPlayer
        else:
            return simpleNextPlayer
        
    @abstractmethod
    def getNextPhase(self):
        """
        This method should return the next phase of the game based on the current state.

        Returns:
            str: The next phase of the game.
        """
        pass

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
    
    def deckToDb(self):
        return self.deck.toDb()
    
    def moveHistoryToDb(self):
        return json.dumps(self.move_history)
    
    def settingsToDb(self):
        return json.dumps(self.settings)
    
    # compare games to see what has changed
    def compare(self, other):
        selfDict = self.toDict()
        originalValues = {}
        for key, value, in other.toDict().items():
            if value != selfDict[key]:
                originalValues[key] = value
        return originalValues
    
    def quitFromCompletedGame(self, player, db, modifyDb=True):
        if self.completed == False:
            return
        
        player.lastAction = "quit the game"
        self.players.remove(player)
        if self.player_turn == player.id:
            if len(self.getActivePlayers()) > 0:
                self.player_turn = self.getActivePlayers()[0].id
            else:
                self.player_turn = None
        self.p_act = player.username + " quit the game"

        if modifyDb:
            dbList = [
                self.playersToDb(),
                self.player_turn,
                self.p_act,
                self.id
            ]

            db.execute(f"UPDATE {self.getVariant().value}_games SET players = ?, player_turn = ?, p_act = ? WHERE game_id = ?", dbList)

    def betPhaseAction(self, params:dict, player, db, modifyDb=True):
        players = self.getActivePlayers()

        if params["action"] == "check":
            if player.getBet() != self.getGreatestBet():
                return
            player.makeBet(0, False)

        elif params["action"] == "bet":
            if player.getBet() != self.getGreatestBet() or player.bet != None or players.index(player) != 0:
                return
            player.makeBet(params["amount"], True)

        elif params["action"] == 'call':
            player.makeBet(self.getGreatestBet(), True)
            player.lastAction = 'calls'

        elif params["action"] == 'raise':
            player.makeBet(params["amount"], True)
            player.lastAction = f'raises to {params["amount"]}'

        nextPlayer = self.getNextPlayerInPhase(player)

        if params['action'] == "fold":
            if self.settings["PokerStyleBetting"]:
                self.hand_pot += player.getBet()
            player.fold(self.settings["PokerStyleBetting"])

        elif params["action"] == "quit":
            self.hand_pot += player.getBet()
            player.lastAction = "quit the game"
            self.players.remove(player)
            if nextPlayer != None:
                if nextPlayer.getBet() == self.getGreatestBet():
                    nextPlayer = None

        players = self.getActivePlayers()

        if len(players) == 1:
            winningPlayer = players[0]
            winningPlayer.credits += self.hand_pot + winningPlayer.getBet()
            self.hand_pot = 0
            winningPlayer.bet = None

        if nextPlayer == None:
            # add all bets to hand pot
            for p in players:
                self.hand_pot += p.getBet()
                p.bet = None

        # Update game object before db update
        self.phase = 'betting' if nextPlayer != None else self.getNextPhase()
        self.player_turn = nextPlayer.id if nextPlayer != None else (players[0].id if len(players) > 0 else None)
        self.p_act = player.username + " " + player.lastAction
        self.completed = len(players) <= 1

        if modifyDb:
            dbList = [
                self.playersToDb(),
                self.hand_pot,
                self.phase,
                self.player_turn,
                self.p_act,
                self.completed,
                self.id
            ]
        
            db.execute(f"UPDATE {self.getVariant().value}_games SET players = ?, hand_pot = ?, phase = ?, player_turn = ?, p_act = ?, completed = ? WHERE game_id = ?", dbList)
    
    def shiftPhaseAction(self, params:dict, player, db, modifyDb=True):
        if params["action"] == "shift":
            self._shift = self.rollShift()

            if self._shift:
                self.shift()

            # Set the Shift message
            shiftStr = "Sabacc shift!" if self._shift else "No shift!"

            # Update game object before db update

            self.phase = self.getNextPhase()
            self.p_act = shiftStr
            self.cycle_count += 1
        elif params["action"] == "quit":
            self.players.remove(player)
            self.p_act = player.username + " quit the game"
            if len(self.getActivePlayers()) == 1:
                winningPlayer = self.getActivePlayers()[0]
                winningPlayer.credits += self.hand_pot + winningPlayer.getBet()
                self.hand_pot = 0
                winningPlayer.bet = None
                self.p_act += "; " + winningPlayer.username + " wins!"
                self.completed = True

        self.player_turn = self.getActivePlayers()[0].id

        if modifyDb:
            dbList = [
                self.phase,
                self.hand_pot,
                self.deck.toDb(),
                self.playersToDb(),
                self.cycle_count,
                self.player_turn,
                self._shift,
                self.p_act,
                self.completed,
                self.id
            ]

            db.execute(f"UPDATE {self.getVariant().value}_games SET phase = ?, hand_pot = ?, deck = ?, players = ?, cycle_count = ?, player_turn = ?, shift = ?, p_act = ?, completed = ? WHERE game_id = ?", dbList)


    # abstract method for card actions (draw, trade, etc.)
    # each sub game class must override
    @abstractmethod
    def action(self, action, actionParams):
        pass

""" These must be imported after all the parent classes are defined """
from traditional.traditionalHelpers import *
from corellian_spike.corellianHelpers import *
from kessel.kesselHelpers import *

# For getting a list of dictionaries for rows in a database.
def getDictsForDB(cursor: sqlite3.Cursor):
    rows = cursor.fetchall()
    columns = cursor.description

    returnList = []
    for row in rows:
        rowDict = {}
        for i, col in enumerate(columns):
            rowDict[col[0]] = row[i]
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
def checkLogin(db, username, password):
    # If username is none
    if not username:
        return {"message": "Must provide username", "status": 401}

    # If password is none
    if not password:
        return {"message": "Must provide password", "status": 401}
    
    # Attempt to find the password hash of this user
    orHash = None
    try:
        db.execute("SELECT * FROM users WHERE username = ?", [username])
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
