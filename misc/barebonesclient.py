import requests
import socketio
import threading

# SERVER_IP = (127, 0, 0, 1)
# SERVER_PORT = (5000)
SERVER_URL = "http://127.0.0.1:5000"

# None at first, populated whenever logged in
username = None
password = None
halt = False

def checkLogin():
    if username is not None and password is not None:
        return True
    return False

def register():
    print()
    usernameTemp = input("username: ")
    password1Temp = input("password: ")
    password2Temp = input("confirm password: ")

    res = requests.post(SERVER_URL + "/register", json = {"username": usernameTemp, "password": password1Temp, "confirmPassword": password2Temp})

    if res.ok is True:
        print("ok")
    else:
        print(res.text)

def login():
    print()
    usernameTemp = input("username: ")
    passwordTemp = input("password: ")

    res = requests.post(SERVER_URL + "/login", json = {"username": usernameTemp, "password": passwordTemp})

    if res.ok is True:
        global username
        global password
        username = usernameTemp
        password = passwordTemp
        print("ok")
    else:
        print(res.text)

def loggedOutOptions():
    print()
    print("Options:")
    print("1. Register")
    print("2. Log In")
    print("3. Exit")
    print()

    userChoice = input(">>")

    match userChoice:
        case "1":
            register()
        case "2":
            login()
        case "3":
            global halt
            halt = True

def renderTraditionalGame(data):
    gata = data["gata"]
    print()
    print(f"ID: {gata["id"]}")
    print(gata["p_act"])
    print()
    print(f"Phase: {gata["phase"]}")
    print(f"Hand Pot: {gata["hand_pot"]}")
    print(f"Sabacc Pot: {gata["sabacc_pot"]}")
    print(f"Cycle Count: {gata["cycle_count"]}")
    print(f"Shift: {gata["shift"]}")
    print(f"Settings: {gata["settings"]}")

    for i in gata["players"]:
        print()
        print(f"{"#*#*# " if i["id"] == gata["player_turn"] else ""}{i["username"]}:")
        print(f"    Last Action: {i["lastAction"]}")
        print(f"    ID: {i["id"]}")
        print(f"    Bet: {i["bet"]}")
        print(f"    Credits: {i["credits"]}")
        print(f"    Folded: {i["folded"]}")
        print(f"    Hand:")
        for j in i["hand"]:
            print(f"        {j["val"]} of {j["suit"]} ({"" if j["prot"] else "un"}protected)")
        print()

def joinGameById():
    print()
    variant = input("Variant: ")
    ID = int(input("ID: "))
    print()

    s = socketio.Client()
    s.connect(SERVER_URL)
    s.on("clientUpdate", renderTraditionalGame)
    s.emit("getGame", {"username": username, "password": password, "game_id": ID, "game_variant": variant})

    s.sleep(5)

    s.disconnect()

def loggedInOptions():
    print()
    print("Options:")
    print("1. Join Game By ID")
    print("2. View Games")
    print("3. Host Game")
    print("4. Log Out")
    print("5. Exit")

    userChoice = input(">>")

    match userChoice:
        case "1":
            joinGameById()
        case "5":
            global halt
            halt = True


print("Hello, world!")
print("Welcome to sabacc! (barebones client)")

while True:
    if halt is True:
        break

    if checkLogin() is True:
        loggedInOptions()
    else:
        loggedOutOptions()