import random
from enum import Enum
from helpers import *
import copy
import json
from datetime import datetime, timezone
from typing import Union

class TraditionalSuit(Suit):
    COINS = 'coins'
    FLASKS = 'flasks'
    SABERS = 'sabers'
    STAVES = 'staves'
    NEGATIVE_NEUTRAL = 'negative/neutral'
    ALL = [COINS, FLASKS, SABERS, STAVES]
    @staticmethod
    def random(val=None):
        return random.choice(TraditionalSuit.ALL)

class SpecialHands(Enum):
    IDIOTS_ARRAY = 230
    FAIRY_EMPRESS = -22

class TraditionalCard(Card):
    def __init__(self, val:int, suit:TraditionalSuit, protected=False):
        super().__init__(val=val, suit=suit)
        self.protected = protected

    def __eq__(self, other) -> bool:
        return other != None and (self.val == other.val and self.suit == other.suit)

    def __str__(self) -> str:
        return f"{self.val} of {str(self.suit)}{' (protected)' if self.protected else ''}"
        

    def toDict(self) -> dict:
        return {
            'val': self.val,
            'suit': self.suit,
            'prot': self.protected
        }

    @staticmethod
    def fromDb(card: Union[str, dict]) -> object:
        if isinstance(card, str):
            return TraditionalCard.fromDict(json.loads(card))
        if isinstance(card, dict):
            return TraditionalCard.fromDict(card)

    @staticmethod
    def fromDict(dict):
        return TraditionalCard(dict['val'],dict['suit'],dict['prot'])

    @staticmethod
    def randCardNotInList(val:int, protected=False, unallowedCards=[]):
        card = None
        if val <= 0:
            card = TraditionalCard(val=val, suit=TraditionalSuit.NEGATIVE_NEUTRAL, protected=protected)
            if unallowedCards.count(card) > 1:
                print(f"WARNING: more than 2 {val}'s exist")

        else: # positive val
            allowedSuits = [TraditionalSuit.COINS, TraditionalSuit.FLASKS, TraditionalSuit.SABERS, TraditionalSuit.STAVES]
            for c in unallowedCards:
                if c.val == val and c.suit in allowedSuits:
                    allowedSuits.remove(c.suit)

            if len(allowedSuits) == 0:
                print(f"WARNING: more than 4 {val}'s exist")
                card = TraditionalCard(val=val,suit=random.choice([TraditionalSuit.COINS, TraditionalSuit.FLASKS, TraditionalSuit.SABERS, TraditionalSuit.STAVES]),protected=protected)

            else:
                card = TraditionalCard(val=val,suit=random.choice(allowedSuits), protected=protected)

        return card

