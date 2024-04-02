from helpers import *

def calcHandVals(handsList):
    handVals = []
    for hand in handsList:
            v = 0
            for card in hand.split(","):
                v += int(card)

            hs = hand.split(",").copy()
            hs.sort()
            if hs == ["0", "2", "3"]:
                v = 230

            elif hand.split(",") == ["-2", "-2"]:
                v = -22

            handVals.append(v)
    return handVals

def calcBestVal(handVals):
    bestVal = 0
    for val in handVals:
            if val == 230:
                bestVal = val
                break

            elif val == 0 or abs(val) > 23:
                # bombOutDexes.append(handVals.index(val))
                pass

            elif abs(val) > abs(bestVal):
                bestVal = val

            elif abs(val) == abs(bestVal):
                if val < bestVal: # aka if this new val is negative and the old one is positive
                    bestVal = val

    if bestVal == 0:
        return None

    return bestVal

def findBestDexes(handVals, bestVal):
    bestDexes = []
    for i in range(len(handVals)):
        if handVals[i] == bestVal:
            bestDexes.append(i)
    return bestDexes


# Most big brain piece of code in this project
def alderaanEnd(hL : list, deckStrIn : str, pL : list, suddenDemise : bool, bD : list=[]):

    handsList = hL.copy()
    newDeck = deckStrIn
    protsList = pL.copy()

    if suddenDemise == True:
        # Give each participant in the sudden demise a card
        for i in bD:
                
                drawData = drawCard(newDeck)
                newDeck = drawData["deck"]
                newCard = drawData["card"]

                handsList[i] += "," + newCard
                protsList[i] += ",0"

    handVals = calcHandVals(handsList)

    bestVal = calcBestVal(handVals)

    bestDexes = findBestDexes(handVals, bestVal)

    if len(bestDexes) > 1:
        return alderaanEnd(handsList, newDeck, protsList, True, bD=bestDexes)
    
    elif len(bestDexes) == 0: # Everyone bombed out
        closestDist = 1000
        closestVal = 0
        for val in handVals:
            if abs(abs(val) - 23) < closestDist:
                closestDist = abs(abs(val) - 23)
                closestVal = val

            elif abs(abs(val) - 23) == closestDist:
                if val < closestVal: # aka if this new val is negative and the old one is positive
                    closestVal = val

        closestDexes = findBestDexes(handVals, closestVal)

        if len(closestDexes) > 1:
            return alderaanEnd(handsList, newDeck, protsList, True, bD=closestDexes)
        
        elif len(closestDexes) == 1:

            returnData = {
                "handsList": handsList,
                "deck": newDeck,
                "protsList": protsList,
                "winner": closestDexes[0],
                "winnerVal": closestVal
            }
            return returnData
        
    elif len(bestDexes) == 1: # Only one winner
        returnData = {
            "handsList": handsList,
            "deck": newDeck,
            "protsList": protsList,
            "winner": bestDexes[0],
            "winnerVal": bestVal
        }
        return returnData