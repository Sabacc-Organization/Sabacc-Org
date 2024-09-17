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
    def __init__(self, id: int, username: str, lastAction: str, positiveCard: Card, negativeCard: Card, chips: int = 8, shiftTokens: list[KesselShiftToken] = []):
        self.id = id
        self.username = username
        self.lastAction = lastAction
        self.positiveCard = positiveCard
        self.negativeCard = negativeCard
        self.chips = chips
        self.shiftTokens = shiftTokens

    def replaceCard(self, suit: str, card: Card):
        if suit == "negative":
            self.negativeCard = card
        elif suit == "positive":
            self.positiveCard = card

    def toDb(self, playerType, cardType, shiftTokenType):

        return playerType.python_type(self.id, self.username, self.lastAction, self.positiveCard.toDb(cardType), self.negativeCard.toDb(cardType), self.chips, [i.toDb(tokenType) for i in self.shiftTokens])

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'lastAction': self.lastAction,
            'positiveCard': self.positiveCard.toDict(),
            'negativeCard': self.negativeCard.toDict(),
            'chips': self.chips,
            'shiftTokens': self.shiftTokens.toDict()
        }

    @staticmethod
    def fromDb(player:object):
        return KesselPlayer(player.id, player.username, player.lastaction, player.positiveCard, player.negativeCard, player.chips, [KesselShiftToken.fromDb(i) for i in player.shiftTokens])

    @staticmethod
    def fromDict(dict:dict):
        return KesselPlayer(id=dict['id'], username=dict['username'], lastAction=dict['lastAction'], positiveCard=dict['positiveCard'], negativeCard=dict['negativeCard'], chips=dict['chips'], shiftTokens=[KesselShiftToken(i) for i in dict['shiftTokens']])

class KesselGame(Game):
    def __init__(self,
        players: list,
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
            players.append(KesselPlayer(playerIds[i], playerUsernames[i], '', positive.draw(), negative.draw(), startingChips))

        game = KesselGame(players=players, player_turn=players[0].id, p_act='', positiveDeck=positive, negativeDeck=negative, positiveDiscard=positive.draw(), negativeDiscard=negative.draw(), cycle_count=0, completed=False)

        if db:
            db.execute("INSERT INTO kessel_games (players, player_turn, p_act, positiveDeck, negativeDeck, positiveDiscard, negativeDiscard) VALUES(%s, %s, %s, %s, %s, %s, %s)", [game.playersToDb(player_type=kesselPlayerType,card_type=kesselCardType), game.positiveDeck, game.negativeDeck, game.positiveDiscard, game.negativeDiscard, game.player_turn, game.p_act])

        return game

    @staticmethod
    def fromDb(game:object):
        return KesselGame( id = game[0],
            players = [KesselGame.fromDb(player) for player in game[1]],
            positiveDeck = KesselDeck.fromDb(game[2]),
            positiveDeck = KesselDeck.fromDb(game[3]),
            positiveDiscard = KesselDeck.fromDb(game[4]),
            negativeDiscard = KesselDeck.fromDb(game[5]),
            player_turn = game[6],
            p_act = game[7],
            cycle_count = game[8],
            completed = game[9])

    def toDb(self, card_type, player_type, includeId=False):
        if includeId:
            return [self.id, self.players.toDb(player_type, card_type), self.player_turn, self.positiveDeck.toDb(card_type), self.negativeDeck.toDb(card_type), self.positiveDiscard.toDb(card_type), self.negativeDiscard.toDb(card_type), self.cycle_count, self.completed]
        else:
            return [self.players.toDb(player_type, card_type), self.player_turn, self.positiveDeck.toDb(card_type), self.negativeDeck.toDb(card_type), self.positiveDiscard.toDb(card_type), self.negativeDiscard.toDb(card_type), self.cycle_count, self.completed]
