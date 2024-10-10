import random
from enum import Enum
from helpers import *
import copy
import json
from datetime import datetime, timezone

traditionalCardType = None
traditionalPlayerType = None

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

    def toDb(self, cardType):
        return cardType.python_type(self.val, self.suit, self.protected)
    
    def toDict(self) -> dict:
        return {
            'val': self.val,
            'suit': self.suit,
            'prot': self.protected
        }
    @staticmethod
    def fromDb(card):
        a = TraditionalCard(card.val, card.suit, card.protected)
        return a
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
    def __init__(self, cardsToExclude:list=[]):
        super().__init__()
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
        for card in cardsToExclude:
            self.cards.remove(card)
        self.shuffle()
    
    @staticmethod
    def fromDb(deck) -> object:
        return TraditionalDeck([TraditionalCard.fromDb(card) for card in deck])

    def toDb(self, card_type):
        return [card.toDb(card_type) for card in self.cards]

class TraditionalHand(Hand):
    def __init__(self, cards=[]):
        super().__init__(cards)

    def protect(self, card:TraditionalCard):
        try:
            self.cards[self.cards.index(card)].protected = True
        except IndexError:
            print("ERROR: invalid index for protected card")
            return "non matching user input"
        return card
    
    @staticmethod
    def fromDb(hand) -> object:
        return TraditionalHand([TraditionalCard.fromDb(card) for card in hand])
    @staticmethod
    def fromDict(hand) -> object:
        return TraditionalHand([TraditionalCard.fromDict(card) for card in hand])

class TraditionalPlayer(Player):
    def __init__(self, id:int, username:str, credits=0, bet:int = None, hand:Hand=Hand(), folded=False, lastAction=""):
        super().__init__(id, username, credits, bet, hand, folded, lastAction)
    
    def protect(self, card:TraditionalCard):
        self.hand.protect(card)
        self.lastAction = f"protected a {card.val}"

    def toDb(self, playerType, cardType):
        # for i in range(len(self.hand.cards)):
        #     self.hand.cards[i] = self.hand.cards[i].toDb(cardType)
        return playerType.python_type(self.id, self.username, self.credits, self.bet, [card.toDb(cardType) for card in self.hand.cards], self.folded, self.lastAction)
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
    def fromDb(player:object):
        return TraditionalPlayer(player.id, player.username, player.credits, player.bet, TraditionalHand.fromDb(player.hand), player.folded, player.lastaction)
    @staticmethod
    def fromDict(dict:dict):
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
    
defaultSettings = { 
    "PokerStyleBetting": False, 
    "SmallBlind": 1, 
    "BigBlind": 2, 
    "HandPotAnte": 5, 
    "SabaccPotAnte": 10, 
    "StartingCredits": 1000 
}

