from helpers import *
from server.helpers import Deck

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

class KesselPlayer(Player):
    def __init__(self, id: int, username: str, lastAction: str, positiveCard: Card, negativeCard: Card, chips: int = 8):
        self.id = id
        self.username = username
        self.lastAction = lastAction
        self.positiveCard = positiveCard
        self.negativeCard = negativeCard
        self.chips = chips

    def replaceCard(self, suit: str, card: Card):
        if suit == "negative":
            self.negativeCard = card
        elif suit == "positive":
            self.positiveCard = card

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

        return KesselGame(players=players, player_turn=players[0].id, p_act='', positiveDeck=positive, negativeDeck=negative, positiveDiscard=positive.draw(), negativeDiscard=negative.draw(), cycle_count=0, completed=False)