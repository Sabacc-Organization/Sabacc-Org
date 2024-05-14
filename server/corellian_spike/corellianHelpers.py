# corellian spike helper functions

import random
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from dataHelpers import *

class Suit:
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    SYLOP = 'sylop'

class Card:
    def __init__(self, val:int, suit:Suit):
        self.value = val
        self.suit = suit
    def __str__(self) -> str:
        return f'{addPlusBeforeNumber(self.value)} {self.suit}'
    def __eq__(self, other:object) -> bool:
        return self.value == other.value and self.suit == other.suit
    def toDict(self) -> dict:
        return {
            'val': self.value,
            'suit': self.suit
        }
    @staticmethod
    def fromDict(card:dict) -> object:
        return Card(val=card['val'], suit=card['suit'])
    
    # changes lists of card objects to lists of dictionaries and vice versa
    @staticmethod
    def cardsToDicts(listOfCards:list) -> list:
        return [card.toDict() for card in listOfCards]
    @staticmethod
    def dictsToCards(listOfDicts:list) -> list:
        return [Card.fromDict(card) for card in listOfDicts]

class Deck:
    def __init__(self, cards=[]):
        self.cards = cards
        # if no cards provided, create new deck
        if cards == []:
            for suit in [Suit.CIRCLE,Suit.SQUARE,Suit.TRIANGLE]:
                for val in range(1, 11):
                    self.cards.extend([Card(val, suit), Card(-val, suit)])
            sylop = Card(0, 'sylop')
            self.cards.extend([sylop, sylop])
            self.shuffle()
    def __str__(self) -> str:
        return f'[{listToStr(self.cards)}]'
    
    def toListOfDicts(self) -> list:
        return Card.cardsToDicts(self.cards)
    @staticmethod
    def fromListOfDicts(deck:list) -> object:
        return Deck(Card.dictsToCards(deck))

    def shuffle(self):
        for i in range(len(self.cards)):
            switchIndex = random.randint(0, len(self.cards) - 1)
            temp = self.cards[switchIndex]
            self.cards[switchIndex] = self.cards[i]
            self.cards[i] = temp

    # remove a number of cards from the top (end) of the deck and return them
    def draw(self, numCards=1):
        # check there are enuf cards left in deck
        if len(self.cards) < numCards:
            print(f"ERROR: trying to draw from deck but not enough cards left")
            return None
        
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
        3: 'sylop w/ straight khyron',
        4: 'sylop w/ rule of 2',
        5: 'akaata',
        6: 'boss triad',
        7: 'yee-ha',
        8: 'rhylet',
        9: 'squadron',
        10: 'gee whiz',
        11: 'straight khyron',
        12: 'banthas wild',
        13: 'rule of 2',
        14: 'senate',
        15: 'clan',
        16: 'triad',
        17: 'power coupling',
        18: 'Nulrhek'
    }
    def __init__(self, cards=[]):
        self.cards = cards
        self.sort()
    def __str__(self) -> str:
        self.sort()
        return f'[{listToStr(self.cards)}]'
    def __eq__(self, other:object) -> bool:
        if len(self.cards) != len(other.cards):
            return False
        for i in range(len(self.cards)):
            if self.cards[i] != other.cards[i]:
                return False
        return True
    
    def toListOfDicts(self) -> list:
        return Card.cardsToDicts(self.cards)
    @staticmethod
    def fromListOfDicts(hand:list) -> object:
        return Hand(Card.dictsToCards(hand))
    
    def getListOfVals(self) -> list:
        return [card.value for card in self.cards]
    
    def append(self, card:Card):
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
    
    def getTotal(self) -> int:
        return sum([card.value for card in self.cards])
    def getRanking(self):
        # get the values of the cards and take the absolute value (negatives don't matter here)
        vals = [abs(val) for val in self.getListOfVals()]
        vals.sort() # sort ascending

        if self.getTotal() == 0: # hands 1-17 total 0
            if 0 in vals: # hands 1-7 have a sylop
                # 1. Pure Sabacc: 2 sylops
                if vals == [0, 0]:
                    return 1
                if len(vals) == 5: # hands 2-5 have 5 cards
                    # 2-Full sabacc- sylop with 4 of a kind
                    if vals.count(vals[1]) == 4:
                        return 2
                    # 3. sylop w/ straight khyron- sylop w/ sequential run of 4 cards
                    if [vals[i + 1] - vals[i] for i in range(1, 4)] == [1,1,1]:   # find differences b/w values & check that they're all 1
                        return 3
                    # 4. sylop w/ rule of 2- sylop with 2 pairs
                    if vals[1] == vals[2] and vals[3] == vals[4]:
                        return 4
                    # 5-Akaata- sylop with 4 cards equaling zero
                    return 5 # conditions alr met if got to this point
                # 6-Boss Triad- sylop with 3 cards equaling 0
                if len(vals) == 4:
                    return 6
                # 7-Yee-ha- Sylop and a pair
                if len(vals) == 3 and vals[1] == vals[2]:
                    return 7
            # 8-Rhylet- 3 of a kind with 2 of a kind
            if len(vals) == 5 and vals[0] == vals[1] and vals[3] == vals[4] and (vals[2] == vals[1] or vals[2] == vals[3]): # check that the 1st 2 & last 2 are = and the middle one equals either the 2nd or 4th one
                return 8
            # 9-Squadron – 4 of a kind
            if len(vals) == 4 and vals.count(vals[0]) == 4:
                return 9
            # 10-Gee Whiz- 1,2,3,4 and a 10
            if vals == [1,2,3,4,10]:
                return 10
            # 11. straight khyron - sequential run of 4
            if len(vals) == 4 and [vals[i + 1] - vals[i] for i in range(0, 3)] == [1,1,1]:
                return 11
            # 12- Banthas Wild- 3 of a kind
            for val in vals:
                if vals.count(val) == 3:
                    return 12
            # 13- Rule of 2- two pair
            if len(vals) == 4 and vals[0] == vals[1] and vals[2] == vals[3]:
                return 13
            # 14-Senate- 5 random cards totaling zero
            if len(vals) == 5:
                return 14
            # 15- Clan- 4 random cards totaling zero
            if len(vals) == 4:
                return 15
            # 16- Triad – 3 random cards totaling zero
            if len(vals) == 3:
                return 16
            # 17- Power Coupling – a pair
            if len(vals) == 2 and vals[0] == vals[1]:
                return 17
            return "error: hand total was 0 but hand did't match any known hand"
        else:
            return 18 # Nulrhek- Hand closest to zero

    def lowestPosValue(self):
        lowest = None
        for val in [card.value for card in self.cards]:
            if val > 0 and (lowest == None or val < lowest):
                lowest = val
        return lowest

