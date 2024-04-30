from app import *
from traditional.traditionalHelpers import *

# copy over data from sqlite3
def convertDb(db, card_type, player_type):
    # connect to sqltie3 db
    sqlite3_db = SQL("sqlite:///sabacc.db")

    # add test users and games
    # sqlite3_db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', 'durin', 'the deathless')
    # sqlite3_db.execute('INSERT INTO games (player_ids, player_credits, player_bets, hand_pot, sabacc_pot, phase, player_hands, player_protecteds, player_turn, folded_players, folded_credits, p_act, cycle_count, shift, completed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', '4,1,3','900,5000,300','45,45,20',250,600,'shift','17,-17,0;0,2,3;3,3,3,11','0,0,1;1,1,1;1,0,0,0',1,'2','4000','thrawn folded :O',5,1,0)

    # copy over users
    # get users from sqlite3 db
    users = sqlite3_db.execute("SELECT * FROM users")
    # loop thru users & insert each into postgresql db
    numUsersAdded = 0
    for user in users:
        id = user['id']
        # check if user alr exists first
        if len(db.execute("SELECT * FROM users WHERE id = %s", [id]).fetchall()) == 0:
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", [user['username'], user['hash']])
            numUsersAdded += 1

    # copy over games
    games = sqlite3_db.execute("SELECT * FROM games")
    numGamesCopied = 0
    # loop thru games
    for game in games:
        player_ids = [int(id) for id in game['player_ids'].split(',')]
        folded_ids = [int(id) for id in game['folded_players'].split(',')]
        player_ids.extend(folded_ids)
        player_credits = game['player_credits'].split(',') + game['folded_credits'].split(',')
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
                    card = Card.randCardNotInList(val=int(oldHand[j]), protected=prots[j], unallowedCards=usedCards)
                    newHand.append(card)
                    usedCards.append(card)
                
                bet = int(player_bets[i])
            else:
                folded = True
            
            # add player to list
            player = Player(id=id, username=username, credits=int(player_credits[i]), bet=bet, hand=newHand, folded=folded)
            players.append(player)
        
        # convert deck
        oldDeck = game['deck'].split(',')
        newDeck = []
        for val in oldDeck:
            card = Card.randCardNotInList(val=int(val), unallowedCards=usedCards)
            newDeck.append(card)
            usedCards.append(card)

        # add game to db
        newGame = Game(players=players, id=game['game_id'], deck=newDeck, player_turn=game['player_turn'], p_act=game['p_act'], hand_pot=game['hand_pot'], sabacc_pot=game['sabacc_pot'], phase=game['phase'], cycle_count=game['cycle_count'], shift=(game['shift'] == 1), completed=(game['completed'] == 1))
        if(len(db.execute("SELECT * FROM games WHERE game_id = %s", [newGame.id]).fetchall()) == 0):
            db.execute("INSERT INTO games VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", newGame.toDb(card_type, player_type))
            numGamesCopied += 1

    # if numUsersAdded != 0 or numGamesCopied != 0:
    print(f"{numUsersAdded} of {len(users)} users and {numGamesCopied} of {len(games)} games copied over from sqlite3 db to postgresql db")
