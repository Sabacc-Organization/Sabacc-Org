class Card:
    def __init__(self, val, suit):
        self.value = val
        self.suit = suit
        self.protected = False

class Player:
    def __init__(self, id, username, startingCredits):
        self.id = id
        self.username = username
        self.credits = startingCredits
        self.bet = None
        self.hand = []
        self.folded = False
        self.lastAction = "start"