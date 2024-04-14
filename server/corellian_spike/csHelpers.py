# corellian spike helper functions

import random
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from dataHelpers import *

class Card:
    def __init__(self, val, suit):
        self.value = val
        self.suit = suit
    def __str__(self):
        return f'{'+' if self.value > 0 else ''}{self.value} {self.suit}'
    
    @staticmethod
    def listOfCardsToStr(cards):
        ret = '['
        for card in cards:
            ret += str(card) + ', '
        return str(ret).strip(', ') + ']'

class Deck:
    def __init__(self):
        self.cards = []
        for suit in ['circle','square','triangle']:
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

    def draw(self, numCards=1):
        if numCards == 1:
            return self.cards.pop()
        else:
            drawnCards = self.cards[-numCards:]
            del self.cards[-numCards:]
            return drawnCards

class Player:
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.credits = 990
        self.bet = 0
    
    def drawFromDeck(self, deck):
        self.hand.append(deck.draw())
    
    def drawFromDiscard(self, discardPile):
        self.hand.append(discardPile.pop()) # since new cards are added to the end, the last card is the top one
    
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
        
    def newGame(self):
        # clear players' hands
        for player in self.players:
            player.hand = []
        
        # create deck, discard pile, and pots
        self.deck = Deck()
        self.discardPile = [self.deck.draw()]
        self.handPot = 5 * len(self.players)
        self.sabaccPot = 5 * len(self.players)

        # deal 2 cards to each player
        for i in range(2):
            for player in self.players:
                player.hand.append(self.deck.draw())
        
        # create discard pile with a card from the deck
        self.discardPile = [self.deck.draw()]

        self.round = 1 # round number

        # designate the 1st player as the 1st dealer
        self.dealerId = self.players[0].id
    
    def shift(self):
        for player in self.players:
            # put player's cards on bottom of deck
            self.deck.cards = player.hand + self.deck.cards
            # deal player as many cards as they had before
            player.hand = self.deck.draw(len(player.hand))
    
    def __str__(self):
        ret = f'\ndeck ({len(self.deck.cards)}): {self.deck}\n'
        ret += f'discard pile ({len(self.discardPile)}): {Card.listOfCardsToStr(self.discardPile)}\n'
        for player in self.players:
            ret += f'player {player.id} hand: {Card.listOfCardsToStr(player.hand)}\n'
        return ret
