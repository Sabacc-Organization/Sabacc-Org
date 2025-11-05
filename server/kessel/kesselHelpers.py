from helpers import *
import json
from datetime import datetime, timezone
from typing import Union

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
    def __init__(self, cards: list = None):
        super().__init__()

        if cards is None:
            for i in range(3):
                for j in range(6):
                    self.cards.append(Card(j+1, 'basic'))
                self.cards.append(Card(0, 'imposter'))
            self.cards.append(Card(0, 'sylop'))

        else:
            self.cards.extend(cards)

        self.shuffle()

    @staticmethod
    def fromDb(deck: Union[str, list]) -> object:
        if isinstance(deck, str):
            return KesselDeck.fromDict(json.loads(deck))
        if isinstance(deck, list):
            return KesselDeck.fromDict(deck)

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

    def getHandValue(self, markdown = False):
        if markdown is False:
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

        return ((abs(self.positiveCard.val - self.negativeCard.val), min(self.positiveCard.val, self.negativeCard.val)))

    def extraCardToDb(self):
        if self.extraCard is None:
            return None
        else:
            return self.extraCard.toDb()

    def extraCardToDict(self):
        if self.extraCard is None:
            return None
        else:
            return self.extraCard.toDict()

    def toDb(self):
        return json.dumps(self.toDict())

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

    @staticmethod
    def extraCardFromDb(fromDb):
        if fromDb is None:
            return None
        else:
            return Card.fromDb(fromDb)

    @staticmethod
    def shiftTokensFromDb(string):
        retList = string.strip("}{").split(',')
        if retList == ['']:
            retList = []
        return retList

    @staticmethod
    def fromDb(player: Union[str, dict]) -> object:
        if isinstance(player, str):
            return KesselPlayer.fromDict(json.loads(player))
        if isinstance(player, dict):
            return KesselPlayer.fromDict(player)

    @staticmethod
    def fromDict(dict: dict):
        return KesselPlayer(id=dict['id'], username=dict['username'], lastAction=dict['lastAction'], positiveCard=Card.fromDict(dict['positiveCard']), negativeCard=Card.fromDict(dict['negativeCard']), extraCard=Card.fromDict(dict["extraCard"]), extraCardIsNegative=dict["extraCardIsNegative"], chips=dict['chips'], usedChips=dict['usedChips'], shiftTokens=dict["shiftTokens"], outOfGame=dict['outOfGame'])


