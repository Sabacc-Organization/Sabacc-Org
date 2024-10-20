from helpers import *
import json
from datetime import datetime, timezone

kesselCardType = None
kesselPlayerType = None

shiftTokenTypes = [
    "freeDraw",
    "refund",
    "extraRefund",
    "embezzlement",
    "majorFraud",
    "generalTariff",
    "targetTariff",
    "generalAudit",
    "targetAudit",
    "immunity",
    "exhaustion",
    "directTransaction",
    "embargo",
    "markdown",
    "cookTheBooks",
    "primeSabacc"
]

class KesselDeck(Deck):
    def __init__(self, cardsToExclude: list = []):
        super().__init__()

        for i in range(3):
            for j in range(6):
                self.cards.append(Card(j+1, 'basic'))
            self.cards.append(Card(0, 'imposter'))
        self.cards.append(Card(0, 'sylop'))

        for card in cardsToExclude:
            self.cards.remove(card)
        self.shuffle()

    @staticmethod
    def fromDb(deck) -> object:
        return KesselDeck([Card.fromDb(card) for card in deck])

class KesselPlayer(Player):
    def __init__(self, id: int, username: str, lastAction: str, positiveCard: Card, negativeCard: Card, extraCard: Card = None, extraCardIsNegative: bool = False, chips: int = 8, usedChips: int = 0, shiftTokens: list[str] = [], outOfGame: bool = False):
        self.id = id
        self.username = username
        self.lastAction = lastAction
        self.positiveCard = positiveCard
        self.negativeCard = negativeCard
        self.extraCard = extraCard
        self.extraCardIsNegative = extraCardIsNegative
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

    def extraCardToDb(self, card_type):
        if self.extraCard is None:
            return None
        else:
            return self.extraCard.toDb(cardType=card_type)
    
    def extraCardToDict(self):
        if self.extraCard is None:
            return None
        else:
            return self.extraCard.toDict()

    def toDb(self, player_type, card_type):
        return player_type.python_type(
            self.id,
            self.username,
            self.chips,
            self.usedChips,
            self.positiveCard.toDb(card_type),
            self.negativeCard.toDb(card_type),
            self.extraCardToDb(card_type),
            self.extraCardIsNegative,
            self.shiftTokens,
            self.outOfGame,
            self.lastAction
        )

    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'lastAction': self.lastAction,
            'positiveCard': self.positiveCard.toDict(),
            'negativeCard': self.negativeCard.toDict(),
            'extraCard': self.extraCardToDict(),
            'extraCardIsNegative': self.extraCardIsNegative,
            'chips': self.chips,
            'usedChips': self.usedChips,
            'shiftTokens': self.shiftTokens,
            'outOfGame': self.outOfGame
        }

    @abstractmethod
    def extraCardFromDb(fromDb):
        if fromDb is None:
            return None
        else:
            return Card.fromDb(fromDb)

    @staticmethod
    def fromDb(player:object):
        return KesselPlayer(
            player.id,
            player.username,
            player.lastaction,
            Card.fromDb(player.positivecard),
            Card.fromDb(player.negativecard),
            KesselPlayer.extraCardFromDb(player.extracard),
            player.extracardisnegative,
            player.chips,
            player.usedchips,
            player.shifttokens.strip('}{').split(','),
            player.outofgame
        )

    @staticmethod
    def fromDict(dict:dict):
        return KesselPlayer(id=dict['id'], username=dict['username'], lastAction=dict['lastAction'], positiveCard=dict['positiveCard'], negativeCard=dict['negativeCard'], extraCard=dict["extraCard"], extraCardIsNegative=dict["extraCardIsNegative"], chips=dict['chips'], usedChips=dict['usedChips'], shiftTokens=dict["shiftTokens"], outOfGame=dict['outOfGame'])

defaultSettings = {
    "startingChips": 8,
    "playersChooseShiftTokens": False
}

