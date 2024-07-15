# corellian spike helper functions

corellianSpikeCardType = None
corellianSpikePlayerType = None

import random
import sys
import os
import copy
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from dataHelpers import *
from helpers import *

class Suit:
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    SYLOP = 'sylop'

# there's no CorellianSpikeCard bc it'd be the same as a regular Card

class CorellianSpikeDeck(Deck):
    def __init__(self, cards:list|None=None):
        super().__init__()
        self.cards = []
        if cards == None:
            for suit in ['circle','square','triangle']:
                for val in range(1, 11):
                    self.cards.extend([Card(val, suit), Card(-val, suit)])
            sylop = Card(0, 'sylop')
            self.cards.extend([sylop, sylop])
            self.shuffle()
        else:
            self.cards.extend(cards)

    @staticmethod
    def fromDb(deck) -> object:
        return CorellianSpikeDeck([Card.fromDb(card) for card in deck])

class CorellianSpikeHand(Hand):
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
        super().__init__(cards)
    
    @staticmethod
    def fromDb(hand) -> object:
        return CorellianSpikeHand([Card.fromDb(card) for card in hand])
    @staticmethod
    def fromDict(hand) -> object:
        return CorellianSpikeHand([Card.fromDict(card) for card in hand])

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
        for val in [card.val for card in self.cards]:
            if val > 0 and (lowest == None or val < lowest):
                lowest = val
        return lowest

class CorellianSpikePlayer(Player):
    def __init__(self, id:int, username:str, credits=0, bet:int=None, hand=CorellianSpikeHand(), folded=False, lastAction=''):
        super().__init__(id, username, credits, bet, hand, folded, lastAction)
    
    def __str__(self) -> str:
        return str(self.id)
    def toString(self) -> str:
        ranking = self.hand.getRanking()
        return f'player {self.id}:\n\thand ({CorellianSpikeHand.HANDS[ranking].capitalize()} #{ranking}): {self.hand} ({len(self.hand.cards)} cards, total: {addPlusBeforeNumber(self.hand.getTotal())})\n'

    def toDb(self, playerType, cardType):
        dbcards = []
        for i in self.hand.cards:
            dbcards.append(i.toDb(cardType))
        return playerType.python_type(self.id, self.username, self.credits, self.bet, dbcards, self.folded, self.lastAction)

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'credits': self.credits,
            'bet': self.bet,
            'hand': self.hand.toDict(),
            'folded': self.folded,
            'lastAction': self.lastAction
        }

    @staticmethod
    def fromDb(player:object):
        return CorellianSpikePlayer(player.id, player.username, player.credits, player.bet, CorellianSpikeHand.fromDb(player.hand), player.folded, player.lastaction)

