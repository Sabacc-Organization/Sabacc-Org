import { get } from 'svelte/store';
import {
    socket,
    username,
    game_id,
    game_variant,
    backupServerInfo,
    currentMove,
    game,
    movesDone,
    user_id,
    turnSound,
    dataToRender,
    activePlayers,
    u_dex,
    thisPlayer,
    orderedPlayers,
    header,
    isWaitingOnClick,
    password,
    betCreds,
    potsActive,
    betErr,
    raising,
    chipInput,
    followAmount,
    raiseAmount,
    cardBool,
    tradeCard,
    tradeType,
    alderaanActive,
    shiftActive,
    greatestBet,
} from './sharedValues';

export function requestGameUpdate() {
    // client info to send to server so it knows who its sending this info back to.
    let clientInfo = {};

    // If logged in user
    clientInfo = {
        "username": get(username) != undefined? get(username):"",
        "game_id": get(game_id) != undefined? get(game_id):"invalid :(",
        "game_variant": get(game_variant)
    }

    // Send info
    get(socket)!.emit('getGame', clientInfo);
}

export function updateClientGame(serverInfo: any) {

    backupServerInfo.set(serverInfo);

    currentMove.set(null);

    // Set game data
    for (let key in serverInfo['gata']){
        game.update((value) => {
            value[key] = serverInfo['gata'][key];
            return value;
        });
    }

    if (get(game)["move_history"] !== undefined && get(game)["move_history"] !== null) {
        movesDone.set(get(game)["move_history"].length);
    }

    updateGame(serverInfo)

    if (get(game)["player_turn"] === get(user_id)) {
        get(turnSound)!.play();
    }
    dataToRender.set(true);
}

export function updateGame(info:any) {
    // sets all player specific elements, such as hands and whatnot

    let players: {[id: string]: any}[] = get(game)["players"];
    activePlayers.set([]);

    greatestBet.set(0);
    players.forEach((element : any) => {
        //sets u_dex
        if (get(user_id) === element['id']) {
            u_dex.set(players.indexOf(element));
            thisPlayer.set(element);
        }
        if (!element['folded']) {
            activePlayers.update((value) => [...value, element]);
        }
        if (element['bet'] > get(greatestBet)) {
            greatestBet.set(element['bet']);
        }
    });

    //sets players, and sets orderedPlayers to the correct length in case of a fold.
    orderedPlayers.set([... players]);

    // If player is in game, make orderedPlayers proper
    if (get(u_dex) != -1) {
        for (let i = 0; i < players.length; i++) {
            orderedPlayers.update((value) => {
                value[i] = players[(i + get(u_dex)) % players.length];
                return value
            });
        }
    }

    // Creat p(layer)s array
    let ps: any[] = [];

    // Prepare header var (p vs. p vs. p)
    header.set("");

    // For every user in users
    for (let i = 0; i < players.length; i++) {
        // Add vs. except on first loop through
        if (i != 0) {
            header.update((value) => value + " vs. ");
        }

        // Update player array
        ps[i] = players[i]["username"];

        // Add username to header
        header.update((value) => value + players[i]["username"]);
    }
}

export function updateClientInfo(serverInfo: any){
    if (get(username) === serverInfo["username"]) {
        // Set user ID
        user_id.set(serverInfo["user_id"]);
    }
    updateClientGame(serverInfo);
}

export function clickOrDblclick(clickFunction: () => void, dblclickFunction: () => void, delay: number = 500) {
    if (get(isWaitingOnClick) === true){
        isWaitingOnClick.set(false);
        dblclickFunction();
    } else {
        isWaitingOnClick.set(true);
        setTimeout(() => {
            if (get(isWaitingOnClick) === true){
                isWaitingOnClick.set(false);
                clickFunction()
            }
        }, delay);
    }
}

export function numOfActivePlayers() {
    let players = get(game)["players"];
    let num = 0;
    for (let i = 0; i < players.length; i++) {
        if (!players[i]['folded']) {
            num++;
        }
    }
    return num;
}

export function bet(action: string) {
    let players = get(game)["players"];
    if (get(potsActive) === true) {
        if ((isNaN(get(betCreds)!) || get(betCreds)! < 0 || get(betCreds)! > players[get(u_dex)]['credits']) && action != "fold") {
            betErr.set("Please input a number of credits you would like to bet(an integer 0 to " + players[get(u_dex)]['credits'] + ")");
        } else {

            let clientInfo = {
                "username": get(username),
                "password": get(password),
                "game_id": get(game_id),
                "game_variant": get(game_variant),
                "action": action,
                "amount": get(betCreds)
            }
            get(socket)!.emit('gameAction', clientInfo);
        }
        raising.set(false);
        betCreds.set(0);
    }
}