class KesselGame(Game):
    def __init__(self,
        players: list[KesselPlayer],
        id: int = None,
        player_turn: int = None,
        p_act = '',
        phase = 'draw',
        dice = (1, 1),
        positiveDeck: KesselDeck = None,
        negativeDeck: KesselDeck = None,
        positiveDiscard: list[Card] = None,
        negativeDiscard: list[Card] = None,
        activeShiftTokens: list[list[str, str]] = [],
        cycle_count=0,
        completed=False,
        settings = defaultSettings,
        created_at = None,
        move_history = None):

        super().__init__(players, id, player_turn, p_act, None, phase, cycle_count, completed, settings = settings, created_at = created_at, move_history = move_history)
        del self.shift
        del self.deck

        self.dice = dice
        self.positiveDeck = positiveDeck
        self.negativeDeck = negativeDeck
        self.positiveDiscard = positiveDiscard
        self.negativeDiscard = negativeDiscard
        self.activeShiftTokens = activeShiftTokens

    @staticmethod
    def newGame(playerIds: list, playerUsernames: list, settings=defaultSettings, db=None):
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
            shiftTokens = []
            if settings["playersChooseShiftTokens"] is False:
                shiftTokens = [random.choice(shiftTokenTypes) for _ in range(3)]
            players.append(KesselPlayer(playerIds[i], playerUsernames[i], '', positive.draw(), negative.draw(), None, False, settings["startingChips"], 0, shiftTokens))

        game = KesselGame(
            players = players,
            player_turn=players[0].id,
            p_act = '',
            phase = 'shiftTokenSelect' if settings["playersChooseShiftTokens"] else 'draw',
            positiveDeck = positive,
            negativeDeck = negative,
            positiveDiscard = [positive.draw()],
            negativeDiscard = [negative.draw()],
            activeShiftTokens = [],
            cycle_count = 0,
            completed = False,
            settings = settings
        )
        game.rollDice()

        if db:
            db.execute("INSERT INTO kessel_games (players, phase, dice, positiveDeck, negativeDeck, positiveDiscard, negativeDiscard, activeShiftTokens, player_turn, p_act, settings) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                game.playersToDb(player_type=kesselPlayerType, card_type=kesselCardType),
                game.phase,
                list(game.dice),
                game.positiveDeck.toDb(kesselCardType),
                game.negativeDeck.toDb(kesselCardType),
                [card.toDb(kesselCardType) for card in game.positiveDiscard],
                [card.toDb(kesselCardType) for card in game.negativeDiscard],
                game.activeShiftTokens,
                game.player_turn,
                game.p_act,
                json.dumps(game.settings)
            ])

        return game

    def getClientData(self, user_id = None, username = None):
        player: Player = self.getPlayer(username, user_id)

        gameDict = self.toDict()
        users = [i.username for i in self.getActivePlayers()]

        gameDict.pop("positiveDeck")
        gameDict.pop("negativeDeck")

        return {"message": "Good luck!", "gata": gameDict, "users": users, "user_id": int(player.id), "username": player.username}

    @staticmethod
    def fromDb(game:object):
        return KesselGame( id = game[0],
            players = [KesselPlayer.fromDb(player) for player in game[1]],
            phase = game[2],
            dice = game[3],
            positiveDeck = KesselDeck.fromDb(game[4]),
            negativeDeck = KesselDeck.fromDb(game[5]),
            positiveDiscard = [Card.fromDb(i) for i in game[6]],
            negativeDiscard = [Card.fromDb(i) for i in game[7]],
            activeShiftTokens = game[8],
            player_turn = game[9],
            p_act = game[10],
            cycle_count = game[11],
            completed = game[12],
            settings = game[13],
            created_at = game[14],
            move_history = game[15]
        )

    def toDb(self, player_type, card_type, includeId=False):
        if includeId:
            return [
                self.id,
                self.playersToDb(player_type, card_type),
                self.phase,
                list(self.dice),
                self.positiveDeck.toDb(card_type),
                self.negativeDeck.toDb(card_type),
                self.positiveDiscard.toDb(card_type),
                self.negativeDiscard.toDb(card_type),
                self.activeShiftTokens,
                self.player_turn,
                self.cycle_count,
                self.completed,
                json.dumps(self.settings),
                self.created_at,
                self.moveHistoryToDb()
            ]
        else:
            return [
                self.playersToDb(player_type, card_type),
                self.phase,
                list(self.dice),
                self.positiveDeck.toDb(card_type),
                self.negativeDeck.toDb(card_type),
                self.positiveDiscard.toDb(card_type),
                self.negativeDiscard.toDb(card_type),
                self.activeShiftTokens,
                self.player_turn,
                self.cycle_count,
                self.completed,
                json.dumps(self.settings),
                self.created_at,
                self.moveHistoryToDb()
            ]

    def toDict(self):
        return {
            "id": self.id,
            "players": [i.toDict() for i in self.players],
            "phase": self.phase,
            "dice": list(self.dice),
            "positiveDeck": self.positiveDeck.toDict(),
            "negativeDeck": self.negativeDeck.toDict(),
            "positiveDiscard": [i.toDict() for i in self.positiveDiscard],
            "negativeDiscard": [i.toDict() for i in self.negativeDiscard],
            "activeShiftTokens": self.activeShiftTokens,
            "player_turn": self.player_turn,
            "p_act": self.p_act,
            "cycle_count": self.cycle_count,
            "completed": self.completed,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "move_history": self.move_history
        }

    def playersToDb(self, player_type, card_type):
        return [i.toDb(player_type, card_type) for i in self.players]

    def getActivePlayers(self) -> list[KesselPlayer]:
        activePlayers = []
        for player in self.players:
            if not player.outOfGame:
                activePlayers.append(player)
        return activePlayers

    def rollDice(self):
        self.dice = (random.randint(1, 6), random.randint(1, 6))

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

    def handOver(self):
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
            else:
                i.chips -= min(i.getHandValue()[0], 1)
            i.usedChips = 0

        # remove players who have no chips.
        for i in self.getActivePlayers():
            if i.chips <= 0:
                i.chips = 0
                i.outOfGame = True

        # if someone has won the game, game over.
        if len(self.getActivePlayers() <= 1):
            self.completed = True

        # otherwise, distribute chips to winners, delete chips from losers, reshuffle cards, and deal
        self.phase = "reveal"

    def nextHand(self):
        self.positiveDeck = KesselDeck()
        self.negativeDeck = KesselDeck()

        self.positiveDiscard = [self.positiveDeck.draw()]
        self.negativeDiscard = [self.negativeDeck.draw()]

        for i in self.getActivePlayers():
            i.positiveCard = self.positiveDeck.draw()
            i.negativeCard = self.negativeDeck.draw()
            i.extraCard = None
            i.usedChips = 0

        self.player_turn = self.getActivePlayers()[0].id
        self.cycle_count = 0

    def unRolledImposters(self):
        nextPlayer = 0
        otherImposter = False
        while nextPlayer < len(self.getActivePlayers()):
            cond1 = (self.getActivePlayers()[nextPlayer].positiveCard.suit == "imposter") and (self.getActivePlayers()[nextPlayer].positiveCard.val == 0)
            cond2 = (self.getActivePlayers()[nextPlayer].negativeCard.suit == "imposter") and (self.getActivePlayers()[nextPlayer].negativeCard.val == 0)
            if cond1 or cond2:
                otherImposter = True
                self.phase = "imposterRoll"

        return nextPlayer if otherImposter else None

    def action(self, params: dict, db):
        originalSelf = copy.deepcopy(self)

        player: KesselPlayer = self.getPlayer(username=params["username"])

        if (params["action"] in ["positiveDeckTrade", "negativeDeckTrade", "positiveDiscardTrade", "negativeDiscardTrade", "stand"]) and (self.player_turn == player.id) and (self.phase == "normal") and (self.completed == False):

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
                    self.handOver()
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

        elif (params["action"] == "shiftTokenSelect") and (self.player_turn == player.id) and (self.phase == "shiftTokenSelect") and (self.completed == False):
            if len(player.shiftTokens) >= 3:
                return "too many shift tokens"

            player.shiftTokens.append(params["shiftToken"])

            if len(player.shiftTokens) >= 3:
                uDex = self.getActivePlayers().index(player)
                nextPlayer = uDex + 1
                if nextPlayer >= len(self.getActivePlayers()):
                    nextPlayer = 0
                    self.phase = "draw"

                self.player_turn = self.getActivePlayers()[nextPlayer].id

        elif (params["action"] == "imposterRoll") and (self.player_turn == player.id) and (self.phase == "imposterRoll") and (self.completed == False):
            self.rollDice()
            self.phase = "imposterChoice"

        elif (params["action"] in ("positiveDeckDraw", "negativeDeckDraw", "positiveDiscardDraw", "negativeDiscardDraw")) and (self.player_turn == player.id) and (self.phase == "draw") and (self.completed == False):
            print(f'aery {params["action"]}')
            if player.extraCard is not None:
                print(player.extraCard)
                print("player already has extra card")
                return "player already has extra card"

            if player.chips == 0:
                print("not enough chips to draw")
                return "not enough chips to draw"

            player.chips -= 1
            player.usedChips += 1

            if params["action"] == "positiveDeckDraw":
                player.extraCard = self.positiveDeck.draw()
                player.extraCardIsNegative = False
            elif params["action"] == "negativeDeckDraw":
                player.extraCard = self.negativeDeck.draw()
                player.extraCardIsNegative = True
            elif params["action"] == "positiveDiscardDraw":
                player.extraCard = self.positiveDiscard.pop()
                player.extraCardIsNegative = False
            elif params["action"] == "negativeDiscardDraw":
                player.extraCard = self.negativeDiscard.pop()
                player.extraCardIsNegative = True

            self.phase = "discard"

        elif (params["action"] == "discard") and (self.player_turn == player.id) and (self.phase == "discard") and (self.completed == False):
            if player.extraCard is None:
                return "player doesnt have an extra card to discard"
            if params["keep"] is True:
                if player.extraCardIsNegative:
                    self.negativeDiscard.append(player.negativeCard)
                    player.negativeCard = player.extraCard
                    player.extraCard = None
                else:
                    self.positiveDiscard.append(player.positiveCard)
                    player.positiveCard = player.extraCard
                    player.extraCard = None
            else:
                if player.extraCardIsNegative:
                    self.negativeDiscard.append(player.extraCard)
                    player.extraCard = None
                else:
                    self.positiveDiscard.append(player.extraCard)
                    player.extraCard = None

            uDex = self.getActivePlayers().index(player)
            nextPlayer = uDex + 1
            if nextPlayer >= len(self.getActivePlayers()):
                nextPlayer = 0
                if self.cycle_count >= 2:
                    otherImposter = self.unRolledImposters()
                    if otherImposter is None:
                        self.phase = "reveal"

        elif (params["action"] == "imposterChoice") and (self.player_turn == player.id) and (self.phase == "imposterChoice") and (self.completed == False):
            rollingCard = player.negativeCard if params["negatvie"] else player.positiveCard
            if rollingCard.suit == "imposter" and rollingCard.val == 0:
                rollingCard.val == self.dice[params["die"]]

            otherImposter = self.unRolledImposters()

            if otherImposter is None:
                self.phase = "reveal"
                nextPlayer = 0
            else:
                nextPlayer = otherImposter

            self.player_turn = self.getActivePlayers()[nextPlayer].id

        elif (params["action"] == "nextHand") and (self.player_turn == player.id) and (self.phase == "reveal") and (self.completed == False):
            self.nextHand()

        elif (params["action"] == "playAgain") and (self.player_turn == player.id) and (self.phase == "reveal") and (self.completed):
            self.nextRound()

        dbList = [
            self.playersToDb(kesselPlayerType, kesselCardType),
            self.phase,
            self.dice,
            self.positiveDeck.toDb(kesselCardType),
            self.negativeDeck.toDb(kesselCardType),
            [i.toDb(kesselCardType) for i in self.positiveDiscard],
            [i.toDb(kesselCardType) for i in self.negativeDiscard],
            self.activeShiftTokens,
            self.player_turn,
            self.p_act,
            self.cycle_count,
            self.completed,
            self.id
        ]

        db.execute("UPDATE kessel_games SET players = %s, phase = %s, dice = %s, positiveDeck = %s, negativeDeck = %s, positiveDiscard = %s, negativeDiscard = %s, activeShiftTokens = %s, player_turn = %s, p_act = %s, cycle_count = %s, completed = %s WHERE game_id = %s", dbList)

        originalChangedValues = self.compare(originalSelf)
        if originalChangedValues == {}:
            print("invalid user input")
            return "invalid user input"

        originalChangedValues["timestamp"] = datetime.now(timezone.utc).isoformat()
        if self.move_history:
            self.move_history.append(originalChangedValues)
        else:
            self.move_history = [originalChangedValues]

        db.execute("UPDATE kessel_games SET move_history = %s WHERE game_id = %s", [self.moveHistoryToDb(), self.id])

        return self