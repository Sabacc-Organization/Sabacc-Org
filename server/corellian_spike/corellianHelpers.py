# corellian spike helper functions

import random
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from dataHelpers import *

class Suits:
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    SYLOP = 'sylop'

class Card:
    def __init__(self, val, suit):
        self.value = val
        self.suit = suit
    def __str__(self):
        return f'{addPlusBeforeNumber(self.value)} {self.suit}'
    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

class Deck:
    def __init__(self):
        self.cards = []
        for suit in [Suits.CIRCLE,Suits.SQUARE,Suits.TRIANGLE]:
            for val in range(1, 11):
                self.cards.extend([Card(val, suit), Card(-val, suit)])
        sylop = Card(0, 'sylop')
        self.cards.extend([sylop, sylop])
        self.shuffle()
    
    def __str__(self):
        return f'[{listToStr(self.cards)}]'

    def shuffle(self):
        for i in range(len(self.cards)):
            switchIndex = random.randint(0, len(self.cards) - 1)
            temp = self.cards[switchIndex]
            self.cards[switchIndex] = self.cards[i]
            self.cards[i] = temp

    # remove a number of cards from the top (end) of the deck and return them
    def draw(self, numCards=1):
        if numCards == 1:
            return self.cards.pop()
        else:
            drawnCards = self.cards[-numCards:]
            del self.cards[-numCards:] # delete drawn cards from deck
            return drawnCards

class Hand:
    HANDS = {
        1: 'pure sabacc',
        2: 'full sabacc',
        3: 'fleet',
        4: 'full khyron',
        5: 'dual power couplings',
        6: 'akaata',
        7: 'yeeha',
        8: 'boss triad',
        9: 'rhylet',
        10: 'squadron',
        11: 'gee whiz',
        12: 'banthas wild',
        13: 'rule of 2',
        14: 'straight khyron',
        15: 'senate',
        16: 'clan',
        17: 'power coupling',
        18: 'triad',
        19: 'Nulrhek'
    }
    def __init__(self, cards=[]):
        self.cards = cards
        self.sort()
    def __str__(self):
        self.sort()
        return f'[{listToStr(self.cards)}]'
    def __eq__(self, other):
        if len(self.cards) != len(other.cards):
            return False
        for i in range(len(self.cards)):
            if self.cards[i] != other.cards[i]:
                return False
        return True
    
    def getListOfVals(self):
        return [card.value for card in self.cards]
    
    def append(self, card):
        self.cards.append(card)
    
    # sort hand by value (selection sort)
    def sort(self):
        # print(self)
        for i in range(len(self.cards) - 1):
            # print(f'\ni = {i}, hand[i] = {self.cards[i]}')
            minIndex = i
            for j in range(i+1, len(self.cards)):
                # print(f'j = {j}, hand[j] = {self.cards[j]}')
                if self.cards[j].value < self.cards[minIndex].value:
                    minIndex = j
            if minIndex != i:
                # swap min card with current one
                minCard = self.cards[minIndex]
                self.cards[minIndex] = self.cards[i]
                self.cards[i] = minCard
                # print(f'minCard: {minCard}')
                # print(f'swapped {minIndex} to {i}')
        # print()
        # print(self)
    
    def getTotal(self):
        return sum([card.value for card in self.cards])
    def getRanking(self):
        # get the values of the cards and take the absolute value (negatives don't matter here)
        vals = [abs(val) for val in self.getListOfVals()]
        vals.sort() # sort ascending

        if self.getTotal() == 0: # hands 1-18 total 0
            if 0 in vals: # hands 1-8 have a sylop
                # 1. Pure Sabacc: 2 sylops
                if vals == [0, 0]:
                    return 1
                if len(vals) == 5: # hands 2-6 have 5 cards
                    # 2-Full sabacc- sylop with 4 10s
                    if vals == [0,10,10,10,10]:
                        return 2
                    # 3-Fleet- sylop with 4 of a kind that are not 10s
                    if vals.count(vals[1]) == 4:
                        return 3
                    # 4-Full khyron- sylop with 4 cards in numerically ascending order
                    if [vals[i + 1] - vals[i] for i in range(1, 4)] == [1,1,1]:   # find differences b/w values & check that they're all 1
                        return 4
                    # 5-Dual Power Couplings- sylop with 2 pair
                    if(vals[1] == vals[2] and vals[3] == vals[4]):
                        return 5
                    # 6-Akaata- sylop with 4 cards equaling zero
                    return 6 # conditions alr met if got to this point
                # 7-Yeeha- Sylop and a pair
                if len(vals) == 3 and vals[1] == vals[2]:
                    return 7
                # 8-Boss Triad- sylop with 3 cards equaling 0
                if len(vals) == 4:
                    return 8
            # 9-Rhylet- 3 of a kind with 2 of a kind
            if len(vals) == 5 and vals[0] == vals[1] and vals[3] == vals[4] and (vals[2] == vals[1] or vals[2] == vals[3]): # check that the 1st 2 & last 2 are = and the middle one equals either the 2nd or 4th one
                return 9
            # 10-Squadron – 4 of a kind
            if len(vals) == 4 and vals.count(vals[0]) == 4:
                return 10
            # 11-Gee Whiz- 1,2,3,4 and a 10
            if vals == [1,2,3,4,10]:
                return 11
            # 12- Banthas Wild- 3 of a kind
            for val in vals:
                if vals.count(val) == 3:
                    return 12
            # 13- Rule of 2- two pair
            if len(vals) == 4 and vals[0] == vals[1] and vals[2] == vals[3]:
                return 13
            # 14-Straight Khyron- 4 cards in numerically ascending order
            if len(vals) == 4 and [vals[i + 1] - vals[i] for i in range(0, 3)] == [1,1,1]:
                return 14
            # 15-Senate- 5 random cards totaling zero
            if len(vals) == 5:
                return 15
            # 16- Clan- 4 random cards totaling zero
            if len(vals) == 4:
                return 16
            # 17- Power Coupling – a pair
            if len(vals) == 2 and vals[0] == vals[1]:
                return 17
            # 18- Triad – 3 random cards totaling zero
            if len(vals) == 3:
                return 18
            return 'error: hand total was 0 but hand did\'t match any known hand'
        else:
            return 19 # Nulrhek- Hand closest to zero

