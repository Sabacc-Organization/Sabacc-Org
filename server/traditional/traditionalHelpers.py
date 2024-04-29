import random
from enum import Enum

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

class Card:
    def __init__(self, val:int, suit:Suit, protected=False):
        self.val = val
        self.suit = suit
        self.protected = protected
    def __eq__(self, other) -> bool:
        return self.val == other.val and self.suit == other.suit
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
        return Card(card.val, card.suit, card.protected)
    @staticmethod
    def fromDict(dict):
        return Card(dict['val'],dict['suit'],dict['prot'])
    @staticmethod
    def randCardNotInList(val:int, protected=False, unallowedCards=[]):
        card = None
        if val <= 0:
            card = Card(val=val, suit=Suit.NEGATIVE_NEUTRAL, protected=protected)
            if unallowedCards.count(card) > 1:
                print(f"WARNING: more than 2 {val}'s exist")
        else: # positive val
            allowedSuits = [Suit.COINS, Suit.FLASKS, Suit.SABERS, Suit.STAVES]
            for c in unallowedCards:
                if c.val == val and c.suit in allowedSuits:
                    allowedSuits.remove(c.suit)
            if len(allowedSuits) == 0:
                print(f"WARNING: more than 4 {val}'s exist")
                card = Card(val=val,suit=random.choice([Suit.COINS, Suit.FLASKS, Suit.SABERS, Suit.STAVES]),protected=protected)
            else:
                card = Card(val=val,suit=random.choice(allowedSuits), protected=protected)
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
        return Player(player.id, player.username, player.credits, player.bet, [Card.fromDb(card) for card in player.hand], player.folded, player.lastaction)
    @staticmethod
    def fromDict(dict:dict):
        return Player(id=dict['id'],username=dict['username'],credits=dict['credits'],bet=dict['bet'],hand=[Card.fromDict(card) for card in dict['hand']],folded=dict['folded'],lastAction=dict['lastAction'])
    
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
        
    
class Game:
    def __init__(self, players:list, id:int=None, deck:list=None, player_turn:int=None, p_act='', hand_pot=0, sabacc_pot=0, phase='betting', cycle_count=0, shift=False, completed=False):
        self.id = id
        self.players = players
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self.phase = phase
        self.deck = deck
        self.player_turn = player_turn
        self.p_act = p_act
        self.cycle_count = cycle_count
        self._shift = shift
        self.completed = completed
    # create a new game
    @staticmethod
    def newGame(players:list,startingCredits=1000,hand_pot_ante=5,sabacc_pot_ante=10):
        # give each player credits
        for player in players:
            player.credits = startingCredits - hand_pot_ante - sabacc_pot_ante
        # construct deck
        deck = Game.newDeck()
        
        game = Game(players=players,deck=deck,player_turn=players[0].id,hand_pot=hand_pot_ante*len(players),sabacc_pot=sabacc_pot_ante*len(players))
        game.shuffleDeck()
        game.dealHands()
        
        return game
    @staticmethod
    def newDeck(cardsToExclude:list=[]):
        deck = 2 * [
            Card(-11,Suit.NEGATIVE_NEUTRAL),
            Card(0,Suit.NEGATIVE_NEUTRAL),
            Card(-8,Suit.NEGATIVE_NEUTRAL),
            Card(-14,Suit.NEGATIVE_NEUTRAL),
            Card(-15,Suit.NEGATIVE_NEUTRAL),
            Card(-2,Suit.NEGATIVE_NEUTRAL),
            Card(-13,Suit.NEGATIVE_NEUTRAL),
            Card(-17,Suit.NEGATIVE_NEUTRAL)
        ]
        for suit in [Suit.COINS,Suit.FLASKS,Suit.SABERS,Suit.STAVES]:
            for val in range(1,16):
                deck.append(Card(val=val,suit=suit))
        for card in cardsToExclude:
            deck.remove(card)
        return deck
    def dealHands(self):
        for player in self.players:
            player.hand = [self.drawFromDeck(),self.drawFromDeck()]

    def toDb(self, card_type, player_type):
        return [self.id, self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deckToDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed]
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
        return Game(id=game[0],players=[Player.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=[Card.fromDb(card) for card in game[5]], player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10])
    @staticmethod
    def fromDict(dict:dict):
        return Game(id=dict['id'],players=[Player.fromDict(player) for player in dict['players']],deck=[Card.fromDict(card) for card in dict['deck']],player_turn=dict['player_turn'],p_act=dict['p_act'],hand_pot=dict['hand_pot'],sabacc_pot=dict['sabacc_pot'],phase=dict['phase'],cycle_count=dict['cycle_count'],shift=dict['shift'],completed=dict['completed'])

    def getActivePlayers(self):
        activePlayers = []
        for player in self.players:
            if not player.folded:
                activePlayers.append(player)
        return activePlayers

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
            self.deck = Game.newDeck(cardsToExclude=cardsToExclude)
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
    
    # sets up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= 15 # Make users pay Sabacc and Hand pot Antes
            player.bet = 0 # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Update pots
        self.hand_pot = 5 * len(self.players)
        self.sabacc_pot += 10 * len(self.players)

        # construct deck and deal hands
        self.deck = Game.newDeck()
        self.dealHands()

    def alderaan(self, suddenDemise=False, sdPlayers:list=[]):
        # If recursion has been activated due to a tie, and there is sudden demise
        if suddenDemise == True:
            # Give each participant in the sudden demise a card
            for player in sdPlayers:
                player.hand.append(self.drawFromDeck())
        
        # calculate winners and losers
        winningPlayers, bestHand, bombedOutPlayers = Game.calcWinners(sdPlayers) if suddenDemise else Game.calcWinners(self.players)

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