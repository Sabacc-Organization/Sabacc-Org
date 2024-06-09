import random
from enum import Enum
from helpers import *

class Suit:
    COINS = 'coins'
    FLASKS = 'flasks'
    SABERS = 'sabers'
    STAVES = 'staves'
    NEGATIVE_NEUTRAL = 'negative/neutral'
    ALL = [COINS, FLASKS, SABERS, STAVES]
    @staticmethod
    def random(val=None):
        return random.choice(Suit.ALL)

class SpecialHands(Enum):
    IDIOTS_ARRAY = 230
    FAIRY_EMPRESS = -22

class TraditionalCard(Card):
    def __init__(self, val:int, suit:Suit, protected=False):
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
        return TraditionalCard(card.val, card.suit, card.protected)
    @staticmethod
    def fromDict(dict):
        return TraditionalCard(dict['val'],dict['suit'],dict['prot'])
    @staticmethod
    def randCardNotInList(val:int, protected=False, unallowedCards=[]):
        card = None
        if val <= 0:
            card = TraditionalCard(val=val, suit=Suit.NEGATIVE_NEUTRAL, protected=protected)
            if unallowedCards.count(card) > 1:
                print(f"WARNING: more than 2 {val}'s exist")
        else: # positive val
            allowedSuits = [Suit.COINS, Suit.FLASKS, Suit.SABERS, Suit.STAVES]
            for c in unallowedCards:
                if c.val == val and c.suit in allowedSuits:
                    allowedSuits.remove(c.suit)
            if len(allowedSuits) == 0:
                print(f"WARNING: more than 4 {val}'s exist")
                card = TraditionalCard(val=val,suit=random.choice([Suit.COINS, Suit.FLASKS, Suit.SABERS, Suit.STAVES]),protected=protected)
            else:
                card = TraditionalCard(val=val,suit=random.choice(allowedSuits), protected=protected)
        return card

class Player:
    def __init__(self, id:int, username='', credits=0, bet:int = None, hand:list=[], folded=False, lastAction=""):
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
        self.hand = hand
        self.folded = folded
        self.lastAction = lastAction
    def toDb(self, playerType, cardType):
        for i in range(len(self.hand)):
            self.hand[i] = self.hand[i].toDb(cardType)
        return playerType.python_type(self.id, self.username, self.credits, self.bet, self.hand, self.folded, self.lastAction)
    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'credits': self.credits,
            'bet': self.bet,
            'hand': [card.toDict() for card in self.hand],
            'folded': self.folded,
            'lastAction': self.lastAction
        }
    @staticmethod
    def fromDb(player:object):
        return Player(player.id, player.username, player.credits, player.bet, [TraditionalCard.fromDb(card) for card in player.hand], player.folded, player.lastaction)
    @staticmethod
    def fromDict(dict:dict):
        return Player(id=dict['id'],username=dict['username'],credits=dict['credits'],bet=dict['bet'],hand=[TraditionalCard.fromDict(card) for card in dict['hand']],folded=dict['folded'],lastAction=dict['lastAction'])
    
    def calcHandVal(self):
        cardVals = [card.val for card in self.hand]
        cardVals.sort()

        '''special hands'''
        # idiot's array (best)
        if cardVals == [0, 2, 3]:
            return SpecialHands.IDIOTS_ARRAY
        elif cardVals == [-2, -2]:
            return SpecialHands.FAIRY_EMPRESS
        
        return sum(cardVals)
    
    def getBet(self) -> int:
        return self.bet if self.bet != None else 0
        
    def fold(self):
        self.credits += self.getBet()
        self.bet = None
        self.folded = True
    
    def makeBet(self, creditAmount: int, absolute: bool = True):
        if absolute:
            self.credits -= creditAmount - self.getBet()
            self.bet = creditAmount
        else:
            self.bet = self.bet if creditAmount == 0 else self.getBet()
            self.credits -= creditAmount
            self.bet += creditAmount

