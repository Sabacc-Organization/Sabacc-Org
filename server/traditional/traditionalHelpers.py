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
    def toDb(self, cardType):
        return cardType.python_type(self.val, self.suit, self.protected)
    def toDict(self):
        return {
            'val': self.val,
            'suit': self.suit,
            'prot': self.protected
        }
    @staticmethod
    def fromDb(card):
        return Card(card.val, card.suit, card.protected)
    @staticmethod
    def fromDict(dict):
        return Card(dict['val'],dict['suit'],dict['prot'])

class Player:
    def __init__(self, id:int, username:str, credits:int, bet:int = None, hand=[], folded=False, lastAction="start"):
        self.id = id
        self.username = username
        self.credits = credits
        self.bet = bet
        self.hand = hand
        self.folded = folded
        self.lastAction = lastAction
    def toDb(self, playerType, cardType):
        for i in range(len(self.hand)):
            self.hand[i] = self.hand[i].toDb(cardType)
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
    def fromDb(player):
        return Player(player.id, player.username, player.credits, player.bet, [Card.fromDb(card) for card in player.hand], player.folded, player.lastaction)
    @staticmethod
    def fromDict(dict):
        return Player(id=dict['id'],username=dict['username'],credits=dict['credits'],bet=dict['bet'],hand=[Card.fromDict(card) for card in dict['hand']],folded=dict['folded'],lastAction=dict['lastAction'])
    
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
    def toDb(self, card_type, player_type):
        return [self.id, [player.toDb(player_type, card_type) for player in self.players], self.hand_pot, self.sabacc_pot, self.phase, [card.toDb(card_type) for card in self.deck], self.player_turn, self.p_act, self.cycle_count, self.shift, self.completed]
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
    @staticmethod
    def fromDb(game):
        return Game(id=game[0],players=[Player.fromDb(player) for player in game[1]], hand_pot=game[2], sabacc_pot=game[3], phase=game[4], deck=[Card.fromDb(card) for card in game[5]], player_turn=game[6],p_act=game[7],cycle_count=game[8],shift=game[9],completed=game[10])
    @staticmethod
    def fromDict(dict):
        return Game(dict['id'],[Player.fromDict(player) for player in dict['players']],[Card.fromDict(card) for card in dict['deck']],dict['player_turn'],dict['p_act'],dict['hand_pot'],dict['sabacc_pot'],dict['phase'],dict['cycle_count'],dict['shift'],dict['completed'])

    def containsPlayer(self, player_id):
        return player_id in [player.id for player in self.players]