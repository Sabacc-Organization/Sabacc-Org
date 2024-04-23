class Suit:
    FLASKS = 'flasks'
    SABERS = 'sabers'
    STAVES = 'staves'
    COINS = 'coins'
    NEGATIVE_NEUTRAL = 'negative/neutral'

class Card:
    def __init__(self, val:int, suit:Suit, protected=False):
        self.val = val
        self.suit = suit
        self.protected = protected
    def __str__(self) -> str:
        return f"{self.val} of {str(self.suit)}{' (protected)' if self.protected else ''}"
    def toDatabaseVersion(self, cardType):
        return cardType.python_type(self.val, self.suit, self.protected)
    @staticmethod
    def copy(card):
        return Card(card.val, card.suit, card.protected)
    

class Player:
    def __init__(self, id:int, username:str, credits:int, bet:int = None, hand=[], folded=False, lastAction="start"):
        self.id = id
        self.username = username
        self.credits = credits
        self.bet = bet
        self.hand = hand
        self.folded = folded
        self.lastAction = lastAction
    def toDatabaseVersion(self, playerType, cardType):
        for card in self.hand:
            card = card.toDatabaseVersion(cardType)
        return playerType.python_type(self.id, self.username, self.credits, self.bet, self.hand, self.folded, self.lastAction)