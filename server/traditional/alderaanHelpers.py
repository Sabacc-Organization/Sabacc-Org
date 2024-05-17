import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from helpers import *

# Calculate the hand values in a list of hands
def calcHandVals(handsList):
    # Iterate through handsList
    handVals = []
    for hand in handsList:
            # Iterate through cards in hand
            v = 0
            for card in hand.split(","):
                v += int(card) # Add value of card to hand val

            # Create a copy of hand and sort it
            hs = hand.split(",").copy()
            hs.sort()

            # Special hands

            # Idiots array, best hand, 0,2,3
            if hs == ["0", "2", "3"]:
                v = 230

            # Fairy empress, -2,-2 (-22)
            elif hand.split(",") == ["-2", "-2"]:
                v = -22

            # Append hand val to handVals
            handVals.append(v)

    return handVals

# Calculate the best hand value in a list of hand values
def calcBestVal(handVals):

    # Iterate through hand values looking for best value
    bestVal = 0
    for val in handVals:
            # Idiot's Array, unbeatable
            if val == 230:
                bestVal = val
                break

            # Check for Bomb Outs
            elif val == 0 or abs(val) > 23:
                 pass

            # Current val is better than stored val
            elif abs(val) > abs(bestVal):
                bestVal = val

            # Current val abs is equal to stored val abs
            elif abs(val) == abs(bestVal):
                if val < bestVal: # aka if this new val is negative and the old one is positive
                    bestVal = val # Negative beats positive

    # Everyone bombed out
    if bestVal == 0:
        return None

    return bestVal

# Find indexes in hands list with the best value
def findBestDexes(handVals, bestVal):
    
    # Iterate through handVals
    bestDexes = []
    for i in range(len(handVals)):
        # If this hand value is equal to the best value, add it to best indexes list
        if handVals[i] == bestVal:
            bestDexes.append(i)

    # Return indexes with best value
    return bestDexes


# Master function that incorporates the other functions to end the game (determine the winner, final hand vals, etc.)
def alderaanEnd(game:object, suddenDemise:bool, bD:list = []):

    # Make copies of inputs
    

    # If recursion has been activated due to a tie, and there is sudden demise
    if suddenDemise == True:
        # Give each participant in the sudden demise a card
        for i in bD:
            game.players[i].hand.append(game.deck.pop())

    # Calculate hand values
    handVals = calcHandVals(handsList)

    # Find the best value out of all the hands
    bestVal = calcBestVal(handVals)

    # Find the players with the best hands
    bestDexes = findBestDexes(handVals, bestVal)

    # If there is a tie, initiat recursion and sudden demise
    if len(bestDexes) > 1:
        return alderaanEnd(handsList, newDeck, protsList, True, bD=bestDexes)
    
    elif len(bestDexes) == 0: # Everyone bombed out
        
        returnData = {
            "handsList": handsList,
            "handVals": handVals,
            "deck": newDeck,
            "protsList": protsList,
            "winner": -1,
            "winnerVal": 1000
        }
        
    elif len(bestDexes) == 1: # Only one winner
        returnData = {
            "handsList": handsList,
            "handVals": handVals,
            "deck": newDeck,
            "protsList": protsList,
            "winner": bestDexes[0],
            "winnerVal": bestVal
        }
    return returnData