class Player:
    def __init__(self, id):
        self.id = id
        self.hand = Hand()
        self.credits = 990
        self.bet = 0
    
    def __str__(self):
        return str(self.id)
    def toString(self):
        ranking = self.hand.getRanking()
        return f'player {self.id}:\n\thand ({Hand.HANDS[ranking].capitalize()} #{ranking}): {self.hand} ({len(self.hand.cards)} cards, total: {addPlusBeforeNumber(self.hand.getTotal())})\n'
    
    # these 2 are only helper functions, you can't just draw from the deck for free
    def drawFromDeck(self, deck):
        self.hand.append(deck.draw())
    
    def drawFromDiscard(self, discardPile):
        self.hand.append(discardPile.pop()) # since new cards are added to the end, the last card is the top one
    
    # these are the 5 actions you can do on your turn
    def buyFromDeck(self, deck):
        self.drawFromDeck(deck)
        self.credits -= 5

    def buyFromDiscard(self, discardPile):
        self.drawFromDiscard(discardPile)
        self.credits -= 10

    def tradeWithDeck(self, deck, tradeCardIndex):
        self.discard(tradeCardIndex)
        self.drawFromDeck(deck)

    def tradeWithDiscard(self, discardPile, tradeCardIndex):
        self.hand.append(discardPile.pop())
        self.discard(tradeCardIndex, discardPile)

    def discard(self, discardCardIndex, discardPile):
        discardPile.append(self.hand.pop(discardCardIndex))
    
    def getIndexOfCard(self, targetCard):
        for i in range(len(self.hand)):
            if self.hand[i] == targetCard:
                return i
        return -1