class TraditionalGame(Game):
    handPotAnte = 5
    sabaccPotAnte = 10

    def __init__(self, players:list, id:int=None, deck:list=None, player_turn:int=None, p_act='', hand_pot=0, sabacc_pot=0, phase='betting', cycle_count=0, shift=False, completed=False):
        super().__init__(players=players, id=id, player_turn=player_turn, p_act=p_act, deck=deck, phase=phase, cycle_count=cycle_count, completed=completed)
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self._shift = shift

    # create a new game
    @staticmethod
    def newGame(playerIds:list, startingCredits=1000):
        # create player list
        players = []
        for id in playerIds:
            players.append(Player(id, credits=startingCredits - TraditionalGame.handPotAnte - TraditionalGame.sabaccPotAnte))

        # construct deck
        deck = TraditionalGame.newDeck()

        game = TraditionalGame(players=players, deck=deck, player_turn=players[0].id, hand_pot=TraditionalGame.handPotAnte*len(players), sabacc_pot=TraditionalGame.sabaccPotAnte*len(players))
        game.shuffleDeck()
        game.dealHands()

        return game
    
    # sets up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= (TraditionalGame.sabaccPotAnte + TraditionalGame.handPotAnte) # Make users pay Sabacc and Hand pot Antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Update pots
        self.hand_pot = TraditionalGame.handPotAnte * len(self.players)
        self.sabacc_pot += TraditionalGame.sabaccPotAnte * len(self.players)

        # construct deck and deal hands
        self.deck = TraditionalGame.newDeck()
        self.shuffleDeck()
        self.dealHands()

    @staticmethod
    def newDeck(cardsToExclude:list=[]):
        deck = 2 * [
            TraditionalCard(-11,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(0,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-8,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-14,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-15,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-2,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-13,Suit.NEGATIVE_NEUTRAL),
            TraditionalCard(-17,Suit.NEGATIVE_NEUTRAL)
        ]
        for suit in [Suit.COINS,Suit.FLASKS,Suit.SABERS,Suit.STAVES]:
            for val in range(1,16):
                deck.append(TraditionalCard(val=val,suit=suit))
        for card in cardsToExclude:
            deck.remove(card)
        return deck
    def dealHands(self):
        for player in self.players:
            player.hand = [self.drawFromDeck(),self.drawFromDeck()]

    def toDb(self, card_type, player_type, includeId=False):
        if includeId:
            return [self.id, self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deckToDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed]
        elif includeId == False:
            return [self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deckToDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed]
    def deckToDb(self, card_type):
        return [card.toDb(card_type) for card in self.deck]
    def playersToDb(self, player_type, card_type):
        return [player.toDb(player_type, card_type) for player in self.players]
    def toDict(self):
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot,
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': [card.toDict() for card in self.deck],
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self._shift,
            'completed': self.completed
        }
    @staticmethod
    def fromDb(game:object):
        return TraditionalGame(id=game[0],players=[Player.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=[TraditionalCard.fromDb(card) for card in game[5]], player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10])
    @staticmethod
    def fromDict(dict:dict):
        return TraditionalGame(id=dict['id'],players=[Player.fromDict(player) for player in dict['players']],deck=[TraditionalCard.fromDict(card) for card in dict['deck']],player_turn=dict['player_turn'],p_act=dict['p_act'],hand_pot=dict['hand_pot'],sabacc_pot=dict['sabacc_pot'],phase=dict['phase'],cycle_count=dict['cycle_count'],shift=dict['shift'],completed=dict['completed'])

    def shuffleDeck(self):
        for i in range(len(self.deck)):
            randomIndex = random.randint(0, len(self.deck) - 1)
            temp = self.deck[randomIndex]
            self.deck[randomIndex] = self.deck[i]
            self.deck[i] = temp
    def drawFromDeck(self):
        # if deck is empty, reshuffle
        if len(self.deck) == 0:
            # exclude cards in (active) players' hands
            cardsToExclude = []
            for player in self.getActivePlayers():
                cardsToExclude.extend(player.hand)
            self.deck = TraditionalGame.newDeck(cardsToExclude=cardsToExclude)
            self.shuffleDeck()
        return self.deck.pop()
    
    # replace every unprotected card in every player's hand
    def shift(self):
        # loop thru players
        for player in self.players:
            hand = player.hand
            # loop thru cards in hand
            for i in range(len(hand)):
                if not hand[i].protected: # if card is not protected
                    hand[i] = self.drawFromDeck()
    
    def alderaan(self, suddenDemise=False, sdPlayers:list=[]):
        # If recursion has been activated due to a tie, and there is sudden demise
        if suddenDemise == True:
            # Give each participant in the sudden demise a card
            for player in sdPlayers:
                player.hand.append(self.drawFromDeck())
        
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
                pass

            # current val better than stored val
            if abs(tempCurrentHand) > abs(tempBestHand):
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