export function check() {
    betCreds.set(0);
    bet("check");
}

export function handleChipPress(chipValue: number){
    if (get(chipInput) === true){
        betCreds.update((value) => value! + chipValue);
    }
}

export function call() {
    betCreds.set(get(followAmount));
    bet("call");
}

export function raise() {
    if (get(betCreds)! > get(raiseAmount) && get(betCreds)! <= get(game)["players"][get(u_dex)]['credits']) {
        bet("raise");
    }
    else {
        betErr.set("Invalid amount of credits");
    }
}

export function fold() {
    bet("fold");
}

// card phase
export function kesselDiscard(keep: boolean){
    let clientInfo = {
        "username": get(username),
        "password": get(password),
        "game_id": get(game_id),
        "game_variant": get(game_variant),
        "action": "discard",
        "keep": keep
    }

    get(socket)!.emit('gameAction', clientInfo);
}

export function card(action: string) {
    console.log('ewehwherhewhwiiii')
    if (get(cardBool) === true) {

        let clientInfo = {
            "username": get(username),
            "password": get(password),
            "game_id": get(game_id),
            "game_variant": get(game_variant),
            "action": action,
            "trade": get(tradeCard)
        }

        get(socket)!.emit('gameAction', clientInfo);
        tradeType.set('none');
    }
}

export function draw(type: string) {
    if (get(game_variant) !== 'traditional') {
        card(type);
    } else {
        card("draw");
    }
}

export function tradeBtn(type: string) {
    tradeType.set(type);
}

export function trade(traCard: {'val':number, 'suit':string, 'prot':boolean}) {
    tradeCard.set(traCard);
    if (get(tradeType) === 'traditional') {
        card("trade");
    } else {
        card(get(tradeType));
    }
}

export function stand() {
    card("stand");
}

export function alderaan() {
    if (get(alderaanActive) === true) {
        card("alderaan");
    }
}

export function shift() {
    if (get(shiftActive) === true) {

        let clientInfo = {
            "username": get(username),
            "password": get(password),
            "game_id": get(game_id),
            "game_variant": get(game_variant),
            "action": "shift"
        }

        get(socket)!.emit('gameAction', clientInfo);
    }
}

export function imposterRoll() {
    if (get(game)["phase"] === "imposterRoll" && get(game)["player_turn"] === get(user_id)) {

        let clientInfo = {
            "username": get(username),
            "password": get(password),
            "game_id": get(game_id),
            "game_variant": get(game_variant),
            "action": "imposterRoll"
        }

        get(socket)!.emit('gameAction', clientInfo);
    }
}

export function imposterChoice(index: number) {
    if (get(game)["phase"] === "imposterChoice" && get(game)["player_turn"] === get(user_id)) {

        let clientInfo = {
            "username": get(username),
            "password": get(password),
            "game_id": get(game_id),
            "game_variant": get(game_variant),
            "action": "imposterChoice",
            "die": index
        }

        get(socket)!.emit('gameAction', clientInfo);
    }
}

export function shiftTokenSelect(shiftToken: string){
    if (get(shiftActive) === true) {

        let clientInfo = {
            "username": get(username),
            "password": get(password),
            "game_id": get(game_id),
            "game_variant": get(game_variant),
            "shiftToken": shiftToken,
            "action": "shiftTokenSelect"
        }

        get(socket)!.emit('gameAction', clientInfo);
    }
}

export function playAgain() {
    let clientInfo = {
        "username": get(username),
        "password": get(password),
        "game_id": get(game_id),
        "game_variant": get(game_variant),
        "action": "playAgain"
    }

    get(socket)!.emit('gameAction', clientInfo);
}

export function playback(index: number) {
    if (get(game)["move_history"] === null || get(game)["move_history"] === undefined) {
        return;
    }
    if (index >= get(game)["move_history"].length || index < -1) {
        return;
    }
    game.set(JSON.parse(JSON.stringify(get(backupServerInfo)!["gata"])));
    for (let i = get(game)["move_history"].length - 1; i > index; i--) {
        for (const [key, value] of Object.entries(get(game)["move_history"][i])) {
            game.update((game) => {
                game[key] = value;
                return game
            });
        }
    }
    currentMove.set(index);

    updateGame(backupServerInfo);
}

export function playback_back() {
    if (get(game)["move_history"] === null || get(game)["move_history"] === undefined) {
        return;
    }

    if (get(currentMove) === -1) {
        return;
    }

    for (const [key, value] of Object.entries(get(game)["move_history"][get(currentMove)!])) {
        if (key != "timestamp") {
            game.update((game) => {
                game[key] = value;
                return game;
            });
        }
    }
    currentMove.update((value) => value!-1);

    updateGame(backupServerInfo);
}

export function playback_forward() {
    playback(get(currentMove)! + 1);
}