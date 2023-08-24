from cs50 import SQL

def getIndexGameData(user_id, db):
    
    # Query the database for all the games
    games = db.execute("SELECT * FROM games")
    newGames = games.copy()

    user_ids = []
    player_turns = []

    # Remove games that have been completed and that are not relevant to the player
    for game in games:
        if str(user_id) not in game["player_ids"].split(",") or game["completed"] == True:
            newGames.remove(game)

        else:
            user_ids.append(game["player_ids"].split(","))
            player_turns.append(db.execute("SELECT username FROM users WHERE id = ?", game["player_turn"])[0]["username"])


    # Get all the relevant usernames from the database
    usernames = []
    for set in user_ids:
        s = ""
        for user in set:
            s += str(db.execute("SELECT * FROM users WHERE id = ?", int(user))[0]["username"]) + ", "

        st = s.strip(", ")

        usernames.append(st)

    return {
        "games": newGames, 
        "usernames": usernames, 
        "gamesLen": len(newGames), 
        "player_turns": player_turns
    }