class TraditionalGame(Game):
    def __init__(self, players:list, id:int=None, deck=TraditionalDeck(), player_turn:int=None, p_act='', hand_pot=0, sabacc_pot=0, phase='betting', cycle_count=0, shift=False, completed=False, settings=defaultSettings, created_at=None, move_history=None):
        super().__init__(players=players, id=id, player_turn=player_turn, p_act=p_act, deck=deck, phase=phase, cycle_count=cycle_count, completed=completed, settings=settings, created_at=created_at, move_history=move_history)
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self._shift = shift
        self.settings = settings
        self.created_at = created_at
        self.move_history = move_history

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
            players.append(TraditionalPlayer(id, username=playerUsernames[playerIds.index(id)], credits=settings["StartingCredits"] - settings["HandPotAnte"] - settings["SabaccPotAnte"]))

        # construct deck
        deck = TraditionalDeck()

        game = TraditionalGame(players=players, deck=deck, player_turn=players[0].id, hand_pot=settings["HandPotAnte"]*len(players), sabacc_pot=settings["SabaccPotAnte"]*len(players))
        
        # Blinds
        if settings["PokerStyleBetting"]:
            activePlayers = game.getActivePlayers()

            smallBlind = activePlayers[1 % len(activePlayers)]
            smallBlind.bet = settings["SmallBlind"]
            smallBlind.credits -= settings["SmallBlind"]

            bigBlind = activePlayers[2 % len(activePlayers)]
            bigBlind.bet = settings["BigBlind"]
            bigBlind.credits -= settings["BigBlind"]
            game.player_turn = bigBlind.id
        
        # Deal
        game.shuffleDeck()
        game.dealHands()

        if db:
            db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, deck, player_turn, p_act, settings) VALUES(%s, %s, %s, %s, %s, %s, %s)", [game.playersToDb(player_type=traditionalPlayerType,card_type=traditionalCardType), game.hand_pot, game.sabacc_pot, game.deckToDb(traditionalCardType), game.player_turn, game.p_act, json.dumps(settings)])

        return game
    
    # sets up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= (self.settings["HandPotAnte"] + self.settings["SabaccPotAnte"]) # Make users pay Sabacc and Hand pot Antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Antes (Pots)
        self.hand_pot = self.settings["HandPotAnte"] * len(self.players)
        self.sabacc_pot += self.settings["SabaccPotAnte"] * len(self.players)

        # Blinds
        if self.settings["PokerStyleBetting"]:
            activePlayers = self.getActivePlayers()
            
            smallBlind = activePlayers[1 % len(activePlayers)]
            smallBlind.bet = self.settings["SmallBlind"]
            smallBlind.credits -= self.settings["SmallBlind"]

            bigBlind = activePlayers[2 % len(activePlayers)]
            bigBlind.bet = self.settings["BigBlind"]
            bigBlind.credits -= self.settings["BigBlind"]
            self.player_turn = bigBlind.id

        # construct deck and deal hands
        self.deck = TraditionalDeck()
        self.shuffleDeck()
        self.dealHands()

    def dealHands(self):
        for player in self.players:
            player.hand.cards = [self.drawFromDeck(),self.drawFromDeck()]

    def toDb(self, card_type, player_type, includeId=False):
        if includeId:
            return [self.id, self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deck.toDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed, json.dumps(self.settings), self.created_at, self.moveHistoryToDb()]
        elif includeId == False:
            return [self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deck.toDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed, json.dumps(self.settings), self.moveHistoryToDb()]
    def playersToDb(self, player_type, card_type):
        return [player.toDb(player_type, card_type) for player in self.players]
    def toDict(self):
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot,
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': self.deck.toDict(),
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self._shift,
            'completed': self.completed,
            'settings': self.settings,
            'created_at': self.created_at,
            'move_history': self.move_history
        }
    @staticmethod
    def fromDb(game:object, preSettings=False):
        if preSettings:
            return TraditionalGame(id=game[0],players=[TraditionalPlayer.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=TraditionalDeck.fromDb(game[5]), player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10],settings=defaultSettings)
        return TraditionalGame(id=game[0],players=[TraditionalPlayer.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=TraditionalDeck.fromDb(game[5]), player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10],settings=game[11],created_at=game[12],move_history=game[13])
    @staticmethod
    def fromDict(dict:dict):
        return TraditionalGame(id=dict['id'],players=[TraditionalPlayer.fromDict(player) for player in dict['players']],deck=TraditionalDeck.fromDict(dict['deck']),player_turn=dict['player_turn'],p_act=dict['p_act'],hand_pot=dict['hand_pot'],sabacc_pot=dict['sabacc_pot'],phase=dict['phase'],cycle_count=dict['cycle_count'],shift=dict['shift'],completed=dict['completed'],settings=dict['settings'],created_at=dict['created_at'],move_history=dict['move_history'])

    def drawFromDeck(self):
        # if deck is empty, reshuffle
        if len(self.deck.cards) == 0:
            # exclude cards in (active) players' hands
            cardsToExclude = []
            for player in self.getActivePlayers():
                cardsToExclude.extend(player.hand.cards)
            self.deck = TraditionalDeck(cardsToExclude=cardsToExclude)
            self.deck.shuffle()
        return self.deck.draw()

    # replace every unprotected card in every player's hand
    def shift(self):
        # loop thru players
        for player in self.players:
            hand = player.hand.cards
            # loop thru cards in hand
            for i in range(len(hand)):
                if not hand[i].protected: # if card is not protected
                    hand[i] = self.drawFromDeck()
    
    def alderaan(self, suddenDemise=False, sdPlayers:list=[]):
        # If recursion has been activated due to a tie, and there is sudden demise
        if suddenDemise == True:
            # Give each participant in the sudden demise a card
            for player in sdPlayers:
                player.hand.cards.append(self.drawFromDeck())
        
        # calculate winners and losers
        winningPlayers, bestHand, bombedOutPlayers = TraditionalGame.calcWinners(sdPlayers) if suddenDemise else TraditionalGame.calcWinners(self.players)

        winner = None

        # everyone bombed out
        if winningPlayers == None:
            bestHand = None

        # if there's a tie, initiate sudden demise through recursion
        if len(winningPlayers) > 1:
            return self.alderaan(suddenDemise=True, sdPlayers=winningPlayers)
        
        # only 1 winner
        if len(winningPlayers) == 1:
            winner = winningPlayers[0]
        
        return winner, bestHand, bombedOutPlayers
        
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

    def betPhaseAction(self, params:dict, player, db):
        players = self.getActivePlayers()
        if params['action'] == "fold":
            if self.settings["PokerStyleBetting"]:
                self.hand_pot += player.getBet()
            player.fold(self.settings["PokerStyleBetting"])

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


        players = self.getActivePlayers()

        nextPlayer = None

        if not self.settings["PokerStyleBetting"]:
            betAmount = [i.getBet() for i in self.players]
            betAmount.append(0)
            betAmount = max(betAmount)
            for i in players:
                iBet = i.bet if i.bet != None else -1
                if iBet < betAmount:
                    nextPlayer = i.id
                    break
        elif self.settings["PokerStyleBetting"]:
            if self.getNextPlayer(player).getBet() < self.getGreatestBet() or self.getNextPlayer(player).bet == None:
                nextPlayer = self.getNextPlayer(player).id

        if len(players) <= 1:
            winningPlayer = players[0]
            winningPlayer.credits += self.hand_pot + winningPlayer.bet
            self.hand_pot = 0
            winningPlayer.bet = None

        if nextPlayer == None:
            # add all bets to hand pot
            for p in players:
                self.hand_pot += p.getBet()
                p.bet = None

        # Update game object before db update
        self.phase = 'betting' if nextPlayer != None else 'card'
        self.player_turn = nextPlayer if nextPlayer != None else players[0].id
        self.p_act = player.username + " " + player.lastAction
        self.completed = len(players) <= 1

        dbList = [
            self.playersToDb(traditionalPlayerType, traditionalCardType),
            self.hand_pot,
            self.phase,
            self.player_turn,
            self.p_act,
            self.completed,
            self.id
        ]
        db.execute("UPDATE traditional_games SET players = %s, hand_pot = %s, phase = %s, player_turn = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)

    def cardPhaseAction(self, params:dict, player, db):
        players = self.getActivePlayers()

        if params["action"] == "draw":
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



        # Pass turn to next player
        uDex = players.index(player)
        nextPlayer = uDex + 1

        # String that shows the winner
        winStr = None

        # If this action was from the last player
        if nextPlayer == len(players):
            nextPlayer = 0
            if self.phase == "alderaan":
                self.phase = "card"
                # Get end of game data
                winner, bestHand, bombedOutPlayers = self.alderaan()

                # Enact the bomb out transactions for all players that bombed out
                bombOutPrice = int(round(self.hand_pot * .1))
                for p in bombedOutPlayers:
                    p.credits -= bombOutPrice
                    self.sabacc_pot += bombOutPrice


                # If someone won (i.e. not everyone bombed out)
                if winner != None:
                    # Give winner Hand Pot
                    winner.credits += self.hand_pot
                    self.hand_pot = 0

                    # Give winner Sabacc Pot it they had a Sabacc
                    if bestHand == SpecialHands.IDIOTS_ARRAY or (bestHand != SpecialHands.FAIRY_EMPRESS and abs(bestHand) == 23):
                        winner.credits += self.sabacc_pot
                        self.sabacc_pot = 0

                    # Update game and winner string
                    winStr = f"{winner.username} wins!"

                    self.completed = True

                # If no one won (i.e. everyone bombed out)
                else:
                    # Hand pot gets added to Sabacc Pot
                    self.sabacc_pot += self.hand_pot

                    # Update winStr
                    winStr = "Everyone bombs out and loses!"

            else:
                self.phase = "shift"
                self.cycle_count += 1

        # Update game object before db update
        self.player_turn = self.getActivePlayers()[nextPlayer].id
        self.p_act = player.username + " " + player.lastAction if not winStr else winStr

        dbList = [
            self.deck.toDb(traditionalCardType),
            self.playersToDb(traditionalPlayerType, traditionalCardType),
            self.hand_pot,
            self.sabacc_pot,
            self.phase,
            self.player_turn,
            self.cycle_count,
            self.p_act,
            self.completed,
            self.id
        ]
        db.execute("UPDATE traditional_games SET deck = %s, players = %s, hand_pot = %s, sabacc_pot = %s, phase = %s, player_turn = %s, cycle_count = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)

    # overrides parent method
    def action(self, params:dict, db):

        originalSelf = copy.deepcopy(self)
        player = self.getPlayer(username=params["username"])
        if params['action'] == "protect":
            card = TraditionalCard.fromDict(params["protect"])
            response = player.hand.protect(card)
            if isinstance(response, str):
                return response

            # Update game object before db update
            self.p_act = f"{player.username} protected a {card.val}"

            dbList = [
                self.playersToDb(traditionalPlayerType, traditionalCardType),
                self.p_act,
                self.id
            ]
            db.execute("UPDATE traditional_games SET players = %s, p_act = %s WHERE game_id = %s", dbList)

        elif params['action'] in ["fold", "check", "bet", "call", "raise"] and self.phase == "betting" and self.player_turn == player.id and self.completed == False:
            self.betPhaseAction(params, player, db)

        elif params["action"] in ["draw", "trade", "stand", "alderaan"] and self.phase in ["card", "alderaan"] and self.player_turn == player.id and self.completed == False:
            self.cardPhaseAction(params, player, db)

        elif params["action"] == "shift" and self.player_turn == player.id and self.completed == False:
            self._shift = self.rollShift()

            if self._shift:
                self.shift()

            # Set the Shift message
            shiftStr = "Sabacc shift!" if self._shift else "No shift!"

            # Update game object before db update
            self.phase = "betting"
            self.player_turn = self.getActivePlayers()[0].id
            self.p_act = shiftStr

            dbList = [
                self.phase,
                self.deck.toDb(traditionalCardType),
                self.playersToDb(traditionalPlayerType, traditionalCardType),
                self.player_turn,
                self._shift,
                self.p_act,
                self.id
            ]

            db.execute(f"UPDATE traditional_games SET phase = %s, deck = %s, players = %s, player_turn = %s, shift = %s, p_act = %s WHERE game_id = %s", dbList)

        elif params["action"] == "playAgain" and self.player_turn == player.id and self.completed:
            self.nextRound()

            # Update game object before db update
            self.phase = "betting"
            self.cycle_count = 0
            self.p_act = ""
            self.completed = False

            dbList = [
                self.playersToDb(traditionalPlayerType, traditionalCardType),
                self.hand_pot,
                self.sabacc_pot,
                self.phase,
                self.deck.toDb(traditionalCardType),
                self.player_turn,
                self.cycle_count,
                self.p_act,
                self.completed,
                self.id
            ]

            db.execute("UPDATE traditional_games SET players = %s, hand_pot = %s, sabacc_pot = %s, phase = %s, deck = %s, player_turn = %s, cycle_count = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)

        if self == originalSelf:
            return "invalid user input"
        
        originalChangedValues = self.compare(originalSelf)
        originalChangedValues["timestamp"] = datetime.now(timezone.utc).isoformat()
        if self.move_history:
            self.move_history.append(originalChangedValues)
        else:
            self.move_history = [originalChangedValues]

        db.execute("UPDATE traditional_games SET move_history = %s WHERE game_id = %s", [self.moveHistoryToDb(), self.id])

        return self