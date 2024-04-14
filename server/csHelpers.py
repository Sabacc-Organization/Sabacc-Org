# corellian spike helper functions

import random
from dataHelpers import *

class Card:
    def __init__(self, val, suit):
        self.value = val
        self.suit = suit
    def __str__(self):
        return f'{'+' if self.value > 0 else ''}{self.value} {self.suit}'

class Deck:
    def __init__(self):
        self.constructDeck()
    
    def constructDeck(self):
        self.cards = []
        for suit in ['circle','square','triangle']:
            for val in range(1, 11):
                self.cards.extend([Card(val, suit), Card(-val, suit)])
        sylop = Card(0, 'sylop')
        self.cards.extend([sylop, sylop])
    
    def __str__(self):
        ret = []
        for card in self.cards:
            ret.append(str(card))
        return str(ret)

    def draw(self):
        return self.cards.pop(random.randint(0, len(self.cards) - 1))

# deal hands to each player
def dealHands(deck, playerCount):
    # Draw 2 cards for every hand
    hands = []
    for i in range(playerCount):
        hands.append([deck.draw(), deck.draw()])
    return hands

def newGame(players):
    hPot = 0
    sPot = 0
    credits = ''
    for i in range(len(players)):
        credits += '985,'
        hPot += 5
        sPot += 10
    playersStr = listToStr(players)
    bets = (len(players) - 1) * ','
    deck = Deck()
    hands = dealHands(deck, len(players))
    return {
        'hPot': 0,
        'sPot': 0,
        'credits': credits,
        'players': playersStr,
        'bets': bets,
        'deck': deck,
        'hands': hands
    }
