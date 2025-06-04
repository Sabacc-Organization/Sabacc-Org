import sys
# sys.path.insert(0, '../')

from cs50 import SQL
from helpers import *
from dataHelpers import *
# from traditional.alderaanHelpers import *
import traditional.traditionalHelpers as sqlite_traditional
import corellian_spike.corellianHelpers as sqlite_corellian
import kessel.kesselHelpers as sqlite_kessel
from colorama import Fore
from datetime import datetime, timezone
import json
import sqlite3
import psycopg
from psycopg.types.composite import CompositeInfo, register_composite

from dbConversion.psql_helpers.psql_traditionalHelpers import *
from dbConversion.psql_helpers.psql_corellianHelpers import *
from dbConversion.psql_helpers.psql_kesselHelpers import *


# convert from psql to sqlite3
def convertPsqlToSqlite(sqlite_conn, psql_conn):

    psql_db = psql_conn.cursor()
    sqlite_db = sqlite_conn.cursor()

    # register Traditional custom types
    traditionalCardType = CompositeInfo.fetch(psql_conn, 'traditionalcard')
    traditionalPlayerType = CompositeInfo.fetch(psql_conn, 'traditionalplayer')
    register_composite(traditionalCardType, psql_db)
    register_composite(traditionalPlayerType, psql_db)

    print("Registered Traditional custom types")

    # register Corellian custom types
    corellianSpikeCardType = CompositeInfo.fetch(psql_conn, 'corellianspikecard')
    corellianSpikePlayerType = CompositeInfo.fetch(psql_conn, 'corellianspikeplayer')
    register_composite(corellianSpikeCardType, psql_db)
    register_composite(corellianSpikePlayerType, psql_db)

    print("Registered Corellian custom types")

    # register Kessel custom types
    kesselCardType = CompositeInfo.fetch(psql_conn, 'kesselcard')
    kesselPlayerType = CompositeInfo.fetch(psql_conn, 'kesselplayer')
    register_composite(kesselCardType, psql_db)
    register_composite(kesselPlayerType, psql_db)

    print("Registered Kessel custom types")

    psql_users = psql_db.execute("SELECT username, hash FROM users ORDER BY id ASC").fetchall()
    for user in psql_users:
        sqlite_db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", user)

    print("Users copied over")

    psql_traditionalGames = psql_db.execute("SELECT * FROM traditional_games ORDER BY game_id ASC").fetchall()
    psql_corellianSpikeGames = psql_db.execute("SELECT * FROM corellian_spike_games ORDER BY game_id ASC").fetchall()
    psql_kesselGames = psql_db.execute("SELECT * FROM kessel_games ORDER BY game_id ASC").fetchall()

    for game in psql_traditionalGames:
        dbGame = sqlite_traditional.TraditionalGame.fromDict(TraditionalGame.fromDb(game).toDict()).toDb(includeId=False)
        sqlite_db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

    for game in psql_corellianSpikeGames:
        dbGame = sqlite_corellian.CorellianSpikeGame.fromDict(CorellianSpikeGame.fromDb(game).toDict()).toDb(includeId=False)
        sqlite_db.execute("INSERT INTO corellian_spike_games (players, hand_pot, sabacc_pot, phase, deck, discard_pile, player_turn, p_act, cycle_count, shift, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

    for game in psql_kesselGames:
        dbGame = sqlite_kessel.KesselGame.fromDict(KesselGame.fromDb(game).toDict()).toDb(includeId=False)
        sqlite_db.execute("INSERT INTO kessel_games (players, phase, dice, deck, positivedeck, negativedeck, positivediscard, negativediscard, activeshifttokens, player_turn, p_act, cycle_count, shift, completed, settings, created_at, move_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", dbGame)

    print("Games copied over")

    sqlite_conn.commit()
    



    # print(getDictsForDB(psql_db)[0])


# function to clean up deck data from completed games
def cleanDeckData(sqlite3_db):
    games = sqlite3_db.execute("SELECT * FROM games WHERE completed = 1 AND phase = 'alderaan'")

    for game in games:

        deck = game["deck"]

        commaString = ""
        for l in deck:
            if l != "," and commaString != "":
                break
            
            elif l == ",":
                commaString += l

        if commaString != ",":

            deck = deck.replace(commaString, ";")
            deck = deck.replace(",", "")
            deck = deck.replace(";", ",")

            sqlite3_db.execute("UPDATE games SET deck = ? WHERE game_id = ?", deck, game["game_id"])

# copy over data from sqlite3 to postgresql db with only traditional (pre CS)
def convertSqliteToPsql(db, card_type, player_type):

    """ Verify PostgreSQL db is empty - VERY IMPORTANT """
    if len(db.execute("SELECT * FROM users").fetchall()) > 0 or len(db.execute("SELECT * FROM games").fetchall()) > 0:
        print(f"{Fore.RED}PostgreSQL database is not empty. THIS SCRIPT IS NOT MEANT FOR THIS! PLEASE REVIEW! RISK OF DATA LOSS!{Fore.WHITE}")
        exit(1)

    # connect to sqltie3 db
    sqlite3_db = SQL("sqlite:///sabacc.db")
    cleanDeckData(sqlite3_db)

    # add test users and games
    # sqlite3_db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', 'durin', 'the deathless')
    # sqlite3_db.execute('INSERT INTO games (player_ids, player_credits, player_bets, hand_pot, sabacc_pot, phase, player_hands, player_protecteds, player_turn, folded_players, folded_credits, p_act, cycle_count, shift, completed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', '4,1,3','900,5000,300','45,45,20',250,600,'shift','17,-17,0;0,2,3;3,3,3,11','0,0,1;1,1,1;1,0,0,0',1,'2','4000','thrawn folded :O',5,1,0)

    # copy over users
    # get users from sqlite3 db
    users = sqlite3_db.execute("SELECT * FROM users")
    # loop thru users & insert each into postgresql db

    usersIndexLimit = users[len(users) - 1]["id"]

    numUsersAdded = 0
    for i in range(1, usersIndexLimit + 1):
        if users[0]["id"] == i:
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", [users[0]["username"], users[0]["hash"]])
            users.pop(0)
            numUsersAdded += 1
        elif users[0]["id"] != i:
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", [str(i), "empty"])

    db.execute("DELETE FROM users WHERE HASH = %s", ["empty"])


    # Copying over games could have a mechanism for empty rows like the users portion, but it's not necessary
    # copy over games
    games = sqlite3_db.execute("SELECT * FROM games")
    numGamesCopied = 0
    # loop thru games
    for game in games:
        player_ids = [int(id) for id in game['player_ids'].split(',')]
        folded_ids = []
        if game["folded_players"]: # not None
            folded_ids = [int(id) for id in game['folded_players'].split(',')]
        player_ids.extend(folded_ids)
        player_credits = game['player_credits'].split(',')
        if game["folded_credits"]: # not None
            player_credits += game['folded_credits'].split(',')
        player_bets = game['player_bets'].split(',')
        player_hands = game['player_hands'].split(';')
        player_prots = game['player_protecteds'].split(';')
        
        # loop thru player_ids and create list of players
        players = []
        usedCards = []
        for i in range(len(player_ids)):
            # get id
            id = player_ids[i]
            # get username
            username = sqlite3_db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']

            bet = None
            newHand = []
            folded = False
            if id not in folded_ids:
                # convert hand
                oldHand = player_hands[i].split(',')
                prots = [prot == '1' for prot in player_prots[i].split(',')]
                newHand = []
                for j in range(len(oldHand)):
                    try:
                        card = TraditionalCard.randCardNotInList(val=int(oldHand[j]), protected=prots[j], unallowedCards=usedCards)
                        newHand.append(card)
                        usedCards.append(card)
                    except ValueError:
                        pass
                
                try:
                    bet = int(player_bets[i])
                except ValueError:
                    pass
            else:
                folded = True
            
            # add player to list
            player = TraditionalPlayer(id=id, username=username, credits=int(player_credits[i]), bet=bet, hand=newHand, folded=folded)
            players.append(player)
        
        # convert deck
        oldDeck = game['deck'].split(',')
        newDeck = []
        for val in oldDeck:
            try:
                card = TraditionalCard.randCardNotInList(val=int(val), unallowedCards=usedCards)
                newDeck.append(card)
                usedCards.append(card)
            except ValueError:
                pass

        # add game to db
        newGame = TraditionalGame(players=players, id=game['game_id'], deck=newDeck, player_turn=game['player_turn'], p_act=game['p_act'], hand_pot=game['hand_pot'], sabacc_pot=game['sabacc_pot'], phase=game['phase'], cycle_count=game['cycle_count'], shift=(game['shift'] == 1), completed=(game['completed'] == 1))
        if(len(db.execute("SELECT * FROM games WHERE game_id = %s", [newGame.id]).fetchall()) == 0):
            db.execute("INSERT INTO games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", newGame.toDb(card_type, player_type))
            numGamesCopied += 1

    # if numUsersAdded != 0 or numGamesCopied != 0:
    print(f"{numUsersAdded} users and {numGamesCopied} of {len(games)} games copied over from sqlite3 db to PostgreSQL db")


# copy over data from postgresql db with only traditional to db with traditional and CS
# only needs to modify the games table and game data
def transferTraditionalGames(db, traditional_card_type, traditional_player_type):
    allTraditionalGames = [TraditionalGame.fromDb(game) for game in db.execute("SELECT * FROM games").fetchall()]

    numGamesCopied = 0

    for game in allTraditionalGames:
        db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", game.toDb(traditional_card_type, traditional_player_type))
        numGamesCopied += 1

    print(f"{numGamesCopied} of {len(allTraditionalGames)} games copied over from games to traditional_games")
    if numGamesCopied == len(allTraditionalGames):
        print("\nExecute the following Postgres commands to get rid of old data:")
        print("DROP TABLE games;")
        print("DROP TYPE Player;")
        print("DROP TYPE Card;")
        print("DROP TYPE Suit;")


defaultTraditionalSettings = { 
    "PokerStyleBetting": False, 
    "SmallBlind": 1, 
    "BigBlind": 2, 
    "HandPotAnte": 5, 
    "SabaccPotAnte": 10, 
    "StartingCredits": 1000 
}

defaultCorellianSpikeSettings = { 
    "PokerStyleBetting": False,
    "DeckDrawCost": 0,
    "DiscardDrawCost": 0,
    "DeckTradeCost": 0,
    "DiscardTradeCost": 0,
    "DiscardCosts": [0, 0, 0], 
    "SmallBlind": 1, 
    "BigBlind": 2, 
    "HandPotAnte": 5, 
    "SabaccPotAnte": 10, 
    "StartingCredits": 1000 
}

# Accounts for settings that are not in the original psql database and adds poker style betting
def convertPreSettingsToPostSettings(db, traditional_card_type, traditional_player_type, corellian_spike_card_type, corellian_spike_player_type):
    allTraditionalGames = [TraditionalGame.fromDb(game, preSettings=True) for game in db.execute("SELECT * FROM traditional_games ORDER BY game_id ASC;").fetchall()]
    db.execute("DROP TABLE traditional_games;")
    db.execute("CREATE TABLE IF NOT EXISTS traditional_games (game_id SERIAL PRIMARY KEY, players TraditionalPlayer[], hand_pot INTEGER NOT NULL DEFAULT 0, sabacc_pot INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'betting', deck TraditionalCard[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, shift BOOL NOT NULL DEFAULT false, completed BOOL NOT NULL DEFAULT false, settings JSONB NOT NULL DEFAULT '{ \"PokerStyleBetting\" : false, \"SmallBlind\" : 1, \"BigBlind\" : 2, \"HandPotAnte\": 5, \"SabaccPotAnte\": 10, \"StartingCredits\" : 1000 }', created_at TIMESTAMP DEFAULT NOW());")
    numTraditionalGamesCopied = 0

    for game in allTraditionalGames:
        db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed, settings, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", game.toDb(traditional_card_type, traditional_player_type) + [None])
        numTraditionalGamesCopied += 1

    allCorellianSpikeGames = [CorellianSpikeGame.fromDb(game, preSettings=True) for game in db.execute("SELECT * FROM corellian_spike_games ORDER BY game_id ASC").fetchall()]
    db.execute("DROP TABLE corellian_spike_games;")
    db.execute("CREATE TABLE IF NOT EXISTS corellian_spike_games (game_id SERIAL PRIMARY KEY, players CorellianSpikePlayer[], hand_pot INTEGER NOT NULL DEFAULT 0, sabacc_pot INTEGER NOT NULL DEFAULT 0, phase TEXT NOT NULL DEFAULT 'card', deck CorellianSpikeCard[], discard_pile CorellianSpikeCard[], player_turn INTEGER, p_act TEXT, cycle_count INTEGER NOT NULL DEFAULT 0, shift BOOL NOT NULL DEFAULT false, completed BOOL NOT NULL DEFAULT false, settings JSONB NOT NULL DEFAULT '{ \"PokerStyleBetting\" : false, \"SmallBlind\" : 1, \"BigBlind\" : 2, \"HandPotAnte\": 5, \"SabaccPotAnte\": 10, \"StartingCredits\": 1000, \"HandRanking\": \"Wayne\", \"DeckDrawCost\": 5, \"DiscardDrawCost\": 10, \"DeckTradeCost\": 10, \"DiscardTradeCost\": 15, \"DiscardCosts\": [15, 20, 25] }', created_at TIMESTAMP DEFAULT NOW());")
    numCorellianSpikeGamesCopied = 0

    for game in allCorellianSpikeGames:
        db.execute("INSERT INTO corellian_spike_games (players, hand_pot, sabacc_pot, phase, deck, discard_pile, player_turn, p_act, cycle_count, shift, completed, settings, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", game.toDb(corellian_spike_card_type, corellian_spike_player_type) + [None])
        numCorellianSpikeGamesCopied += 1

    print(f"Converted {numTraditionalGamesCopied} out of {len(allTraditionalGames)} Traditional Games")
    print(f"Converted {numCorellianSpikeGamesCopied} out of {len(allCorellianSpikeGames)} Corellian Spike Games")
    print(f"Converted {numTraditionalGamesCopied + numCorellianSpikeGamesCopied} out of {len(allTraditionalGames) + len(allCorellianSpikeGames)} Games")
    print(f"{Fore.GREEN}Done!{Fore.WHITE}")

# converting games tables created_at from TIMESTAMP to TIMESTAMPTZ
def convertDBToTimestamptz(db, alterTables=True):
    if alterTables:
        db.execute("ALTER TABLE traditional_games ALTER COLUMN created_at TYPE TIMESTAMPTZ;")
        db.execute("ALTER TABLE traditional_games ALTER COLUMN created_at SET DEFAULT NOW();")
        db.execute("ALTER TABLE corellian_spike_games ALTER COLUMN created_at TYPE TIMESTAMPTZ;")
        db.execute("ALTER TABLE corellian_spike_games ALTER COLUMN created_at SET DEFAULT NOW();")

    traditionalGames = [TraditionalGame.fromDb(game) for game in db.execute("SELECT * FROM traditional_games WHERE created_at IS NOT NULL;").fetchall()]

    for game in traditionalGames:
        db.execute("UPDATE traditional_games SET created_at = %s WHERE game_id = %s;", (datetime(game.created_at.year, game.created_at.month, game.created_at.day, game.created_at.hour, game.created_at.minute, game.created_at.second, game.created_at.microsecond, tzinfo=timezone.utc), game.id))

    corellianSpikeGames = [CorellianSpikeGame.fromDb(game) for game in db.execute("SELECT * FROM corellian_spike_games WHERE created_at IS NOT NULL;").fetchall()]

    for game in corellianSpikeGames:
        db.execute("UPDATE corellian_spike_games SET created_at = %s WHERE game_id = %s;", (datetime(game.created_at.year, game.created_at.month, game.created_at.day, game.created_at.hour, game.created_at.minute, game.created_at.second, game.created_at.microsecond, tzinfo=timezone.utc), game.id))