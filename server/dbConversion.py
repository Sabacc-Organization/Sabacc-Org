from cs50 import SQL
from helpers import *
from dataHelpers import *
# from traditional.alderaanHelpers import *
from traditional.traditionalHelpers import *
from corellian_spike.corellianHelpers import *
from colorama import Fore


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
    allTraditionalGames = [TraditionalGame.fromDb(game) for game in db.execute("SELECT * FROM traditional_games").fetchall()]

    numGamesCopied = 0

    print("saf")
    print(allTraditionalGames[0])

    for game in allTraditionalGames:
        print(game.id)
        print(game.deck)
        db.execute("INSERT INTO traditional_games (players, hand_pot, sabacc_pot, phase, deck, player_turn, p_act, cycle_count, shift, completed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", game.toDb(traditional_card_type, traditional_player_type))
        numGamesCopied += 1

    print(f"{numGamesCopied} of {len(allTraditionalGames)} games copied over from games to traditional_games")
    if numGamesCopied == len(allTraditionalGames):
        print("\nExecute the following Postgres commands to get rid of old data:")
        print("DROP TABLE games;")
        print("DROP TYPE Player;")
        print("DROP TYPE Card;")
        print("DROP TYPE Suit;")