class TraditionalDeck(Deck):
    def __init__(self, cards:list=None):
        super().__init__()
        if not cards:
            self.cards = 2 * [
                TraditionalCard(-11,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(0,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-8,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-14,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-15,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-2,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-13,TraditionalSuit.NEGATIVE_NEUTRAL),
                TraditionalCard(-17,TraditionalSuit.NEGATIVE_NEUTRAL)
            ]

            for suit in [TraditionalSuit.COINS,TraditionalSuit.FLASKS,TraditionalSuit.SABERS,TraditionalSuit.STAVES]:
                for val in range(1,16):
                    self.cards.append(TraditionalCard(val=val,suit=suit))

            self.shuffle()

        else:
            self.cards = cards

    @staticmethod
    def fromDb(deck: Union[str, list]) -> object:
        if isinstance(deck, str):
            return TraditionalDeck.fromDict(json.loads(deck))
        if isinstance(deck, list):
            return TraditionalDeck.fromDict(deck)
        
    @staticmethod
    def fromDict(dict) -> object:
        return TraditionalDeck([TraditionalCard.fromDict(card) for card in dict])
        

class TraditionalHand(Hand):
    def __init__(self, cards=None):
        super().__init__(cards if cards is not None else [])

    def protect(self, card:TraditionalCard):
        try:
            self.cards[self.cards.index(card)].protected = True
        except IndexError:
            print("ERROR: invalid index for protected card")
            return "non matching user input"
        return card

    @staticmethod
    def fromDb(hand: Union[str, list]) -> object:
        if isinstance(hand, str):
            return TraditionalHand.fromDict(json.loads(hand))
        if isinstance(hand, list):
            return TraditionalHand.fromDict(hand)

    @staticmethod
    def fromDict(hand) -> object:
        return TraditionalHand([TraditionalCard.fromDict(card) for card in hand])

class TraditionalPlayer(Player):
    def __init__(self, id:int, username:str, credits=0, bet:int = None, hand:Hand=Hand(), folded=False, lastAction=""):
        super().__init__(id, username, credits, bet, hand, folded, lastAction)

    def protect(self, card:TraditionalCard):
        self.hand.protect(card)
        self.lastAction = f"protected a {card.val}"

    def toDb(self):
        return json.dumps(self.toDict())

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'credits': self.credits,
            'bet': self.bet,
            'hand': self.hand.toDict(),
            'folded': self.folded,
            'lastAction': self.lastAction
        }

    @staticmethod
    def fromDb(player: Union[str, dict]) -> object:
        if isinstance(player, str):
            print("player is a string",player)
            return TraditionalPlayer.fromDict(json.loads(player))
        if isinstance(player, dict):
            return TraditionalPlayer.fromDict(player)

    @staticmethod
    def fromDict(dict: dict):
        return TraditionalPlayer(id=dict['id'],username=dict['username'],credits=dict['credits'],bet=dict['bet'],hand=TraditionalHand.fromDict(dict['hand']),folded=dict['folded'],lastAction=dict['lastAction'])

    def calcHandVal(self):
        cardVals = self.hand.getListOfVals()
        cardVals.sort()

        '''special hands'''
        # idiot's array (best)
        if cardVals == [0, 2, 3]:
            return SpecialHands.IDIOTS_ARRAY

        elif cardVals == [-2, -2]:
            return SpecialHands.FAIRY_EMPRESS

        return sum(cardVals)

# Default game settings
defaultSettings = {
    "PokerStyleBetting": False,
    "SmallBlind": 1,
    "BigBlind": 2,
    "HandPotAnte": 5,
    "SabaccPotAnte": 10,
    "StartingCredits": 1000
}