class CorellianSpikeGame:
    def __init__(self, playerIds):
        self.players = []
        for id in playerIds:
            self.players.append(Player(id))
        self.newGame()
        # designate the 1st player as the 1st dealer
        self.dealer = self.players[0]
        
    def newGame(self):
        # clear players' hands
        for player in self.players:
            player.hand.cards = []
        
        # create deck, discard pile, and pots
        self.deck = Deck()
        self.discardPile = [self.deck.draw()]
        self.handPot = 5 * len(self.players)
        self.sabaccPot = 5 * len(self.players)

        # deal cards to each player
        # for i in range(1):
        for player in self.players:
            player.hand.cards = self.deck.draw(random.randint(2,5))

        # create discard pile with a card from the deck
        self.discardPile = [self.deck.draw()]

        # round number
        self.round = 1

    def playAgain(self):
        self.newGame()
        
        # rotate dealer
        self.dealer = self.players.index(self.dealer) + 1

    def getPlayerFromId(self, id):
        for player in self.players:
            if player.id == id:
                return player
    
    def shift(self):
        for player in self.players:
            # put player's cards on bottom of deck
            self.deck.cards = player.hand.cards + self.deck.cards
            # deal player as many cards as they had before
            player.hand.cards = self.deck.draw(len(player.hand.cards))
    
    def determineWinner(self):
        ret = ''
        handRankings = [player.hand.getRanking() for player in self.players]
        winningHand = min(handRankings)
        winningPlayers = []
        for player in self.players:
            if player.hand.getRanking() == winningHand:
                winningPlayers.append(player)
        
        if len(winningPlayers) == 1:
            return f'player {winningPlayers[0].id} won with a hand of {Hand.HANDS[winningHand]} (#{winningHand})'
        ret += f'{'all players' if len(winningPlayers) == len(self.players) else f'players {listToStr(winningPlayers)}'} tied with a hand of {Hand.HANDS[winningHand]} (#{winningHand})\n'
        
        ''' tie breakers '''

        if winningHand == 19:
            # closest to 0
            handTotals = [abs(player.hand.getTotal()) for player in winningPlayers]
            closestTo0 = min(handTotals)
            for i in range(len(winningPlayers) - 1, -1, -1):
                if handTotals[i] != closestTo0:
                    del winningPlayers[i]
            if len(winningPlayers) == 1:
                return ret + f'player {winningPlayers[0].id} won with a total of {addPlusBeforeNumber(winningPlayers[0].hand.getTotal())}'
            ret += f'players {listToStr(winningPlayers)} tied with a total of {closestTo0}\n'
        
        # 1-Most Cards
        numCards = [len(player.hand.cards) for player in winningPlayers]
        mostCards = max(numCards)
        for i in range(len(winningPlayers) - 1, -1, -1):
            if numCards[i] < mostCards:
                del winningPlayers[i]
        if len(winningPlayers) == 1:
            return ret + f'player {winningPlayers[0].id} won with {len(winningPlayers[0].hand.cards)} cards'
        ret += f'players {listToStr(winningPlayers)} tied with {mostCards} cards\n'
        
        # 2-Positive Score
        handTotals = [player.hand.getTotal() for player in winningPlayers]
        atLeast1Pos = max(handTotals) > 0 # at least 1 person has a positive score
        if atLeast1Pos: 
            for i in range(len(winningPlayers)-1, -1, -1):
                if handTotals[i] < 0:
                    del winningPlayers[i]
            if len(winningPlayers) == 1:
                return ret + f'player {winningPlayers[0].id} won with a positive score'
        ret += f'players {listToStr(winningPlayers)} {'both' if len(winningPlayers) == 2 else 'all'} had a {'positive' if atLeast1Pos else 'negative'} score\n'

        # 3- highest total of all positive cards
        posTotals = []
        for player in winningPlayers:
            total = 0
            for val in [card.value for card in player.hand.cards]:
                if val > 0:
                    total += val
            posTotals.append(total)
        maxPosTotal = max(posTotals)
        for i in range(len(winningPlayers)-1, -1, -1):
            if posTotals[i] != maxPosTotal:
                del winningPlayers[i]
        
        if len(winningPlayers) == 1:
            return ret + f'player {winningPlayers[0].id} won with a positive card total of {maxPosTotal}'
        ret += f'players {listToStr(winningPlayers)} tied with a positive card total of {maxPosTotal}\n'

        # 4- highest value positive card (aka highest value card)
        highestCards = [max([card.value for card in player.hand.cards]) for player in winningPlayers]
        mostHighestCard = max(highestCards)
        for i in range(len(winningPlayers)-1, -1, -1):
            if highestCards[i] != mostHighestCard:
                del winningPlayers[i]
        
        if len(winningPlayers) == 1:
            return ret + f'player {winningPlayers[0].id} won with a high card of +{mostHighestCard}'
        ret += f'players {listToStr(winningPlayers)} tied with high cards of +{mostHighestCard}\n'

        # 5- blind draw (closest to 0)
        ret += 'blind draw: '
        blindDraws = []
        while len(winningPlayers) > 1:
            closestTo0 = 0
            for i in range(len(winningPlayers)):
                drawnCard = self.deck.draw()
                val = abs(drawnCard.value)
                if i == 0 or val < closestTo0:
                    closestTo0 = val
                blindDraws.append(drawnCard)
                ret += f'player {winningPlayers[i].id} drew a {drawnCard}{', ' if i < len(winningPlayers) - 1 else ' - '}'
            for i in range(len(winningPlayers) - 1, -1, -1):
                if abs(blindDraws[i].value) != closestTo0:
                    del winningPlayers[i]
            if len(winningPlayers) > 1:
                ret += f'{'everyone' if len(winningPlayers) == len(blindDraws) else listToStr(winningPlayers)} tied with {closestTo0}s\n'
            else:
                ret += f'player {winningPlayers[0].id} won with a {closestTo0}'

        return ret

    # for testing purposes
    def __str__(self):
        ret = '\n'
        for player in self.players:
            ret += player.toString()
        ret += '\n' + self.determineWinner()
        return ret

# if the number is positive, it adds a plus in front of it (otherwise just returns the number)
def addPlusBeforeNumber(n):
    return ('+' if n > 0 else '') + str(n)

game = CorellianSpikeGame(list(range(1, 3)))
for player in game.players:
    player.hand.cards = [Card(7, Suits.CIRCLE), Card(-6, Suits.CIRCLE)]
print(game)