# Default game settings 
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

        print(settings)
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
            phase = 'shiftTokenSelect' if settings["playersChooseShiftTokens"] is True else 'draw',
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
            db.execute("INSERT INTO kessel_games (players, phase, dice, positiveDeck, negativeDeck, positiveDiscard, negativeDiscard, activeShiftTokens, player_turn, p_act, settings) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
                game.playersToDb(),
                game.phase,
                game.diceToDb(),
                game.positiveDeckToDb(),
                game.negativeDeckToDb(),
                game.positiveDiscardToDb(),
                game.negativeDiscardToDb(),
                game.activeShiftTokensToDb(),
                game.player_turn,
                game.p_act,
                game.settingsToDb()
            ])

        return game

    def getClientData(self, user_id = None, username = None):
        player: Player = self.getPlayer(username, user_id)

        gameDict = self.toDict()
        users = [i.username for i in self.getActivePlayers()]

        if (self.completed is False) and (not self.phase in ('reveal', 'imposterRoll', 'imposterChoice')):
            for p in gameDict['players']:
                if p['id'] == player.id:
                    continue

                p['positiveCard']['suit'] = 'hidden'
                p['positiveCard']['val'] = 0
                p['negativeCard']['suit'] = 'hidden'
                p['negativeCard']['val'] = 0

                if p['extraCard'] is not None:
                    p['extraCard']['suit'] = 'hidden'
                    p['extraCard']['val'] = 0

        gameDict.pop("positiveDeck")
        gameDict.pop("negativeDeck")

        return {"message": "Good luck!", "gata": gameDict, "users": users, "user_id": int(player.id), "username": player.username}
    
    def positiveDeckToDb(self):
        return self.positiveDeck.toDb()

    def negativeDeckToDb(self):
        return self.negativeDeck.toDb()
    
    def positiveDiscardToDb(self):
        return json.dumps(self.discardPileToDict(self.positiveDiscard))

    def negativeDiscardToDb(self):
        return json.dumps(self.discardPileToDict(self.negativeDiscard))
    
    def discardPileToDict(self, discardPile):
        return [card.toDict() for card in discardPile]
    
    def activeShiftTokensToDb(self):
        return json.dumps(self.activeShiftTokens)

    @staticmethod
    def fromDb(game: list):
        return KesselGame( id = game[0],
            players = [KesselPlayer.fromDb(player) for player in json.loads(game[1])],
            phase = game[2],
            dice = json.loads(game[3]),
            positiveDeck = KesselDeck.fromDb(game[4]),
            negativeDeck = KesselDeck.fromDb(game[5]),
            positiveDiscard = [Card.fromDb(i) for i in json.loads(game[6])],
            negativeDiscard = [Card.fromDb(i) for i in json.loads(game[7])],
            activeShiftTokens = json.loads(game[8]),
            player_turn = game[9],
            p_act = game[10],
            cycle_count = game[11],
            completed = game[12],
            settings = json.loads(game[13]),
            created_at = game[14],
            move_history = None if not game[15] else json.loads(game[15])
        )
    
    @staticmethod
    def fromDict(dict: dict) -> object:
        return KesselGame(
            id = dict['id'],
            players = [KesselPlayer.fromDict(player) for player in dict['players']],
            phase = dict['phase'],
            dice = dict['dice'],
            positiveDeck = KesselDeck.fromDict(dict['positiveDeck']),
            negativeDeck = KesselDeck.fromDict(dict['negativeDeck']),
            positiveDiscard = [Card.fromDict(i) for i in dict['positiveDiscard']],
            negativeDiscard = [Card.fromDict(i) for i in dict['negativeDiscard']],
            activeShiftTokens = dict['activeShiftTokens'],
            player_turn = dict['player_turn'],
            p_act = dict['p_act'],
            cycle_count = dict['cycle_count'],
            completed = dict['completed'],
            settings = dict['settings'],
            created_at = dict['created_at'],
            move_history = dict['move_history']
        )

    def toDb(self, includeId=False):

        dbGame = [
            self.id,
            self.playersToDb(),
            self.phase,
            self.diceToDb(),
            self.positiveDeckToDb(),
            self.negativeDeckToDb(),
            self.positiveDiscardToDb(),
            self.negativeDiscardToDb(),
            self.activeShiftTokensToDb(),
            self.player_turn,
            self.p_act,
            self.cycle_count,
            self.completed,
            self.settingsToDb(),
            self.created_at,
            self.moveHistoryToDb()
        ]

        if includeId == False:
            dbGame.pop(0)

        return dbGame

    def toDict(self):
        return {
            "id": self.id,
            "players": [i.toDict() for i in self.players],
            "phase": self.phase,
            "dice": self.dice,
            "positiveDeck": self.positiveDeck.toDict(),
            "negativeDeck": self.negativeDeck.toDict(),
            "positiveDiscard": self.discardPileToDict(self.positiveDiscard),
            "negativeDiscard": self.discardPileToDict(self.negativeDiscard),
            "activeShiftTokens": self.activeShiftTokens,
            "player_turn": self.player_turn,
            "p_act": self.p_act,
            "cycle_count": self.cycle_count,
            "completed": self.completed,
            "settings": self.settings,
            "created_at": self.created_at,
            "move_history": self.move_history
        }

    def playersToDb(self):
        return json.dumps([player.toDict() for player in self.players])
    
    def diceToDb(self):
        return json.dumps(self.dice)

    def getActivePlayers(self) -> list[KesselPlayer]:
        activePlayers = []
        for player in self.players:
            if not player.outOfGame:
                activePlayers.append(player)
        return activePlayers

    def rollDice(self):
        self.dice = (random.randint(1, 6), random.randint(1, 6))

    @staticmethod
    def cardToString(card, negative):
        retStr = 'negative ' if negative else 'positive '
        if card.suit == "sylop":
            retStr += 'sylop'
        elif card.suit == 'imposter':
            if card.val == 0:
                retStr += 'imposter'
            else:
                retStr += f'imposter ({card.val})'
        else:
            retStr += str(card.val)
        return retStr

    @staticmethod
    def namesToString(names):
        if len(names) == 0:
            return ''
        if len(names) == 1:
            return names[0]

        retStr = ''
        if len(names) == 2:
            retStr = f'{names[0]} and {names[1]}'

        else:
            for i in names[0:-1]:
                retStr += f'{i}, '
            retStr += f'and {names[-1]}'

        return retStr

    @staticmethod
    def camelToNatural(string: str):
        retStr = ''
        for i in string:
            if i.isupper():
                retStr += ' ' + i.lower()
            else:
                retStr += i
        return retStr

    def nextRound(self):
        self.activeShiftTokens = []

        self.positiveDeck = KesselDeck()
        self.negativeDeck = KesselDeck()

        self.positiveDiscard = [self.positiveDeck.draw()]
        self.negativeDiscard = [self.negativeDeck.draw()]

        newPlayers = []
        for i in range(len(self.players)):
            newPlayers.append(self.players[(i + 1) % len(self.players)])
        self.players = newPlayers

        for i in self.players:
            i.shiftTokens = []
            i.outOfGame = False
            i.chips = self.settings["startingChips"]
            i.usedChips = 0
            if self.settings["playersChooseShiftTokens"] is False:
                i.shiftTokens = [random.choice(shiftTokenTypes) for _ in range(3)]

        for i in self.getActivePlayers():
            i.positiveCard = self.positiveDeck.draw()
            i.negativeCard = self.negativeDeck.draw()
            i.extraCard = None

        self.player_turn = self.getActivePlayers()[0].id
        self.cycle_count = 0

        if self.settings["playersChooseShiftTokens"]:
            self.phase = "shiftTokenSelect"
        else:
            self.phase = "draw"
        self.p_act = ""
        self.rollDice()
        self.completed = False

    def handOver(self):
        self.player_turn = self.getActivePlayers()[0].id
        # determine winners of the hand
        handWinners = []

        markdown = ["markdown", ""] in self.activeShiftTokens
        primeSabacc = -1
        for i in self.activeShiftTokens:
            if i[0] == "primeSabacc":
                if i[1].isdigit():
                    primeSabacc = i[1]

        if ["cookTheBooks", ""] in self.activeShiftTokens:
            winningHand = (6, 0)

            for i in self.getActivePlayers():
                tempHand = i.getHandValue(markdown)

                if (tempHand[0] < winningHand[0]) or ((tempHand[0] == winningHand[0]) and (tempHand[1] > winningHand[1] or tempHand[1] == primeSabacc)):
                    winningHand = tempHand

        else:
            winningHand = (6, 6) # distance between cards, lowest card

            for i in self.getActivePlayers():
                tempHand = i.getHandValue(markdown)

                if (tempHand[0] < winningHand[0]) or ((tempHand[0] == winningHand[0]) and (tempHand[1] < winningHand[1] or tempHand[1] == primeSabacc)):
                    winningHand = tempHand

        for i in self.getActivePlayers():
            tempHand = i.getHandValue(markdown)

            if tempHand == winningHand:
                handWinners.append(i)

        if len(handWinners) == 1:
            winner = handWinners[0]
            if winningHand == (0, 0):
                self.p_act = f'{winner.username} got a pure sabacc and won the hand!'
            elif winningHand[0] == 0:
                self.p_act = f'{winner.username} got a {winningHand[1]} sabacc and won the hand!'
            else:
                self.p_act = f'{winner.username} won the hand with a {KesselGame.cardToString(winner.negativeCard, True)} and a {KesselGame.cardToString(winner.positiveCard, False)}'
        else:
            if winningHand[0] == 0:
                self.p_act = f'players {KesselGame.namesToString([i.username for i in handWinners])} got a {winningHand[1]} sabacc and won the hand!'
            else:
                self.p_act = f'players {KesselGame.namesToString([i.username for i in handWinners])} won the hand with a card difference of {winningHand[0]}'

        for i in self.getActivePlayers():
            if i in handWinners:
                i.chips += i.usedChips
            else:
                i.chips -= min(i.getHandValue(markdown)[0], 1)
            i.usedChips = 0

        # remove players who have no chips.
        for i in self.getActivePlayers():
            if i.chips <= 0:
                i.chips = 0
                i.outOfGame = True

        # if someone has won the game, game over.
        if len(self.getActivePlayers()) <= 1:
            self.completed = True

        newActiveShiftTokens = []
        for i in self.activeShiftTokens:
            if i == ["markdown", ""]:
                continue
            elif i == ["cookTheBooks", ""]:
                continue
            elif i[0] == "primeSabacc" and i[1].isdigit():
                continue
            newActiveShiftTokens.append(i)
        self.activeShiftTokens = newActiveShiftTokens

        self.phase = "reveal"

    def nextHand(self):
        self.phase = "draw"
        self.activeShiftTokens = []

        self.positiveDeck = KesselDeck()
        self.negativeDeck = KesselDeck()

        self.positiveDiscard = [self.positiveDeck.draw()]
        self.negativeDiscard = [self.negativeDeck.draw()]

        newPlayers = []
        for i in range(len(self.players)):
            newPlayers.append(self.players[(i + 1) % len(self.players)])
        self.players = newPlayers

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
                break
            nextPlayer += 1

        return nextPlayer if otherImposter else None

    def playerTurnOver(self, player):
        uDex = self.getActivePlayers().index(player)
        nextPlayer = uDex + 1
        if nextPlayer >= len(self.getActivePlayers()):
            nextPlayer = 0
            if self.cycle_count >= 2:
                otherImposter = self.unRolledImposters()
                if otherImposter is None:
                    self.handOver()
                else:
                    nextPlayer = otherImposter
                    self.phase = "imposterRoll"
            else:
                self.phase = "draw"
            self.cycle_count += 1
        else:
            self.phase = "draw"
        self.player_turn = self.getActivePlayers()[nextPlayer].id

        if ["embargo", self.getActivePlayers()[nextPlayer].id] in self.activeShiftTokens:
            self.activeShiftTokens.remove(["embargo", self.getActivePlayers()[nextPlayer].id])
            self.playerTurnOver()

    def getLastDrawActions(self):
        # print(self.move_history)
        playerLastActions = {i.id: "none" for i in self.players}

        if self.move_history is not None:
            moveHistoryIndex = 0
            while moveHistoryIndex < len(self.move_history):
                currentDict = self.move_history[moveHistoryIndex]
                if "players" in currentDict:
                    for i in currentDict["players"]:
                        if i["lastAction"] == "stands" or i["lastAction"].startswith("draws"):
                            playerLastActions[i["id"]] = i["lastAction"]
                if "phase" in currentDict:
                    if currentDict["phase"] == "reveal":
                        for i in playerLastActions:
                            playerLastActions[i] = 'none'

                moveHistoryIndex += 1

            for i in self.players:
                if i.lastAction == "stands" or i.lastAction.startswith("draws"):
                    playerLastActions[i.id] = i.lastAction

        return playerLastActions

    def shiftTokenUse(self, player: KesselPlayer, shiftToken: str):
        if shiftToken == "freeDraw":
            self.activeShiftTokens.append(["freeDraw", str(player.id)])
            self.p_act = f'{player.username} used free draw shift token, thier next draw will be free.'
            player.lastAction = 'uses free draw'

        elif shiftToken == "refund":
            transferAmount = min(player.usedChips, 2)
            player.chips += transferAmount
            player.usedChips -= transferAmount
            self.p_act = f'{player.username} used refund shift token, they got refunded two chips'
            player.lastAction = 'uses refund'

        elif shiftToken == "extraRefund":
            transferAmount = min(player.usedChips, 3)
            player.chips += transferAmount
            player.usedChips -= transferAmount
            self.p_act = f'{player.username} used free extra refund shift token, they got refunded three chips.'
            player.lastAction = 'uses extra refund'

        elif shiftToken == "embezzlement":
            for i in self.getActivePlayers():
                if ["immunity", str(i.id)] in self.activeShiftTokens:
                    continue

                if i.chips >= 1:
                    i.chips -= 1
                    player.chips += 1

            self.p_act = f'{player.username} used embezzlement shift token, taking one chip from each players pots'
            player.lastAction = 'uses embezzlement'

        elif shiftToken == "majorFraud":
            fraudify = (lambda x: (6 if x.suit == "imposter" else x.val))
            for i in self.positiveDeck.cards:
                i.val = fraudify(i)

            for i in self.negativeDeck.cards:
                i.val = fraudify(i)

            for i in self.positiveDiscard:
                i.val = fraudify(i)

            for i in self.negativeDiscard:
                i.val = fraudify(i)

            for i in self.getActivePlayers():
                i.positiveCard.val = fraudify(i.positiveCard)
                i.negativeCard.val = fraudify(i.negativeCard)

                if i.extraCard is not None:
                        i.extraCard.val = fraudify(i.extraCard)

            self.p_act = f'{player.username} used major fraud shift token, all imposters now have a value of 6.'
            player.lastAction = 'uses major fraud'

        elif shiftToken == "generalTariff":
            for i in self.getActivePlayers():
                if ["immunity", str(i.id)] in self.activeShiftTokens:
                    continue

                if i.chips >= 1:
                    i.chips -= 1

            self.p_act = f'{player.username} used general tariff shift token, taxing each player 1 chip.'
            player.lastAction = 'uses general tariff'

        elif shiftToken == "targetTariff":
            self.activeShiftTokens.append(["targetTariff", self.phase])
            self.phase = "shiftTokenPlayer"

        elif shiftToken == "generalAudit":
            if self.cycle_count == 0:
                for i in self.getActivePlayers():
                    if ["immunity", str(i.id)] in self.activeShiftTokens:
                        continue

                    if (self.getPlayerDex(None, i.id) > self.getPlayerDex(None, player.id) and self.getLastDrawActions()[i.id] == "stands"):
                        i.chips -= min(i.chips, 2)
            else:
                for i in self.getActivePlayers():
                    if ["immunity", str(i.id)] in self.activeShiftTokens:
                        continue

                    if i.lastAction == "stands" and i != player:
                        i.chips -= min(i.chips, 2)

            self.p_act = f'{player.username} used general audit shift token, taxing every standing player 2 chips.'
            player.lastAction = 'uses general audit'

        elif shiftToken == "targetAudit":
            self.activeShiftTokens.append(["targetAudit", self.phase])
            self.phase = "shiftTokenPlayer"

        elif shiftToken == "immunity":
            self.activeShiftTokens.append(["immunity", str(player.id)])
            self.p_act = f'{player.username} used immunity shift token, they are immune to other players shift token attacks.'
            player.lastAction = 'uses immunity'

        elif shiftToken == "exhaustion":
            self.activeShiftTokens.append(["exhaustion", self.phase])
            self.phase = "shiftTokenPlayer"

        elif shiftToken == "directTransaction":
            if self.phase == "discard":
                return "you cannot use directTransaction during discard phase"
            self.activeShiftTokens.append(["directTransaction", self.phase])
            self.phase = "shiftTokenPlayer"

        elif shiftToken == "embargo":
            targetPlayer = self.getNextPlayer(player)
            if not (["immunity", str(targetPlayer.id)] in self.activeShiftTokens):
                self.activeShiftTokens.append(["embargo", str(targetPlayer.id)])

            self.p_act = f'{player.username} used embargo shift token, forcing {targetPlayer.username} to stand.'
            player.lastAction = 'uses embargo'

        elif shiftToken == "markdown":
            self.activeShiftTokens.append(["markdown", ""])

            self.p_act = f'{player.username} used markdown shift token, now all sylops have a value of 0 (as opposed to matching the other card).'
            player.lastAction = 'uses markdown'

        elif shiftToken == "cookTheBooks":
            self.activeShiftTokens.append(["cookTheBooks", ""])

            self.p_act = f'{player.username} used cook the books shift token, now sabacc ranks are reversed (you want higher cards).'
            player.lastAction = 'uses cook the books'

        elif shiftToken == "primeSabacc":
            self.activeShiftTokens.append(["primeSabacc", self.phase])
            self.phase = "shiftTokenRoll"

        player.shiftTokens.remove(shiftToken)

    def action(self, params: dict, db):
        originalSelf = copy.deepcopy(self)

        player: KesselPlayer = self.getPlayer(username=params["username"])

        if (params["action"] == "shiftTokenSelect") and (self.player_turn == player.id) and (self.phase == "shiftTokenSelect") and (self.completed == False):
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

            self.p_act = f'{player.username} chooses new shift token: {KesselGame.camelToNatural(params["shiftToken"])}'
            player.lastAction = f'chooses shift token {params["shiftToken"]}'

        elif (params["action"] == "shiftTokenUse") and (self.player_turn == player.id) and (self.phase in ("draw", "discard")) and (self.completed == False):
            self.shiftTokenUse(player, params["shiftToken"])

        elif (params["action"] == "shiftTokenDetail") and (self.player_turn == player.id) and (self.phase in ("shiftTokenPlayer", "shiftTokenRoll", "shiftTokenDieChoice")) and (self.completed == False):
            for i, j in enumerate(self.activeShiftTokens):
                if j[1] in ("draw", "discard"):
                    shiftToken = j[0]
                    shiftTokenInd = i

            if self.phase == "shiftTokenPlayer":
                targetPlayer: KesselPlayer = self.getPlayer(None, params["player"])
                if targetPlayer == player:
                    return "you cannot target yourself"

                if ["immunity", str(targetPlayer.id)] in self.activeShiftTokens:
                    return "you cannot target this player, they are immune"

                if shiftToken == "targetTariff":
                    targetPlayer.chips -= min(targetPlayer.chips, 2)

                    self.p_act = f'{player.username} used target tariff shift token against {targetPlayer.username}, removing 2 tokens from their pot.'
                    player.lastAction = f'uses target tariff against {targetPlayer.username}'

                elif shiftToken == "targetAudit":
                    if self.cycle_count == 0:
                        if self.getPlayerDex(None, targetPlayer.id) >= self.getPlayerDex(None, player.id):
                            return "you cannot target this player, they havent moved yet"

                        elif self.getLastDrawActions()[targetPlayer.id] != "stands":
                            return "you cannot target this player, they didnt stand"

                        else:
                            targetPlayer.chips -= min(targetPlayer.chips, 3)

                    else:
                        if targetPlayer.lastAction != "stands":
                            return "you cannot target this player, they didnt stand"

                        else:
                            targetPlayer.chips -= min(targetPlayer.chips, 3)

                    self.p_act = f'{player.username} used target audit shift token against {targetPlayer.username}, taxing them 3 tokens because they are standing.'
                    player.lastAction = f'uses target audit against {targetPlayer.username}'

                elif shiftToken == "exhaustion":
                    self.positiveDiscard.append(targetPlayer.positiveCard)
                    self.negativeDiscard.append(targetPlayer.negativeCard)
                    targetPlayer.positiveCard = self.positiveDeck.draw()
                    targetPlayer.negativeCard = self.negativeDeck.draw()

                    self.p_act = f'{player.username} used exhaustion shift token against {targetPlayer.username}, forcing them to redraw both of their cards.'
                    player.lastAction = f'uses exhaustion against {targetPlayer.username}'

                elif shiftToken == "directTransaction":
                    temp = player.negativeCard
                    player.negativeCard = targetPlayer.negativeCard
                    targetPlayer.negativeCard = temp

                    temp = player.positiveCard
                    player.positiveCard = targetPlayer.positiveCard
                    targetPlayer.positiveCard = temp

                    self.p_act = f'{player.username} used direct transaction shift token against {targetPlayer.username}, trading their hands.'
                    player.lastAction = f'uses direct transaction against {targetPlayer.username}'

                self.phase = self.activeShiftTokens[shiftTokenInd][1]
                self.activeShiftTokens.pop(shiftTokenInd)

            elif self.phase == "shiftTokenRoll":
                self.rollDice()
                self.phase = "shiftTokenDieChoice"

            elif self.phase == "shiftTokenDieChoice":
                self.activeShiftTokens.append(["primeSabacc", str(self.dice[params["die"]])])

                self.p_act = f'{player.username} used prime sabacc shift token and rolled {self.dice[params["die"]]}. now {self.dice[params["die"]]} is the best hand value.'
                player.lastAction = f'uses prime sabacc rolling {self.dice[params["die"]]}'

                self.phase = self.activeShiftTokens[shiftTokenInd][1]
                self.activeShiftTokens.pop(shiftTokenInd)

        elif (params["action"] in ("positiveDeckDraw", "negativeDeckDraw", "positiveDiscardDraw", "negativeDiscardDraw", "stand")) and (self.player_turn == player.id) and (self.phase == "draw") and (self.completed == False):
            if player.extraCard is not None:
                return "player already has extra card"

            if params["action"] == "stand":
                self.p_act = f'{player.username} stands'
                player.lastAction = "stands"

                everyoneStands = True
                lastDrawActions = self.getLastDrawActions()
                print(lastDrawActions)
                for i in lastDrawActions:
                    print(i)
                    if self.getPlayer(None, i).outOfGame:
                        continue
                    if lastDrawActions[i] != "stands":
                        everyoneStands = False
                        break

                if everyoneStands:
                    self.handOver()
                else:
                    self.playerTurnOver(player)

            else:
                if not (["freeDraw", str(player.id)] in self.activeShiftTokens):
                    if player.chips == 0:
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

                naturalWordDict = {
                    "positiveDeckDraw":"positive deck",
                    "negativeDeckDraw":"negative deck",
                    "positiveDiscardDraw":"positive discard pile",
                    "negativeDiscardDraw":"negative discard pile"
                }
                self.p_act = f'{player.username} draws a card from the {naturalWordDict[params["action"]]}'
                player.lastAction = f'draws from {naturalWordDict[params["action"]]}'

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

            discardCardString = 'their original card' if params["keep"] else 'their new card'
            self.p_act = f'{player.username} discards {discardCardString}'
            player.lastAction = f'discards {discardCardString}'
            
            self.playerTurnOver(player)

        elif (params["action"] == "imposterRoll") and (self.player_turn == player.id) and (self.phase == "imposterRoll") and (self.completed == False):
            self.rollDice()
            self.phase = "imposterChoice"

        elif (params["action"] == "imposterChoice") and (self.player_turn == player.id) and (self.phase == "imposterChoice") and (self.completed == False):
            if player.negativeCard.suit == "imposter" and player.negativeCard.val == 0:
                player.negativeCard.val = self.dice[params["die"]]
            elif player.positiveCard.suit == "imposter" and player.positiveCard.val == 0:
                player.positiveCard.val = self.dice[params["die"]]

            otherImposter = self.unRolledImposters()

            self.p_act = f'{player.username} rolls for imposter and gets a {self.dice[params["die"]]}'
            player.lastAction = f'rolls {self.dice[params["die"]]} for imposter'

            if otherImposter is None:
                self.handOver()
            else:
                self.phase = "imposterRoll"
                nextPlayer = otherImposter
                self.player_turn = self.getActivePlayers()[nextPlayer].id

        elif (params["action"] == "nextHand") and (self.player_turn == player.id) and (self.phase == "reveal") and (self.completed == False):
            self.nextHand()

        elif (params["action"] == "playAgain") and (self.player_turn == player.id) and (self.phase == "reveal") and (self.completed):
            self.nextRound()

        dbList = [
            self.playersToDb(),
            self.phase,
            self.diceToDb(),
            self.positiveDeckToDb(),
            self.negativeDeckToDb(),
            self.discardPileToDict(self.positiveDiscard),
            self.discardPileToDict(self.negativeDiscard),
            self.activeShiftTokens,
            self.player_turn,
            self.p_act,
            self.cycle_count,
            self.completed,
            self.id
        ]

        db.execute("UPDATE kessel_games SET players = ?, phase = ?, dice = ?, positiveDeck = ?, negativeDeck = ?, positiveDiscard = ?, negativeDiscard = ?, activeShiftTokens = ?, player_turn = ?, p_act = ?, cycle_count = ?, completed = ? WHERE game_id = ?", dbList)

        originalChangedValues = self.compare(originalSelf)
        if originalChangedValues == {}:
            print("invalid user input")
            return "invalid user input"

        originalChangedValues["timestamp"] = datetime.now(timezone.utc).isoformat()
        if self.move_history:
            self.move_history.append(originalChangedValues)
        else:
            self.move_history = [originalChangedValues]

        db.execute("UPDATE kessel_games SET move_history = ? WHERE game_id = ?", [self.moveHistoryToDb(), self.id])

        return self