class TraditionalGame(Game):
    def __init__(self,
        players: list,
        id: int = None,
        deck = TraditionalDeck(),
        player_turn: int = None,
        p_act = '',
        hand_pot = None,
        sabacc_pot = 0,
        phase = 'betting',
        cycle_count = 0,
        shift = False,
        completed = False,
        settings = defaultSettings,
        created_at = None,
        move_history = None):

        super().__init__(
            players = players,
            id = id,
            player_turn = player_turn,
            p_act = p_act,
            deck = deck,
            phase = phase,
            cycle_count = cycle_count,
            completed = completed,
            settings = settings,
            created_at = created_at,
            move_history = move_history
        )
        self.hand_pot = hand_pot if hand_pot is not None else HandPot()
        self.sabacc_pot = sabacc_pot
        self._shift = shift

    # create a new game
    @staticmethod
    def newGame(playerIds:list, playerUsernames:list, db=None, settings=defaultSettings):

        if len(playerIds) != len(playerUsernames):
            return "Uneqal amount of ids and usernames"

        if len(playerIds) > 8:
            "Too many players. Max of 8 players."

        if len(playerIds) <= 1:
            "You cannot play by yourself"


        # create player list
        players = []
        for id in playerIds:
            players.append(TraditionalPlayer(id, username=playerUsernames[playerIds.index(id)], credits=settings["StartingCredits"]))

        # construct deck
        deck = TraditionalDeck()

        game = TraditionalGame(players=players, deck=deck, player_turn=players[0].id, settings=settings)

        game.nextRound(rotateDealer=False)

        if db:
            db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, deck, player_turn, p_act, settings) VALUES(?, ?, ?, ?, ?, ?, ?)", [game.playersToDb(), game.hand_pot.toDb(), game.sabacc_pot, game.deckToDb(), game.player_turn, game.p_act, game.settingsToDb()])

        return game

    def getVariant(self):
        return Game_Variant.TRADITIONAL

    def toDb(self, includeId=False):
        dbGame = [self.id, self.playersToDb(), self.hand_pot.toDb(), self.sabacc_pot, self.phase, self.deck.toDb(), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed, self.settingsToDb(), self.created_at, self.moveHistoryToDb()]
        if includeId == False:
            dbGame.pop(0)

        return dbGame

    def playersToDb(self):
        return json.dumps([player.toDict() for player in self.players])

    def toDict(self, noMutableReferences: bool = False):
        """
        :param noMutableReferences: set to true to deepcopy all mutable data, so you can safely mutate the resulting dictionary
        """
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot.toDict(),
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': self.deck.toDict(),
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self._shift,
            'completed': self.completed,
            'settings': copy.deepcopy(self.settings) if noMutableReferences else self.settings,
            'created_at': self.created_at,
            'move_history': copy.deepcopy(self.move_history) if noMutableReferences else self.move_history
        }

    @staticmethod
    def fromDb(game: list, preSettings=False):
        gameObj = TraditionalGame(id=game[0],players=[TraditionalPlayer.fromDb(player) for player in json.loads(game[1])], hand_pot=HandPot.fromDb(game[2]), sabacc_pot=game[3], phase=game[4], deck=TraditionalDeck.fromDb(game[5]), player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=bool(game[9]),completed=bool(game[10]),settings=defaultSettings,created_at=game[12],move_history=None if not game[13] else json.loads(game[13]))
        if preSettings == False:
            gameObj.settings = json.loads(game[11])
        return gameObj

    @staticmethod
    def fromDict(dict:dict):
        return TraditionalGame(id=dict['id'],players=[TraditionalPlayer.fromDict(player) for player in dict['players']],deck=TraditionalDeck.fromDict(dict['deck']),player_turn=dict['player_turn'],p_act=dict['p_act'],hand_pot=HandPot.fromDict(dict['hand_pot']),sabacc_pot=dict['sabacc_pot'],phase=dict['phase'],cycle_count=dict['cycle_count'],shift=dict['shift'],completed=dict['completed'],settings=dict['settings'],created_at=dict['created_at'],move_history=dict['move_history'])

    def _reshuffle(self):
        # exclude cards in (active) players' hands
        cardsToExclude = []
        for player in self.getActivePlayers():
            cardsToExclude.extend(player.hand.cards)
        self.deck = TraditionalDeck()
        for card in cardsToExclude:
            self.deck.cards.remove(card)
        self.deck.shuffle()

    # replace every unprotected card in every player's hand
    def doShift(self):
        # loop thru players
        for player in self.players:
            hand = player.hand.cards
            # loop thru cards in hand
            for i in range(len(hand)):
                if not hand[i].protected: # if card is not protected
                    hand[i] = self.drawFromDeck()

    def isSabaccHand(self, bestHand) -> bool:
        """
        Check if a hand qualifies for the sabacc pot in Traditional Sabacc.
        Sabacc hands are: Idiot's Array or a hand totaling exactly 23 or -23.
        """
        if bestHand is None:
            return False
        if bestHand == SpecialHands.IDIOTS_ARRAY:
            return True
        if bestHand == SpecialHands.FAIRY_EMPRESS:
            return False
        return abs(bestHand) == 23

    def evaluatePotWinner(self, eligiblePlayers: list, potCredits: int, suddenDemise=False):
        """
        Implementation of abstract method from Game.
        Uses Traditional Sabacc rules with sudden demise for ties.
        Handles bomb outs by penalizing players.

        Args:
            eligiblePlayers: list[Player] - players eligible for this pot
            potCredits: int - credits in this pot (for handling unclaimed pots)
            suddenDemise: bool - True if this is a recursive call for tie-breaking

        Returns: (winner, bestHand, actionStr)
        """
        # If recursion has been activated due to a tie, give each player a card
        if suddenDemise:
            for player in eligiblePlayers:
                player.hand.cards.append(self.drawFromDeck())

        # Calculate winners and losers
        winningPlayers, bestHand, bombedOutPlayers = TraditionalGame.calcWinners(eligiblePlayers)

        # Handle bomb outs (only on first call, not during sudden demise recursion)
        actionParts = []
        if not suddenDemise and len(bombedOutPlayers) > 0:
            bombOutPrice = int(round(self.hand_pot.getTotal() * 0.1))
            bombedNames = []
            for p in bombedOutPlayers:
                p.credits -= bombOutPrice
                self.sabacc_pot += bombOutPrice
                bombedNames.append(p.username)
            actionParts.append(f"{', '.join(bombedNames)} bombed out")

        # Everyone bombed out - transfer pot credits to sabacc pot
        if winningPlayers is None or len(winningPlayers) == 0:
            if potCredits > 0:
                self.sabacc_pot += potCredits
                actionParts.append(f"{potCredits} credits transferred to sabacc pot")
            return None, None, "; ".join(actionParts)

        # If there's a tie, initiate sudden demise through recursion
        if len(winningPlayers) > 1:
            tiedNames = ", ".join([p.username for p in winningPlayers])
            handStr = self._formatHandValue(bestHand)
            actionParts.append(f"{tiedNames} tied with {handStr}; sudden demise")
            sdWinner, sdBestHand, sdActionStr = self.evaluatePotWinner(winningPlayers, potCredits, suddenDemise=True)
            if sdActionStr:
                actionParts.append(sdActionStr)
            return sdWinner, sdBestHand, "; ".join(actionParts)

        # Only 1 winner - include hand info
        winner = winningPlayers[0]
        handStr = self._formatHandValue(bestHand)
        actionParts.append(f"{winner.username} won with {handStr}")
        return winner, bestHand, "; ".join(actionParts)

    def _formatHandValue(self, handValue):
        """Format a hand value for display in action strings."""
        if handValue == SpecialHands.IDIOTS_ARRAY:
            return "Idiot's Array"
        elif handValue == SpecialHands.FAIRY_EMPRESS:
            return "Fairy Empress (-22)"
        elif handValue is None:
            return "no valid hand"
        else:
            return str(handValue)

    def whoCalledAlderaan(self):
        for player in self.getActivePlayers():
            if player.lastAction == "calls Alderaan":
                return player

    @staticmethod
    def calcWinners(players) -> dict:
        bestHand = 0
        bombedOutPlayers = []
        for player in players:
            currentHand = player.calcHandVal()

            # idiot's array, unbeatable
            if currentHand == SpecialHands.IDIOTS_ARRAY:
                bestHand = currentHand
                break
            # fairy empress, beats 22 or -22
            tempCurrentHand = currentHand
            if currentHand == SpecialHands.FAIRY_EMPRESS:
                tempCurrentHand = -22

            # convert enum to int
            tempBestHand = bestHand
            if bestHand == SpecialHands.FAIRY_EMPRESS:
                tempBestHand = -22

            # check for bomb outs
            if tempCurrentHand == 0 or abs(tempCurrentHand) > 23:
                bombedOutPlayers.append(player)

            # current val better than stored val
            elif abs(tempCurrentHand) > abs(tempBestHand):
                bestHand = currentHand
            elif abs(tempCurrentHand) == abs(tempBestHand): # same abs val
                # fairy empress beats 22 or -22
                if currentHand == SpecialHands.FAIRY_EMPRESS:
                    bestHand = currentHand
                elif tempCurrentHand < tempBestHand: # if negative, beats positive
                    bestHand = currentHand

        winningPlayers = []

        # everyone bombed out
        if bestHand == 0:
            bestHand = None
        else:
            # find player(s) with the best hand
            for player in players:
                if player.calcHandVal() == bestHand:
                    winningPlayers.append(player)
        return winningPlayers, bestHand, bombedOutPlayers
    
    def getNextPhase(self):
        if self.phase == "betting":
            return "card"
        elif self.phase == "card":
            return "shift"
        elif self.phase == "shift":
            return "betting"
        # this shouldn't be used when the phase is alderaan

    def cardPhaseAction(self, params:dict, player, db):

        nextPlayer = self.getNextPlayerInPhase(player)

        if params["action"] == "quit":
            player.lastAction = "quit the game"
            self.hand_pot.removePlayerFromAll(player.id)
            self.players.remove(player)

        elif params["action"] == "draw":
            player.hand.cards.append(self.drawFromDeck())
            player.lastAction = "draws"

        elif params["action"] == "trade":
            tradeCard = TraditionalCard.fromDict(params["trade"])

            # The index of the card that is being traded
            tradeDex = player.hand.cards.index(tradeCard)

            # Draw a card and replace the card being traded with it
            player.hand.cards[tradeDex] = self.drawFromDeck()

            player.lastAction = "trades"

        elif params["action"] == "stand":
            player.lastAction = "stands"

        elif params["action"] == "alderaan" and self.cycle_count != 0:
            self.phase = "alderaan"
            player.lastAction = "calls Alderaan"


        players = self.getActivePlayers()

        # String that shows the winner
        winStr = None


        # If only one player remains, they win everything
        if len(players) == 1:
            winningPlayer = players[0]
            winningPlayer.credits += self.hand_pot.getTotal()
            self.hand_pot.reset()
            winStr = f"{winningPlayer.username} wins!"
            self.completed = True
        elif len(players) == 0:
            self.completed = True
        elif not nextPlayer:
            nextPlayer = players[0]
            if self.phase == "alderaan":
                # Evaluate all pots (handles bomb outs, awards credits, sabacc pot, sets self.p_act)
                self.evaluatePots()
                winStr = self.p_act  # evaluatePots() set this
                self.completed = True
            else:
                self.phase = "shift"

        # Update game object before db update
        self.player_turn = nextPlayer.id if nextPlayer is not None else (players[0].id if len(players) > 0 else None)
        self.p_act = player.username + " " + player.lastAction
        if winStr:
            self.p_act += "; " + winStr


        # If alderaan was called, add it to the p_act
        if params["action"] != "alderaan" and self.phase == "alderaan":
            alderaanCaller = self.whoCalledAlderaan()
            self.p_act = alderaanCaller.username + " called Alderaan; " + self.p_act

        dbList = [
            self.deck.toDb(),
            self.playersToDb(),
            self.hand_pot.toDb(),
            self.sabacc_pot,
            self.phase,
            self.player_turn,
            self.cycle_count,
            self.p_act,
            self.completed,
            self.id
        ]
        db.execute("UPDATE traditional_games SET deck = ?, players = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, player_turn = ?, cycle_count = ?, p_act = ?, completed = ? WHERE game_id = ?", dbList)

    # overrides parent method
    def action(self, params:dict, db):

        originalSelf = copy.deepcopy(self)
        player = self.getPlayer(username=params["username"])

        if params["action"] == "quit" and self.completed: # it is necessary for this conditional to be the first one
            self.quitFromCompletedGame(player, db)

        elif params['action'] == "protect":
            card = TraditionalCard.fromDict(params["protect"])
            response = player.hand.protect(card)
            if isinstance(response, str):
                return response

            # Update game object before db update
            self.p_act = f"{player.username} protected a {card.val}"

            dbList = [
                self.playersToDb(),
                self.p_act,
                self.id
            ]
            db.execute("UPDATE traditional_games SET players = ?, p_act = ? WHERE game_id = ?", dbList)

        elif (self.phase == "betting" and self.completed == False) and ((params['action'] in ["fold", "check", "bet", "call", "raise", "allIn"] and self.player_turn == player.id) or params['action'] == "quit"):
            self.betPhaseAction(params, player, db)

        elif (self.phase in ["card", "alderaan"] and self.completed == False) and ((params["action"] in ["draw", "trade", "stand", "alderaan"] and self.player_turn == player.id) or params["action"] == "quit"):
            self.cardPhaseAction(params, player, db)

        elif (self.phase == "shift" and self.completed == False) and ((params["action"] == "shift" and self.player_turn == player.id) or params["action"] == "quit"):
            self.shiftPhaseAction(params, player, db)

        elif params["action"] == "playAgain" and self.player_turn == player.id and self.completed and len(self.players) > 1:
            self.nextRound()

            dbList = [
                self.playersToDb(),
                self.hand_pot.toDb(),
                self.sabacc_pot,
                self.phase,
                self.deck.toDb(),
                self.player_turn,
                self.cycle_count,
                self.p_act,
                self.completed,
                self.id
            ]

            db.execute("UPDATE traditional_games SET players = ?, hand_pot = ?, sabacc_pot = ?, phase = ?, deck = ?, player_turn = ?, cycle_count = ?, p_act = ?, completed = ? WHERE game_id = ?", dbList)

        if self == originalSelf:
            return "invalid user input"
        
        originalChangedValues = self.compare(originalSelf)
        originalChangedValues["timestamp"] = datetime.now(timezone.utc).isoformat()
        if self.move_history:
            self.move_history.append(originalChangedValues)
        else:
            self.move_history = [originalChangedValues]

        db.execute("UPDATE traditional_games SET move_history = ? WHERE game_id = ?", [self.moveHistoryToDb(), self.id])

        return self