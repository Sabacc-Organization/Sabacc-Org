import random
from enum import Enum
from helpers import *

class TraditionalSuit(Suit):
    COINS = 'coins'
    FLASKS = 'flasks'
    SABERS = 'sabers'
    STAVES = 'staves'
    NEGATIVE_NEUTRAL = 'negative/neutral'
    ALL = [COINS, FLASKS, SABERS, STAVES]
    @staticmethod
    def random(val=None):
        return random.choice(TraditionalSuit.ALL)

class SpecialHands(Enum):
    IDIOTS_ARRAY = 230
    FAIRY_EMPRESS = -22

class TraditionalCard(Card):
    def __init__(self, val:int, suit:TraditionalSuit, protected=False):
        super().__init__(val=val, suit=suit)
        self.protected = protected
    def __eq__(self, other) -> bool:
        return other != None and (self.val == other.val and self.suit == other.suit)
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
        return TraditionalCard(card.val, card.suit, card.protected)
    @staticmethod
    def fromDict(dict):
        return TraditionalCard(dict['val'],dict['suit'],dict['prot'])
    @staticmethod
    def randCardNotInList(val:int, protected=False, unallowedCards=[]):
        card = None
        if val <= 0:
            card = TraditionalCard(val=val, suit=TraditionalSuit.NEGATIVE_NEUTRAL, protected=protected)
            if unallowedCards.count(card) > 1:
                print(f"WARNING: more than 2 {val}'s exist")
        else: # positive val
            allowedSuits = [TraditionalSuit.COINS, TraditionalSuit.FLASKS, TraditionalSuit.SABERS, TraditionalSuit.STAVES]
            for c in unallowedCards:
                if c.val == val and c.suit in allowedSuits:
                    allowedSuits.remove(c.suit)
            if len(allowedSuits) == 0:
                print(f"WARNING: more than 4 {val}'s exist")
                card = TraditionalCard(val=val,suit=random.choice([TraditionalSuit.COINS, TraditionalSuit.FLASKS, TraditionalSuit.SABERS, TraditionalSuit.STAVES]),protected=protected)
            else:
                card = TraditionalCard(val=val,suit=random.choice(allowedSuits), protected=protected)
        return card

