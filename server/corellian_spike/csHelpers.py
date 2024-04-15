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

    @staticmethod
    def listOfCardsToStr(cards):
        ret = '['
        for card in cards:
            ret += str(card) + ','
        return str(ret).strip(',') + ']'

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
        return Card.listOfCardsToStr(self.cards)

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
    def __init__(self, cards=[]):
        self.cards = cards
        self.sort()
    def __str__(self):
        self.sort()
        return Card.listOfCardsToStr(self.cards)
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
        self.sort()
        vals = self.getListOfVals()
        print(vals)

        if self.getTotal() == 0: # hands 1-18 total 0
            if 0 in vals: # hands 1-8 have a sylop
                # 1. Pure Sabacc: 2 sylops
                if vals == [0, 0]:
                    return 1
                if len(vals) == 5: # hands 2-6 have 5 cards
                    # 2-Full sabacc- sylop with 4 10s
                    if vals == [-10,-10,0,10,10]:
                        return 2
                    # 3-Fleet- sylop with 4 of a kind that are not 10s
                    if len(vals) == 5 and vals[0] == vals[1] and vals[3] == vals[4] and vals[0] == -vals[3]:
                        return 3
                    # 4-Full khyron- sylop with 4 cards in numerically ascending order
                    copy = vals                     # make a copy so don't mess up orig
                    copy = [abs(n) for n in copy]   # take absolute val of all values
                    copy.sort()                     # sort in ascending order
                    del copy[0]                     # delete sylop in 1st spot
                    if [copy[i + 1] - copy[i] for i in range(0, 3)] == [1,1,1]:            # find differences b/w values & check that they're all 1
                        return 4
                    # 5-Dual Power Couplings- sylop with 2 pair
                    if(vals[0] == -vals[4] and vals[1] == -vals[3]):
                        return 5
                    # 6-Akaata- sylop with 4 cards equaling zero
                    return 6
                # 7-Yeeha- Sylop and a pair
                if len(vals) == 3 and vals[0] == -vals[2]:
                    return 7
                # 8-Boss Triad- sylop with 3 cards equaling 0
                if len(vals) == 4:
                    return 8
            # 9-Rhylet- 3 of a kind with 2 of a kind
            # todo
        else:
            return 19

class Player:
    def __init__(self, id):
        self.id = id
        self.hand = Hand()
        self.credits = 990
        self.bet = 0
    
    def __str__(self):
        return f'player {self.id}:\n\tcredits: {self.credits}\n\thand ({addPlusBeforeNumber(self.hand.getTotal())}): {self.hand}\n'
    
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

        # deal 2 cards to each player
        for i in range(3):
            for player in self.players:
                player.hand.cards.append(self.deck.draw())

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
            self.deck.cards = player.hand + self.deck.cards
            # deal player as many cards as they had before
            player.hand = self.deck.draw(len(player.hand))
    
    # for testing purposes
    def __str__(self):
        ret = f'\ndeck ({len(self.deck.cards)}): {self.deck}\n'
        ret += f'discard pile ({len(self.discardPile)}): {Card.listOfCardsToStr(self.discardPile)}\n\n'
        for player in self.players:
            ret += str(player)
        return ret

# if the number is positive, it adds a plus in front of it (otherwise just returns the number)
def addPlusBeforeNumber(n):
    return ('+' if n > 0 else '') + str(n)

game = CorellianSpikeGame([1,2])
player1 = game.players[0]
sylop = Card(0, Suits.SYLOP)
player1.hand.cards = [sylop, Card(3, Suits.CIRCLE), Card(-2, Suits.CIRCLE), Card(-1, Suits.CIRCLE)]
print(player1.hand)
print(player1.hand.getRanking())