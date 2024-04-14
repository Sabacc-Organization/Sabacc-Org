import random
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from dataHelpers import *

# Global deck constant
DECK = "1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0,-2,-2,-8,-8,-11,-11,-13,-13,-14,-14,-15,-15,-17,-17"

# Construct new deck and hands
def constructDeck(playerCount):
    # Deck variables
    deck = DECK
    deckList = list(deck.split(","))

    # Draw 2 cards for every hand
    hands = []
    for i in range(playerCount):
        player_hand = ""
        for j in range(2):
            randDex = random.randint(0, len(deckList) - 1)
            if player_hand == "":
                player_hand = deckList.pop(randDex)
            else:
                player_hand = player_hand + "," + deckList.pop(randDex)

        hands.append(player_hand)

    # New deck after drawing cards
    deck = listToStr(deckList)

    # Return deck data
    data = {"deck": deck, "hands": hands}
    return data

# Shuffle deck, while removing some cards that players have
def shuffleDeck(outCards):
    deckList = DECK.split(",")
    for card in outCards:
        deckList.remove(card)
    return listToStr(deckList)