class TraditionalDeck(Deck):
    def __init__(self, cardsToExclude:list=[]):
        super().__init__()
        self.cards = 2 * [
            TraditionalCard(-11,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(0,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-8,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-14,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-15,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-2,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-13,TraditionalSuit.NEGATIVE_NEUTRAL),
            TraditionalCard(-17,TraditionalSuit.NEGATIVE_NEUTRAL)
        ]
        for suit in [TraditionalSuit.COINS,TraditionalSuit.FLASKS,TraditionalSuit.SABERS,TraditionalSuit.STAVES]:
            for val in range(1,16):
                self.cards.append(TraditionalCard(val=val,suit=suit))
        for card in cardsToExclude:
            self.cards.remove(card)
        self.shuffle()

class TraditionalHand(Hand):
    def __init__(self, cards=[]):
        super().__init__(cards)

    def protect(self, card:TraditionalCard):
        try:
            self.cards[self.cards.index(card)].protected = True
        except IndexError:
            print("ERROR: invalid index for protected card")
            return "non matching user input"
        return card
    
    @staticmethod
    def fromDb(hand) -> object:
        return TraditionalHand([TraditionalCard.fromDb(card) for card in hand])
    @staticmethod
    def fromDict(hand) -> object:
        return TraditionalHand([TraditionalCard.fromDict(card) for card in hand])

class TraditionalPlayer(Player):
    def __init__(self, id:int, username='', credits=0, bet:int = None, hand:Hand=Hand(), folded=False, lastAction=""):
        super().__init__(id=id, username=username, credits=credits, bet=bet, hand=hand, folded=folded, lastaction=lastAction)
    
    def protect(self, card:TraditionalCard):
        self.hand.protect(card)
        self.lastaction = f"protected a {card.val}"

    def toDb(self, playerType, cardType):
        for i in range(len(self.hand.cards)):
            self.hand.cards[i] = self.hand.cards[i].toDb(cardType)
        return playerType.python_type(self.id, self.username, self.credits, self.bet, self.hand.cards, self.folded, self.lastAction)
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
        return TraditionalPlayer(player.id, player.username, player.credits, player.bet, TraditionalHand.fromDb(player.hand), player.folded, player.lastaction)
    @staticmethod
    def fromDict(dict:dict):
        return TraditionalPlayer(id=dict['id'],username=dict['username'],credits=dict['credits'],bet=dict['bet'],hand=TraditionalHand.fromDict(dict['hand']),folded=dict['folded'],lastAction=dict['lastAction'])
    
    def calcHandVal(self):
        cardVals = self.hand.getListOfVals()
        cardVals.sort()

        '''special hands'''
        # idiot's array (best)
        if cardVals == [0, 2, 3]:
            return SpecialHands.IDIOTS_ARRAY
        elif cardVals == [-2, -2]:
            return SpecialHands.FAIRY_EMPRESS
        
        return sum(cardVals)

class TraditionalGame(Game):
    handPotAnte = 5
    sabaccPotAnte = 10

    def __init__(self, players:list, id:int=None, deck=TraditionalDeck(), player_turn:int=None, p_act='', hand_pot=0, sabacc_pot=0, phase='betting', cycle_count=0, shift=False, completed=False):
        super().__init__(players=players, id=id, player_turn=player_turn, p_act=p_act, deck=deck, phase=phase, cycle_count=cycle_count, completed=completed)
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self._shift = shift

    # create a new game
    @staticmethod
    def newGame(playerIds:list, playerUsernames:list, startingCredits=1000, db=None):

        if len(playerIds) != len(playerUsernames):
            return "Uneqal amount of ids and usernames"
        
        if len(playerIds) > 8:
            "Too many players. Max of 8 players."

        if len(playerIds) <= 1:
            "You cannot play with yourself"


        # create player list
        players = []
        for id in playerIds:
            players.append(TraditionalPlayer(id, playerUsernames[playerIds.index(id)], credits=startingCredits - TraditionalGame.handPotAnte - TraditionalGame.sabaccPotAnte))

        # construct deck
        deck = TraditionalDeck()

        game = TraditionalGame(players=players, deck=deck, player_turn=players[0].id, hand_pot=TraditionalGame.handPotAnte*len(players), sabacc_pot=TraditionalGame.sabaccPotAnte*len(players))
        game.shuffleDeck()
        game.dealHands()

        db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, deck, player_turn, p_act) VALUES(%s, %s, %s, %s, %s, %s)", [game.playersToDb(player_type=TraditionalPlayer,card_type=TraditionalCard), game.hand_pot, game.sabacc_pot, game.deckToDb(TraditionalCard), game.player_turn, game.p_act])

        return game
    
    # sets up for next round
    def nextRound(self):
        # rotate dealer (1st in list is always dealer) - move 1st player to end
        self.players.append(self.players.pop(0))

        for player in self.players:
            player.credits -= (TraditionalGame.sabaccPotAnte + TraditionalGame.handPotAnte) # Make users pay Sabacc and Hand pot Antes
            player.bet = None # reset bets
            player.folded = False # reset folded
            player.lastAction = '' # reset last action
        
        # Update pots
        self.hand_pot = TraditionalGame.handPotAnte * len(self.players)
        self.sabacc_pot += TraditionalGame.sabaccPotAnte * len(self.players)

        # construct deck and deal hands
        self.deck = TraditionalDeck()
        self.shuffleDeck()
        self.dealHands()

    def dealHands(self):
        for player in self.players:
            player.hand.cards = [self.drawFromDeck(),self.drawFromDeck()]

    def toDb(self, card_type, player_type, includeId=False):
        if includeId:
            return [self.id, self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deck.toDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed]
        elif includeId == False:
            return [self.playersToDb(player_type=player_type,card_type=card_type), self.hand_pot, self.sabacc_pot, self.phase, self.deck.toDb(card_type), self.player_turn, self.p_act, self.cycle_count, self._shift, self.completed]
    def playersToDb(self, player_type, card_type):
        return [player.toDb(player_type, card_type) for player in self.players]
    def toDict(self):
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot,
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': self.deck.toDict(),
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self._shift,
            'completed': self.completed
        }
    @staticmethod
    def fromDb(game:object):
        return TraditionalGame(id=game[0],players=[TraditionalPlayer.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=TraditionalDeck.fromDb(game[5]), player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10])
    @staticmethod
    def fromDict(dict:dict):
        return TraditionalGame(id=dict['id'],players=[TraditionalPlayer.fromDict(player) for player in dict['players']],deck=TraditionalDeck.fromDict(dict['deck']),player_turn=dict['player_turn'],p_act=dict['p_act'],hand_pot=dict['hand_pot'],sabacc_pot=dict['sabacc_pot'],phase=dict['phase'],cycle_count=dict['cycle_count'],shift=dict['shift'],completed=dict['completed'])

    def drawFromDeck(self):
        # if deck is empty, reshuffle
        if len(self.deck.cards) == 0:
            # exclude cards in (active) players' hands
            cardsToExclude = []
            for player in self.getActivePlayers():
                cardsToExclude.extend(player.hand.cards)
            self.deck = TraditionalDeck(cardsToExclude=cardsToExclude)
            self.deck.shuffle()
        return self.deck.draw()
    
    # roll shift
    def rollShift(self):
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        self.shift = roll1 == roll2

    # replace every unprotected card in every player's hand
    def shift(self):
        # loop thru players
        for player in self.players:
            hand = player.hand.cards
            # loop thru cards in hand
            for i in range(len(hand)):
                if not hand[i].protected: # if card is not protected
                    hand[i] = self.drawFromDeck()
    
    def alderaan(self, suddenDemise=False, sdPlayers:list=[]):
        # If recursion has been activated due to a tie, and there is sudden demise
        if suddenDemise == True:
            # Give each participant in the sudden demise a card
            for player in sdPlayers:
                player.hand.cards.append(self.drawFromDeck())
        
        # calculate winners and losers
        winningPlayers, bestHand, bombedOutPlayers = TraditionalGame.calcWinners(sdPlayers) if suddenDemise else TraditionalGame.calcWinners(self.players)

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

    # overrides parent method
    def action(self, params:dict, db):

        originalSelf = self

        player = self.getPlayer(username=params["username"])

        if params['action'] == "protect":
            card = TraditionalCard.fromDict(params["protect"])
            response = player.hand.protect(card)
            if type(response) == str:
                return response
            db.execute("UPDATE traditional_games SET players = %s, p_act = %s WHERE game_id = %s", [self.playersToDb(TraditionalPlayer, TraditionalCard), f"{player.username} protected a {card.val}", self.id])

        elif (params['action'] == "fold" or params['action'] == "bet" or params['action'] == "call" or params['action'] == "raise") and self.phase == "betting" and self.player_turn == player.id:
            players = self.getActivePlayers()

            if params['action'] == "fold":
                player.fold()

                players = self.getActivePlayers()

                

            elif params["action"] == "bet" and players.index(player):
                player.makeBet(params["amount"])

            elif params["action"] == 'call':
                player.makeBet(params["amount"], False)
                player.lastaction = f'calls'

            elif params["action"] == 'raise':
                player.makeBet(params["amount"], False)
                player.lastaction = f'raises to {params["amount"]}'

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
                self.playersToDb(TraditionalPlayer, TraditionalCard),
                self.hand_pot,
                'betting' if nextPlayer != None else 'card',
                nextPlayer if nextPlayer != None else players[0].id,
                player.username + " " + player.lastaction,
                len(players) <= 1,
                self.id
            ]
            db.execute("UPDATE traditional_games SET players = %s, hand_pot = %s, phase = %s, player_turn = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)




        elif (params["action"] == "draw" or params["action"] == "trade" or params["action"] == "stand" or params["action"] == "alderaan") and (self.phase == "card" or self.phase == "alderaan") and self.player_turn == player.id:
            
            if params["action"] == "draw":
                player.hand.cards.append(self.drawFromDeck())
                player.lastaction = "draws"

            elif params["action"] == "trade":
                tradeCard = TraditionalCard.fromDict(params["trade"])

                # The index of the card that is being traded
                tradeDex = player.hand.cards.index(tradeCard)

                # Draw a card and replace the card being traded with it
                player.hand.cards[tradeDex] = self.drawFromDeck()

                player.lastaction = "trades"

            elif params["action"] == "stand":
                player.lastaction = "stands"

            elif params["action"] == "alderaan" and self.cycle_count != 0:
                self.phase = "alderaan"
                player.lastaction = "calls Alderaan"



            # Pass turn to next player
            uDex = self.getPlayerDex(id=player.id)
            nextPlayer = uDex + 1

            # String that shows the winner
            winStr = None

            # If this action was from the last player
            if nextPlayer == len(players):
                self.phase = "shift"
                nextPlayer = 0
                self.cycle_count += 1
                if self.phase == "alderaan":
                    self.phase = "card"
                    # Get end of game data
                    winner, bestHand, bombedOutPlayers = self.alderaan()

                    # Enact the bomb out transactions for all players that bombed out
                    bombOutPrice = int(round(self.hand_pot * .1))
                    for p in bombedOutPlayers:
                        p.credits -= bombOutPrice
                        self.sabacc_pot += bombOutPrice


                    # If someone won (i.e. not everyone bombed out)
                    if winner != None:
                        # Give winner Hand Pot
                        winner.credits += self.hand_pot
                        self.hand_pot = 0

                        # Give winner Sabacc Pot it they had a Sabacc
                        if bestHand == SpecialHands.IDIOTS_ARRAY or (bestHand != SpecialHands.FAIRY_EMPRESS and abs(bestHand) == 23):
                            winner.credits += self.sabacc_pot
                            self.sabacc_pot = 0

                        # Update game and winner string
                        winStr = f"{winner.username} wins!"

                    # If no one won (i.e. everyone bombed out)
                    else:
                        # Hand pot gets added to Sabacc Pot
                        self.sabacc_pot += self.hand_pot

                        # Update winStr
                        winStr = "Everyone bombs out and loses!"

            dbList = [
                self.deck,
                self.playersToDb(TraditionalPlayer, TraditionalCard),
                self.hand_pot,
                self.sabacc_pot,
                self.phase,
                self.getActivePlayers()[nextPlayer].id,
                player.username + " " + player.lastaction if not winStr else winStr,
                self.completed,
                self.id
            ]
            db.execute("UPDATE traditional_games SET deck = %s, players = %s, hand_pot = %s, sabacc_pot = %s, phase = %s, player_turn = %s, cycle_count = %s, p_act = %s, completed = %s WHERE game_id = %s", dbList)

        elif params["action"] == "shift" and self.player_turn == player.id:
            self.rollShift()

            if self._shift:
                self.shift()

            # Set the Shift message
            shiftStr = "Sabacc shift!" if self._shift else "No shift!"

            db.execute(f"UPDATE traditional_games SET phase = %s, deck = %s, players = %s, player_turn = %s, shift = %s, p_act = %s WHERE game_id = %s", ["betting", self.deck.toDb(TraditionalCard), self.playersToDb(TraditionalPlayer, TraditionalCard), self.players[0].id, self._shift, shiftStr, self.id])

        elif params["action"] == "playAgain" and self.player_turn == player.id and self.completed:
            self.nextRound()

            db.execute("UPDATE traditional_games SET players = %s, hand_pot = %s, sabacc_pot = %s, phase = %s, deck = %s, player_turn = %s, cycle_count = %s, p_act = %s, completed = %s WHERE game_id = %s", [self.playersToDb(TraditionalPlayer, TraditionalCard), self.hand_pot, self.sabacc_pot, "betting", self.deck.toDb(TraditionalCard), self.players[0].id, 0, "", False, self.id])

        if self == originalSelf:
            "invalid user input"

        return self