class Player:
    def __init__(self, id:int, username='', credits=0, bet:int=None, hand=Hand(), folded=False, lastAction = ''):
        self.id = id
        self.username = username
        self.credits = credits
        self.bet = bet
        self.hand = hand
        self.folded = folded
        self.lastAction = lastAction
    
    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'credits': self.credits,
            'bet': self.bet,
            'hand': self.hand.toListOfDicts(),
            'folded': self.folded,
            'lastAction': self.lastAction
        }
    @staticmethod
    def fromDict(player:dict) -> object:
        return Player(id=player['id'], username=player['username'], credits=player['credits'], bet=player['bet'], hand=Hand.fromListOfDicts(player['hand']), folded=player['folded'], lastAction=player['lastAction'])
    
    def __str__(self) -> str:
        return str(self.id)
    def toString(self) -> str:
        ranking = self.hand.getRanking()
        return f'player {self.id}:\n\tcredits: {self.credits}, bet: {self.bet}\n\thand ({Hand.HANDS[ranking].capitalize()} #{ranking}): {self.hand} ({len(self.hand.cards)} cards, total: {addPlusBeforeNumber(self.hand.getTotal())})\n'
    
    def addToHand(self, cards):
        if type(cards) != list:
            cards = [cards]
        self.hand.extend(cards)

    def discard(self, discardCardIndex:int):
        try:
            return self.hand.pop(discardCardIndex)
        except IndexError:
            print("ERROR: invalid index for discard card")
    
    def getIndexOfCard(self, targetCard:Card) -> int:
        for i in range(len(self.hand)):
            if self.hand[i] == targetCard:
                return i
        return -1
    
    # betting
    def getBet(self) -> int:
        return self.bet if self.bet != None else 0
    def makeBet(self, betAmount:int, absolute:bool=True):
        if absolute:
            self.credits -= betAmount - self.getBet()
            self.bet = betAmount
        else:
            self.credits -= betAmount
            self.bet += betAmount
    
    def fold(self):
        self.credits += self.getBet()
        self.bet = None
        self.folded = True

