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
    def toDict(self):
        return {
            'val': self.val,
            'suit': self.suit,
            'prot': self.protected
        }
    @staticmethod
    def fromDatabaseVersion(card):
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
        for i in range(len(self.hand)):
            self.hand[i] = self.hand[i].toDatabaseVersion(cardType)
        return playerType.python_type(self.id, self.username, self.credits, self.bet, self.hand, self.folded, self.lastAction)
    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'credits': self.credits,
            'bet': self.bet,
            'hand': [card.toDict() for card in self.hand],
            'folded': self.folded,
            'lastAction': self.lastAction
        }
    @staticmethod
    def fromDatabaseVersion(player):
        return Player(player.id, player.username, player.credits, player.bet, [Card.fromDatabaseVersion(card) for card in player.hand], player.folded, player.lastaction)
    
class Game:
    def __init__(self, id:int, players, deck, player_turn:int, p_act:str, hand_pot=0, sabacc_pot=0, phase='betting', cycle_count=0, shift=False, completed=False):
        self.id = id
        self.players = players
        self.hand_pot = hand_pot
        self.sabacc_pot = sabacc_pot
        self.phase = phase
        self.deck = deck
        self.player_turn = player_turn
        self.p_act = p_act
        self.cycle_count = cycle_count
        self.shift = shift
        self.completed = completed
    def toDict(self):
        return {
            'id': self.id,
            'players': [player.toDict() for player in self.players],
            'hand_pot': self.hand_pot,
            'sabacc_pot': self.sabacc_pot,
            'phase': self.phase,
            'deck': [card.toDict() for card in self.deck],
            'player_turn': self.player_turn,
            'p_act': self.p_act,
            'cycle_count': self.cycle_count,
            'shift': self.shift,
            'completed': self.completed
        }
    def toDb(self, card_type, player_type):
        return [self.id, [player.toDatabaseVersion(player_type, card_type) for player in self.players], self.hand_pot, self.sabacc_pot, self.phase, [card.toDatabaseVersion(card_type) for card in self.deck], self.player_turn, self.p_act, self.cycle_count, self.shift, self.completed]
    @staticmethod
    def fromDb(game):
        return Game(id=game[0],players=[Player.fromDatabaseVersion(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=[Card.fromDatabaseVersion(card) for card in game[5]], player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10])