from helpers import *
from server.helpers import Deck

kesselCardType = None
kesselPlayerType = None
tokenType = None

class KesselShiftToken():
    def __init__(self, shiftTokenType: str = None) -> None:
        '''
        freeDraw
        refund
        extraRefund
        embezzlement
        majorFraud
        generalTariff
        targetTariff
        generalAudit
        immunity
        exhaustion
        directTransaction
        embargo
        '''
        self.shiftTokenType = shiftTokenType

    def toDict(self) -> dict:
        return {
            'type': self.shiftTokenType
        }

    @staticmethod
    def fromDict(card:dict) -> object:
        return KesselShiftToken(card['type'])

    def toDb(self, tokenType):
        return tokenType.python_type(self.shiftTokenType)

    @staticmethod
    def fromDb(token):
        return KesselShiftToken(token.type)

class KesselDeck(Deck):
    def __init__(self, cardsToExclude: list = []):
        super().__init__()

        for i in range(3):
            for j in range(6):
                self.cards.append(Card(j, 'basic'))
            self.cards.append(Card(0, 'imposter'))
        self.cards.append(Card(0, 'sylop'))

        for card in cardsToExclude:
            self.cards.remove(card)
        self.shuffle()

    @staticmethod
    def fromDb(deck) -> object:
        return KesselDeck([Card.fromDb(card) for card in deck])

class KesselPlayer(Player):
    def __init__(self, id: int, username: str, lastAction: str, positiveCard: Card, negativeCard: Card, chips: int = 8, usedChips: int = 0, shiftTokens: list[KesselShiftToken] = [], outOfGame: bool = False):
        self.id = id
        self.username = username
        self.lastAction = lastAction
        self.positiveCard = positiveCard
        self.negativeCard = negativeCard
        self.chips = chips
        self.usedChips = usedChips
        self.shiftTokens = shiftTokens
        self.outOfGame = outOfGame

    def getHandValue(self):
        if self.positiveCard.suit == "sylop":
            if self.negativeCard.suit == "sylop":
                return (0, 0)
            else:
                return (0, self.negativeCard.val)

        elif self.negativeCard.suit == "sylop":
            if self.positiveCard.suit == "sylop":
                return (0, 0)
            else:
                return (0, self.positiveCard.val)

        else:
            return ((abs(self.positiveCard.val - self.negativeCard.val), min(self.positiveCard.val, self.negativeCard.val)))

    def toDb(self, player_type, card_type, shiftTokenType):

        return player_type.python_type(self.id, self.username, self.lastAction, self.positiveCard.toDb(card_type), self.negativeCard.toDb(card_type), self.chips, self.usedChips, [i.toDb(tokenType) for i in self.shiftTokens], self.outOfGame)

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'lastAction': self.lastAction,
            'positiveCard': self.positiveCard.toDict(),
            'negativeCard': self.negativeCard.toDict(),
            'chips': self.chips,
            'usedChips': self.usedChips,
            'shiftTokens': self.shiftTokens.toDict(),
            'outOfGame': self.outOfGame
        }

    @staticmethod
    def fromDb(player:object):
        return KesselPlayer(player.id, player.username, player.lastaction, player.positiveCard, player.negativeCard, player.chips, player.usedChips, [KesselShiftToken.fromDb(i) for i in player.shiftTokens], player.outOfGame)

    @staticmethod
    def fromDict(dict:dict):
        return KesselPlayer(id=dict['id'], username=dict['username'], lastAction=dict['lastAction'], positiveCard=dict['positiveCard'], negativeCard=dict['negativeCard'], chips=dict['chips'], usedChips=dict['usedChips'], shiftTokens=[KesselShiftToken(i) for i in dict['shiftTokens']], outOfGame=dict['outOfGame'])