class CorellianSpikeGame:
    def __init__(self, playerIds:list):
        self.players = []
        for id in playerIds:
            self.players.append(Player(id))
        self.newGame()
        # designate the 1st player as the 1st dealer
        self.dealer = self.players[0]
        
    # for testing purposes
    def __str__(self) -> str:
        ret = '\n'
        for player in self.players:
            ret += player.toString()
        #ret += '\n' + self.determineWinner()
        return ret
    
    def newGame(self):
        # clear players' hands
        for player in self.players:
            player.hand.cards = []
        
        # create deck, discard pile, and pots
        self.deck = Deck()
        self.discardPile = [self.deck.draw()]
        self.handPot = 5 * len(self.players)
        self.sabaccPot = 5 * len(self.players)

        # distribute credits
        for player in self.players:
            player.credits = 1000

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

    def getPlayerFromId(self, id:int) -> Player:
        for player in self.players:
            if player.id == id:
                return player
    
    def shift(self):
        for player in self.players:
            # put player's cards on bottom of deck
            self.deck.cards = player.hand.cards + self.deck.cards
            # deal player as many cards as they had before
            player.hand.cards = self._drawFromDeck(len(player.hand.cards))
    
    def determineWinner(self) -> str:
        ret = ''
        handRankings = [player.hand.getRanking() for player in self.players]
        winningHand = min(handRankings)
        winningPlayers = []
        for player in self.players:
            if player.hand.getRanking() == winningHand:
                winningPlayers.append(player)
        
        if len(winningPlayers) == 1:
            return f'player {winningPlayers[0].id} won with a hand of {Hand.HANDS[winningHand]} (#{winningHand})'
        ret += f"{bothOrAll(len(winningPlayers)) + ' players' if len(winningPlayers) == len(self.players) else f'players {listToStr(winningPlayers)}'} tied with a hand of {Hand.HANDS[winningHand]} (#{winningHand})\n"
        
        ''' tie breakers '''
        # if winning hand is something other than nulrhek, tiebreaker is lowest positive value card
        if winningHand == 18: # nulrhek
            # 18. closest to 0
            handTotals = [abs(player.hand.getTotal()) for player in winningPlayers]
            closestTo0 = min(handTotals)
            for i in range(len(winningPlayers) - 1, -1, -1):
                if handTotals[i] != closestTo0:
                    del winningPlayers[i]
            if len(winningPlayers) == 1:
                return ret + f'player {winningPlayers[0].id} won with a total of {addPlusBeforeNumber(winningPlayers[0].hand.getTotal())}'
            ret += f'players {listToStr(winningPlayers)} tied with a total of {addPlusBeforeNumber(closestTo0)}\n'
        
            # 18b. Positive Score
            handTotals = [player.hand.getTotal() for player in winningPlayers]
            atLeast1Pos = max(handTotals) > 0 # at least 1 person has a positive score
            if atLeast1Pos: 
                for i in range(len(winningPlayers)-1, -1, -1):
                    if handTotals[i] < 0:
                        del winningPlayers[i]
                if len(winningPlayers) == 1:
                    return ret + f'player {winningPlayers[0].id} won with a positive score'
            ret += f"players {listToStr(winningPlayers)} {'both' if len(winningPlayers) == 2 else 'all'} had a {'positive' if atLeast1Pos else 'negative'} score\n"

            # 19-Most Cards
            numCards = [len(player.hand.cards) for player in winningPlayers]
            mostCards = max(numCards)
            for i in range(len(winningPlayers) - 1, -1, -1):
                if numCards[i] < mostCards:
                    del winningPlayers[i]
            if len(winningPlayers) == 1:
                return ret + f'player {winningPlayers[0].id} won with {len(winningPlayers[0].hand.cards)} cards'
            ret += f'players {listToStr(winningPlayers)} tied with {mostCards} cards\n'
            
            # 20- lowest sum of all positive cards
            posTotals = []
            for player in winningPlayers:
                total = 0
                for val in [card.value for card in player.hand.cards]:
                    if val > 0:
                        total += val
                posTotals.append(total)
            minPosTotal = min(posTotals)
            for i in range(len(winningPlayers)-1, -1, -1):
                if posTotals[i] != minPosTotal:
                    del winningPlayers[i]
            
            if len(winningPlayers) == 1:
                return ret + f'player {winningPlayers[0].id} won with the lowest positive card total of {minPosTotal}'
            ret += f'players {listToStr(winningPlayers)} tied with a positive card total of {minPosTotal}\n'

        # 21- lowest positive card
        lowestPosValues = [player.hand.lowestPosValue() for player in winningPlayers]
        lowest = lowestPosValues[0]
        for val in lowestPosValues:
            if val != None and val < lowest:
                lowest = val
        newWinningPlayers = []
        for player in winningPlayers:
            if player.hand.lowestPosValue() == lowest:
                newWinningPlayers.append(player)
        if len(newWinningPlayers) == 1:
            return ret + f"player {newWinningPlayers[0].id} won with a lowest positive value of +{lowest}"
        winningPlayers = newWinningPlayers
        ret += f"players {listToStr(winningPlayers)} tied with a lowest positive value of +{lowest}\n"

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
                ret += f"player {winningPlayers[i].id} drew a {drawnCard}{', ' if i < len(winningPlayers) - 1 else ' - '}"
            for i in range(len(winningPlayers) - 1, -1, -1):
                if abs(blindDraws[i].value) != closestTo0:
                    del winningPlayers[i]
            if len(winningPlayers) > 1:
                ret += f"{'everyone' if len(winningPlayers) == len(blindDraws) else listToStr(winningPlayers)} tied with {closestTo0}s\n"
            else:
                ret += f'player {winningPlayers[0].id} won with a {closestTo0}'

        return ret

    # reshuffle the discard pile to form a new deck
    def _reshuffle(self):
        self.deck.cards = self.discardPile
        self.discardPile = []
        self.deck.shuffle()

    # draw a number of cards from the deck (reshuffling if necessary)
    def _drawFromDeck(self, numCards=1):
        if(len(self.deck.cards) < numCards):
            self._reshuffle()
        return self.deck.draw(numCards)
    
    # draw top discard
    def _drawDiscard(self):
        if len(self.discardPile) == 0:
            print(f"ERROR: trying to draw from empty discard pile")
        else:
            return self.discardPile.pop() # since new cards are added to the end, the last card is the top one

    # add discarded card(s) to discard pile
    def _discard(self, cards):
        if type(cards) != list:
            cards = [cards]
        self.discardPile.extend(cards)

    # draw cards from deck for player
    def _playerDrawFromDeck(self, player:Player, numCards=1):
        drawnCard = self._drawFromDeck(numCards)
        player.addToHand(drawnCard)
        return drawnCard

    # draw top discard for player
    def _playerDrawDiscard(self, player:Player):
        drawnCard = self._drawDiscard()
        player.addToHand(drawnCard)
        return drawnCard
    
    # player discards
    def _playerDiscard(self, player:Player, discardCardIndex:int):
        self._discard(player.discard(discardCardIndex))
    
    ''' player actions '''
    # player buys from the deck for 5 credits
    def buyFromDeck(self, player:Player):
        player.credits -= 5
        return self._playerDrawFromDeck(player)
    
    # player buys top discard for 10 creds
    def buyFromDiscard(self, player:Player):
        player.credits -= 10
        return self._playerDrawDiscard(player)
    
    # player discards a card, then draws one
    def tradeWithDeck(self, player:Player, tradeCardIndex:int):
        self._playerDiscard(player, tradeCardIndex)
        return self._playerDrawFromDeck(player)

    # player draws top discard, then discards a card
    def tradeWithDiscard(self, player:Player, tradeCardIndex):
        drawnCard = self._playerDrawDiscard(player)
        self._playerDiscard(player, tradeCardIndex)
        return drawnCard
    
    # player discards for increasing price
    def playerDiscardAction(self, player:Player, discardCardIndex:int):
        player.credits -= 20 * self.round
        self._playerDiscard(player, discardCardIndex)
    
    # set up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= 10 # Make users pay Sabacc and Hand pot Antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Update pots
        self.hand_pot = 5 * len(self.players)
        self.sabacc_pot += 5 * len(self.players)

        # construct deck and deal hands
        self.deck = Deck()
        self.dealHands()
    
    def dealHands(self):
        for player in self.players:
            player.hand.cards = self._drawFromDeck(2)
    
    def getActivePlayers(self):
        activePlayers = []
        for player in self.players:
            if not player.folded:
                activePlayers.append(player)
        return activePlayers

# if the number is positive, it adds a plus in front of it (otherwise just returns the number)
def addPlusBeforeNumber(n:int) -> str:
    return ('+' if n > 0 else '') + str(n)

def bothOrAll(num:int):
    return 'both' if num == 2 else 'all'

game = CorellianSpikeGame(list(range(1, 3)))
game.players[0].makeBet(10)
game.players[1].makeBet(10)
print(game)
game.players[0].makeBet(10, False)
game.players[1].makeBet(game.players[0].getBet())
print(game)