class CorellianSpikeGame(Game):
    handPotAnte = 5
    sabaccPotAnte = 10

    drawFromDeckCost = 0
    drawFromDiscardCost = 0
    deckTradeCost = 0
    discardTradeCost = 0
    discardCost = 0
    discardCostIncremental = False
    standCost = 0

    def __init__(self, players:list, id:int=None, deck:object=None, discardPile:list=None, player_turn:int=None, p_act='', hand_pot=0, sabacc_pot=0, sabacc_pot_ante=10, phase='card', round=1, shift=False, completed=False):
        super().__init__(players=players, id=id, player_turn=player_turn, p_act=p_act, deck=deck, phase=phase, cycle_count=round, completed=completed)
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self.sabaccPotAnte = sabacc_pot_ante
        self._shift = shift
        self.discardPile = discardPile
        
    # for testing purposes
    def __str__(self) -> str:
        ret = f'\ndeck ({len(self.deck.cards)}): {self.deck}\ndiscard pile ({len(self.discardPile)}): [{listToStr(self.discardPile)}]\nhand pot: {self.handPot}\tsabacc pot: {self.sabaccPot}\n\n'
        for player in self.players:
            ret += player.toString()
        #ret += '\n' + self.determineWinner()
        return ret
    
    # create a new game
    @staticmethod
    def newGame(playerIds:list, playerUsernames:list, db, startingCredits=1000):

        if len(playerIds) != len(playerUsernames):
            return "Uneqal amount of ids and usernames"
        
        if len(playerIds) > 8:
            "Too many players. Max of 8 players."

        if len(playerIds) <= 1:
            "You cannot play by yourself"

        # create player list
        players = []
        for i in range(len(playerIds)):
            players.append(CorellianSpikePlayer(playerIds[i], username=playerUsernames[i], credits=startingCredits - CorellianSpikeGame.handPotAnte - CorellianSpikeGame.sabaccPotAnte))
        
        # create deck, discard pile, and pots
        deck = CorellianSpikeDeck()
        discardPile = [deck.draw()]
        handPot = CorellianSpikeGame.handPotAnte * len(players)
        sabaccPot = CorellianSpikeGame.sabaccPotAnte * len(players)

        # create Game object
        game = CorellianSpikeGame(players=players, deck=deck, discardPile=discardPile, player_turn=players[0].id, hand_pot=handPot, sabacc_pot=sabaccPot)

        # deal cards to each player
        game.dealHands()

        # the 1st player is the 1st dealer

        if db:
            db.execute("INSERT INTO corellian_spike_games (players, hand_pot, sabacc_pot, deck, discard_pile, player_turn, p_act) VALUES(%s, %s, %s, %s, %s, %s, %s)", [game.playersToDb(player_type=corellianSpikePlayerType,card_type=corellianSpikeCardType), game.hand_pot, game.sabacc_pot, game.deckToDb(corellianSpikeCardType), game.discardPileToDb(corellianSpikeCardType), game.player_turn, game.p_act])

        # return Game object
        return game

    # set up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= self.sabaccPotAnte + self.handPotAnte # Make users pay antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Update pots
        self.hand_pot = self.handPotAnte * len(self.players)
        self.sabacc_pot += self.sabaccPotAnte * len(self.players)

        # construct deck and discard pile
        self.deck = CorellianSpikeDeck()
        self.discardPile = [self.deck.draw()]

        # deal hands
        self.dealHands()
  
    def dealHands(self):
        for player in self.players:
            player.hand.cards = self.deck.draw(2).copy()
    
    def determineWinner(self) -> str:
        ret = ''
        handRankings = [player.hand.getRanking() for player in self.players]
        winningHand = min(handRankings)
        winningPlayers = []
        for player in self.players:
            if player.hand.getRanking() == winningHand:
                winningPlayers.append(player)
        
        if len(winningPlayers) == 1:
            return {"winStr": f'player {winningPlayers[0].id} won with a hand of {CorellianSpikeHand.HANDS[winningHand]} (#{winningHand})', "winner": winningPlayers[0], "0": winningHand < 18}
        ret += f"{bothOrAll(len(winningPlayers)) + ' players' if len(winningPlayers) == len(self.players) else f'players {listToStr(winningPlayers)}'} tied with a hand of {CorellianSpikeHand.HANDS[winningHand]} (#{winningHand})\n"
        
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
                return {"winStr":ret + f'player {winningPlayers[0].id} won with a total of {addPlusBeforeNumber(winningPlayers[0].hand.getTotal())}', "winner": winningPlayers[0], "0": closestTo0 == 0}
            ret += f'players {listToStr(winningPlayers)} tied with a total of {addPlusBeforeNumber(closestTo0)}\n'
        
            # 18b. Positive Score
            handTotals = [player.hand.getTotal() for player in winningPlayers]
            atLeast1Pos = max(handTotals) > 0 # at least 1 person has a positive score
            if atLeast1Pos: 
                for i in range(len(winningPlayers)-1, -1, -1):
                    if handTotals[i] < 0:
                        del winningPlayers[i]
                if len(winningPlayers) == 1:
                    return {"winStr": ret + f'player {winningPlayers[0].id} won with a positive score', "winner": winningPlayers[0], "0": False}
            ret += f"players {listToStr(winningPlayers)} {'both' if len(winningPlayers) == 2 else 'all'} had a {'positive' if atLeast1Pos else 'negative'} score\n"

            # 19-Most Cards
            numCards = [len(player.hand.cards) for player in winningPlayers]
            mostCards = max(numCards)
            for i in range(len(winningPlayers) - 1, -1, -1):
                if numCards[i] < mostCards:
                    del winningPlayers[i]
            if len(winningPlayers) == 1:
                return {"winStr": ret + f'player {winningPlayers[0].id} won with {len(winningPlayers[0].hand.cards)} cards', "winner": winningPlayers[0], "0": False}
            ret += f'players {listToStr(winningPlayers)} tied with {mostCards} cards\n'
            
            # 20- lowest sum of all positive cards
            posTotals = []
            for player in winningPlayers:
                total = 0
                for val in [card.val for card in player.hand.cards]:
                    if val > 0:
                        total += val
                posTotals.append(total)
            minPosTotal = min(posTotals)
            for i in range(len(winningPlayers)-1, -1, -1):
                if posTotals[i] != minPosTotal:
                    del winningPlayers[i]
            
            if len(winningPlayers) == 1:
                return {"winStr": ret + f'player {winningPlayers[0].id} won with the lowest positive card total of {minPosTotal}', "winner": winningPlayers[0], "0": False}
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
            return {"winStr": ret + f"player {newWinningPlayers[0].id} won with a lowest positive value of +{lowest}", "winner": winningPlayers[0], "0": True}
        winningPlayers = newWinningPlayers
        ret += f"players {listToStr(winningPlayers)} tied with a lowest positive value of +{lowest}\n"

        # 5- blind draw (closest to 0)
        ret += 'blind draw: '
        blindDraws = []
        closestTo0 = 0
        while len(winningPlayers) > 1:
            for i in range(len(winningPlayers)):
                drawnCard = self.deck.draw()
                val = abs(drawnCard.val)
                if i == 0 or val < closestTo0:
                    closestTo0 = val
                blindDraws.append(drawnCard)
                ret += f"player {winningPlayers[i].id} drew a {drawnCard}{', ' if i < len(winningPlayers) - 1 else ' - '}"
            for i in range(len(winningPlayers) - 1, -1, -1):
                if abs(blindDraws[i].val) != closestTo0:
                    del winningPlayers[i]
            if len(winningPlayers) > 1:
                ret += f"{'everyone' if len(winningPlayers) == len(blindDraws) else listToStr(winningPlayers)} tied with {closestTo0}s\n"
            else:
                ret += f'player {winningPlayers[0].id} won with a {closestTo0}'

        return {"winStr": ret, "winner": winningPlayers[0], "0": closestTo0 == 0}
    
    def discardPileToDb(self, cardType):
        return [card.toDb(cardType) for card in self.discardPile]
    
    def discardPileToDict(self):
        return [card.toDict() for card in self.discardPile]
    
    def toDict(self):
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot,
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': self.deck.toDict(),
            'discard_pile': self.discardPileToDict(),
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self._shift,
            'completed': self.completed
        }

    # reshuffle the discard pile to form a new deck
    def _reshuffle(self):
        self.deck.cards = self.discardPile + self.deck.cards # keep remaining cards on top (end)
        self.discardPile = []
        self.deck.shuffle()

    # draw a number of cards from the deck (reshuffling if necessary)
    def safeDrawFromDeck(self, numCards=1):
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
        if not isinstance(cards, list):
            cards = [cards]
        self.discardPile.extend(cards)

    # draw cards from deck for player
    def _playerDrawFromDeck(self, player:CorellianSpikePlayer, numCards=1):
        drawnCard = self.safeDrawFromDeck(numCards)
        player.addToHand(drawnCard)
        return drawnCard

    # draw top discard for player
    def _playerDrawDiscard(self, player:CorellianSpikePlayer):
        drawnCard = self._drawDiscard()
        player.addToHand(drawnCard)
        return drawnCard
    
    # player discards
    def _playerDiscard(self, player:CorellianSpikePlayer, discardCardIndex:int):
        self._discard(player.discard(discardCardIndex))
    
    ''' player actions '''
    # player buys from the deck for 5 credits
    def buyFromDeck(self, player:CorellianSpikePlayer):
        player.credits -= self.drawFromDeckCost
        player.lastAction = "buys from deck"
        return self._playerDrawFromDeck(player)
    
    # player buys top discard for 10 creds
    def buyFromDiscard(self, player:CorellianSpikePlayer):
        player.credits -= self.drawFromDiscardCost
        player.lastAction = "buys from discard"
        card = self._playerDrawDiscard(player)
        if len(self.discardPile) == 0:
            self.discardPile.append(self.deck.draw())
        return card

    # player discards a card, then draws one
    def tradeWithDeck(self, player:CorellianSpikePlayer, tradeCardIndex:int):
        player.credits -= self.deckTradeCost
        player.lastAction = "trades with deck"
        drawnCard = self._playerDrawFromDeck(player)
        self._playerDiscard(player, tradeCardIndex)
        return drawnCard

    # player draws top discard, then discards a card
    def tradeWithDiscard(self, player:CorellianSpikePlayer, tradeCardIndex):
        player.credits -= self.discardTradeCost
        player.lastAction = "trades with discard"
        drawnCard = self._playerDrawDiscard(player)
        self._playerDiscard(player, tradeCardIndex)
        return drawnCard
    
    # player discards for increasing price
    def playerDiscardAction(self, player:CorellianSpikePlayer, discardCardIndex:int):
        player.credits -= self.discardCost * self.cycle_count if self.discardCostIncremental else self.discardCost
        player.lastAction = "discards"
        self._playerDiscard(player, discardCardIndex)

    # replace every card in every player's hand
    def shiftcards(self):
        # loop thru players
        for player in self.players:
            hand = player.hand.cards
            # loop thru cards in hand
            handLen = len(hand)
            for i in range(handLen):
                player.discard(0)
                self._playerDrawFromDeck(player, 1)

    def playersToDb(self, player_type, card_type):
        return [player.toDb(player_type, card_type) for player in self.players]

    @staticmethod
    def fromDb(game:object):
        return CorellianSpikeGame(id=game[0],players=[CorellianSpikePlayer.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=CorellianSpikeDeck.fromDb(game[5]), discardPile=[Card.fromDb(card) for card in game[6]], player_turn=game[7], p_act=game[8], round=game[9], shift=game[10], completed=game[11])

    # overrides parent method
    def action(self, params:dict, db):
        originalSelf = copy.deepcopy(self)

        player = self.getPlayer(username=params["username"])

        if (params["action"] in ["deckDraw", "discardDraw", "deckTrade", "discardTrade", "stand", "discard", "alderaan"]) and (self.phase in ["card", "alderaan"]) and (self.player_turn == player.id) and (self.completed == False):

            if params["action"] == "deckDraw":
                self.buyFromDeck(player)

            elif params["action"] == "discardDraw":
                self.buyFromDiscard(player)

            elif params["action"] == "deckTrade":
                tradeCard = Card.fromDict(params["trade"])
                tradeDex = player.hand.cards.index(tradeCard)

                self.tradeWithDeck(player, tradeDex)

            elif params["action"] == "discardTrade":
                tradeCard = Card.fromDict(params["trade"])
                tradeDex = player.hand.cards.index(tradeCard)

                self.tradeWithDiscard(player, tradeDex)

            elif params["action"] == "stand":
                player.credits -= CorellianSpikeGame.standCost
                player.lastAction = "stands"

            elif params["action"] == "discard":
                tradeCard = Card.fromDict(params["trade"])
                tradeDex = player.hand.cards.index(tradeCard)

                self.playerDiscardAction(player, tradeDex)

            uDex = self.getPlayerDex(id=player.id)
            nextPlayer = uDex + 1

            if nextPlayer >= len(self.getActivePlayers()):
                nextPlayer = 0
                self.phase = "betting"

            dbList = [
                self.deckToDb(corellianSpikeCardType),
                self.discardPileToDb(corellianSpikeCardType),
                self.playersToDb(corellianSpikePlayerType, corellianSpikeCardType),
                self.phase,
                self.getActivePlayers()[nextPlayer].id,
                player.username + " " + player.lastAction,
                self.id
            ]
            db.execute("UPDATE corellian_spike_games SET deck = %s, discard_pile = %s, players = %s, phase = %s, player_turn = %s, p_act = %s WHERE game_id = %s", dbList)

        elif (params['action'] in ["fold", "bet", "call", "raise"]) and (self.phase == "betting") and (self.player_turn == player.id) and (self.completed == False):
            players = self.getActivePlayers()

            if params['action'] == "fold":
                player.fold()

                players = self.getActivePlayers()


            elif (params["action"] == "bet") and (players.index(player) == 0):
                player.makeBet(params["amount"])

            elif params["action"] == 'call':
                player.makeBet(params["amount"], False)
                player.lastAction = f'calls'

            elif params["action"] == 'raise':
                player.makeBet(params["amount"], False)
                player.lastAction = f'raises to {params["amount"]}'

            betAmount = [i.getBet() for i in self.players]
            betAmount.append(0)
            betAmount = max(betAmount)
            nextPlayer = None
            for i in players:
                iBet = i.bet if i.bet != None else -1
                if iBet < betAmount:
                    nextPlayer = i.id
                    break

            if len(players) <= 1:
                winningPlayer = players[0]
                winningPlayer.credits += self.hand_pot + winningPlayer.bet
                self.hand_pot = 0
                winningPlayer.bet = None

            if nextPlayer == None:
                # add all bets to hand pot
                for player in players:
                    self.hand_pot += player.getBet()
                    player.bet = None

            dbList = [
                self.playersToDb(corellianSpikePlayerType, corellianSpikeCardType),
                self.hand_pot,
                'betting' if nextPlayer != None else 'shift',
                nextPlayer if nextPlayer != None else players[0].id,
                player.username + " " + player.lastAction,
                len(players) <= 1,
                self.id
            ]
            db.execute("UPDATE corellian_spike_games SET players = %s, hand_pot = %s, phase = %s, player_turn = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)

        elif (params["action"] == "shift") and (self.player_turn == player.id) and (self.completed == False):
            self._shift = self.rollShift()

            if self._shift:
                self.shiftcards()

            # Set the Shift message
            shiftStr = "Sabacc shift!" if self._shift else "No shift!"

            if self.cycle_count >= 3:
                self.completed = True
                winData = self.determineWinner()

                winningPlayer = self.getPlayer(id=winData["winner"].id)
                winningPlayer.credits += self.hand_pot
                self.hand_pot = 0
                if winData["0"]:
                    winningPlayer.credits += self.sabacc_pot
                    self.sabacc_pot = 0

                shiftStr = f"{winData['winStr']}"

            self.cycle_count += 1

            dbList = [
                "card", 
                self.deckToDb(corellianSpikeCardType),
                self.discardPileToDb(corellianSpikeCardType),
                self.playersToDb(corellianSpikePlayerType, corellianSpikeCardType),
                self.hand_pot,
                self.sabacc_pot,
                self.getActivePlayers()[0].id,
                self._shift,
                shiftStr,
                self.cycle_count,
                self.completed,
                self.id
            ]

            db.execute("UPDATE corellian_spike_games SET phase = %s, deck = %s, discard_pile = %s, players = %s, hand_pot = %s, sabacc_pot = %s, player_turn = %s, shift = %s, p_act = %s, cycle_count = %s, completed = %s WHERE game_id = %s", dbList)

        elif (params["action"] == "playAgain") and (self.player_turn == player.id) and (self.completed):
            self.nextRound()

            dbList = [
                self.playersToDb(corellianSpikePlayerType, corellianSpikeCardType), 
                self.hand_pot,
                self.sabacc_pot,
                "card",
                self.deckToDb(corellianSpikeCardType),
                self.discardPileToDb(corellianSpikeCardType),
                self.players[0].id,
                0,
                "",
                False,
                self.id
            ]

            db.execute("UPDATE corellian_spike_games SET players = %s, hand_pot = %s, sabacc_pot = %s, phase = %s, deck = %s, discard_pile = %s, player_turn = %s, cycle_count = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)


        if self == originalSelf:
            return "invalid user input"

        return self