class KesselGame(Game):
    def __init__(self,
        players: list[KesselPlayer],
        id: int = None,
        player_turn: int = None,
        p_act='',
        positiveDeck: KesselDeck = None,
        negativeDeck: KesselDeck = None,
        positiveDiscard: list[Card] = None,
        negativeDiscard: list[Card] = None,
        cycle_count=0,
        completed=False):

        super().__init__(players, id, player_turn, p_act, Deck(), '', cycle_count, completed)
        del self.deck
        del self.phase

        self.positiveDeck = positiveDeck
        self.negativeDeck = negativeDeck
        self.positiveDiscard = positiveDiscard
        self.negativeDiscard = negativeDiscard

    @staticmethod
    def newGame(playerIds: list, playerUsernames: list, startingChips=8, db=None):
        if len(playerIds) != len(playerUsernames):
            return "Uneqal amount of ids and usernames"

        if len(playerIds) > 8:
            "Too many players. Max of 8 players."

        if len(playerIds) <= 1:
            "You cannot play by yourself"


        positive = KesselDeck()
        negative = KesselDeck()

        players = []
        for i in range(len(playerIds)):
            players.append(KesselPlayer(playerIds[i], playerUsernames[i], '', positive.draw(), negative.draw(), startingChips, 0, []))

        game = KesselGame(players=players, player_turn=players[0].id, p_act='', positiveDeck=positive, negativeDeck=negative, positiveDiscard=[positive.draw()], negativeDiscard=[negative.draw()], cycle_count=0, completed=False)

        if db:
            db.execute("INSERT INTO kessel_games (players, player_turn, p_act, positiveDeck, negativeDeck, positiveDiscard, negativeDiscard) VALUES(%s, %s, %s, %s, %s, %s, %s)", [game.playersToDb(player_type=kesselPlayerType,card_type=kesselCardType), game.positiveDeck, game.negativeDeck, game.positiveDiscard, game.negativeDiscard, game.player_turn, game.p_act])

        return game

    @staticmethod
    def fromDb(game:object):
        return KesselGame( id = game[0],
            players = [KesselGame.fromDb(player) for player in game[1]],
            positiveDeck = KesselDeck.fromDb(game[2]),
            positiveDeck = KesselDeck.fromDb(game[3]),
            positiveDiscard = [Card.fromDb(i) for i in game[4]],
            negativeDiscard = [Card.fromDb(i) for i in game[5]],
            player_turn = game[6],
            p_act = game[7],
            cycle_count = game[8],
            completed = game[9])

    def toDb(self, player_type, card_type, includeId=False):
        if includeId:
            return [self.id, self.playersToDb(player_type, card_type), self.player_turn, self.positiveDeck.toDb(card_type), self.negativeDeck.toDb(card_type), self.positiveDiscard.toDb(card_type), self.negativeDiscard.toDb(card_type), self.cycle_count, self.completed]
        else:
            return [self.playersToDb(player_type, card_type), self.player_turn, self.positiveDeck.toDb(card_type), self.negativeDeck.toDb(card_type), self.positiveDiscard.toDb(card_type), self.negativeDiscard.toDb(card_type), self.cycle_count, self.completed]

    def playersToDb(self, player_type, card_type):
        return [i.toDb(player_type, card_type) for i in self.players]

    def getActivePlayers(self) -> list[KesselPlayer]:
        activePlayers = []
        for player in self.players:
            if not player.outOfGame:
                activePlayers.append(player)
        return activePlayers

    def trade(self, tradeType: str, player: KesselPlayer, playerKeeps: bool):
        if player.chips == 0:
            return "not enough chips to trade"
        player.chips -= 1

        if tradeType == "positiveDeckTrade":
            if playerKeeps:
                self.positiveDiscard.append(player.positiveCard)
                player.positiveCard = self.positiveDeck.draw()
            else:
                self.positiveDiscard.append(self.positiveDeck.draw())

        elif tradeType == "negativeDeckTrade":
            if playerKeeps:
                self.negativeDiscard.append(player.negativeCard)
                player.negativeCard = self.negativeDeck.draw()
            else:
                self.negativeDiscard.append(self.negativeDeck.draw())

        elif tradeType == "positiveDiscardTrade":
            if playerKeeps:
                temp = self.positiveDiscard.pop()
                self.positiveDiscard.append(player.positiveCard)
                player.positiveCard = temp
            else:
                pass

        elif tradeType == "negativeDiscardTrade":
            if playerKeeps:
                temp = self.negativeDiscard.pop()
                self.negativeDiscard.append(player.negativeCard)
                player.negativeCard = temp
            else:
                pass

    def roundOver(self):
        # determine winners of the hand
        handWinners = []
        winningHand = (6, 6) # distance between cards, lowest card
        for i in self.getActivePlayers():
            tempHand = i.getHandValue()

            if (tempHand[0] < winningHand[0]) or ((tempHand[0] == winningHand[0]) and (tempHand[1] < winningHand[1])):
                winningHand = tempHand

        for i in self.getActivePlayers():
            tempHand = i.getHandValue()

            if tempHand == winningHand:
                handWinners.append(i)

        for i in self.getActivePlayers():
            if i in handWinners:
                i.chips += i.usedChips
            i.usedChips = 0

        # remove players who have no chips.
        for i in self.getActivePlayers():
            if i.chips == 0:
                i.outOfGame = True

        # if someone has won the game, game over.
        if len(self.getActivePlayers() <= 1):
            self.completed = True

        # otherwise, distribute chips to winners, delete chips from losers, reshuffle cards, and deal
        else:
            self.nextHand()

    def nextHand(self):
        self.positiveDeck = KesselDeck()
        self.negativeDeck = KesselDeck()

        self.positiveDiscard = [self.positiveDeck.draw()]
        self.negativeDiscard = [self.negativeDeck.draw()]

        for i in self.getActivePlayers():
            i.positiveCard = self.positiveDeck.draw()
            i.negativeCard = self.negativeDeck.draw()

        self.player_turn = self.getActivePlayers()[0].id

    def action(self, params: dict, db):
        originalSelf = copy.deepcopy(self)

        player: KesselPlayer = self.getPlayer(username=params["username"])

        if (params["action"] in ["positiveDeckTrade", "negativeDeckTrade", "positiveDiscardTrade", "negativeDiscardTrade", "stand"]) and (self.player_turn == player.id) and (self.completed == False):

            if params["action"] != "stand":
                naturalActionWords = {
                    "positiveDeckTrade": "positive deck",
                    "negativeDeckTrade": "negative deck",
                    "positiveDiscardTrade": "positive discard pile",
                    "negativeDiscardTrade": "negative discard pile"
                }
                self.trade(params["action"], player, params["playerKeeps"])
                self.p_act = f'{player.username} trades with {naturalActionWords[params["action"]]}'

            else:
                self.p_act = f'{player.username} stands'

            uDex = self.getPlayerDex(id=player.id)
            nextPlayer = uDex + 1

            if nextPlayer >= len(self.getActivePlayers()):
                nextPlayer = 0
                if self.cycle_count >= 2:
                    self.roundOver()
                else:
                    self.cycle_count += 1

            dbList = [
                self.playersToDb(kesselPlayerType, kesselCardType),
                self.player_turn,
                self.p_act,
                self.positiveDeck,
                self.negativeDeck,
                self.positiveDiscard,
                self.negativeDiscard,
                self.cycle_count,
                self.completed,
                self.id
            ]
            db.execute("UPDATE kessel_games SET players = %s, player_turn = %s, p_act = %s positiveDeck = %s, negativeDeck = %s, positiveDiscard = %s, negativeDiscard = %s, cycle_count = %s, completed = %s  WHERE game_id = %s", dbList)

        elif (params["action"] == "playAgain") and (self.player_turn == player.id) and (self.completed):
            self.nextRound()

            dbList = [
                self.playersToDb(kesselPlayerType, kesselCardType),
                self.players[0].id,
                0,
                "",
                KesselDeck(),
                KesselDeck(),
                [],
                [],
                False,
                self.id
            ]

            db.execute("UPDATE kessel_games SET players = %s, player_turn = %s, cycle_count = %s, p_act = %s, positiveDeck = %s, negativeDeck = %s, positiveDiscard = %s, negativeDiscard = %s, completed = %s WHERE game_id = %s", dbList)


        if self == originalSelf:
            return "invalid user input"

        return self