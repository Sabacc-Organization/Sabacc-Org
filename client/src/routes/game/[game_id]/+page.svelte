<script lang="ts">
    import { page } from '$app/stores';
    import { checkLogin, customRedirect } from '$lib';
    import Cookies from 'js-cookie';
    import { onDestroy, onMount } from 'svelte';
    import { io } from 'socket.io-client';

    // URLs for Requests and Redirects
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    // Cookie info
    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let loggedIn = false;
    let dark = (Cookies.get("dark") == "true");
    let cardDesign = (Cookies.get("cardDesign"));
    let theme = Cookies.get("theme");

    // dont render the page until dataToRender is true
    let dataToRender = false;

    //socket.io
    let socket: any;

    // Page header (plaer vs. player vs. player)
    let header = "";

    // Error message for invalid inputs
    let errorMsg = "";

    // Accessing the 'username' parameter from the URL
    $: game_id = $page.params.game_id;

    // Game information
    let game: {[id: string]: any} = {
        "p_act": "",
        "players": [],
        "hand_pot": 0,
        "sabacc_pot": 0,
        "phase": "",
        "shift": 0,
        "player_turn": -1,
        "completed": 0,
        "cycle_count": 0
    };

    let players: any[] = []
    let orderedPlayers: any[] = []

    // User ID
    let user_id = -1;

    // Index of user in list of users
    let u_dex = -1;

    // Game data refresh interval
    let refreshInterval: NodeJS.Timeout;

    let turnSound: HTMLAudioElement;

    // Clean up request cycle
    onDestroy(() => {
        clearInterval(refreshInterval);

    });

    // Once page is mounted
    onMount(() => {
        // defines a new socket object for real-time communication with server
        socket = io(BACKEND_URL);

        // code to catch errors
        socket.io.on('error', (err: any) => {console.log(err)});

        // when there is a connection established with the server, it will explicitely ask the server for a game update. 
        // this is the only time it will explicitly ask for a game update.
        socket.on('connect', () => {
            requestGameUpdate();
        });

        // when the server responds to a game update request or recieves new information, it will pass that info on to updateClientGame as serverInfo
        socket.on('gameUpdate', (serverInfo: any) => {
            updateClientGame(serverInfo);
        });

        // sometimes the server wants to give the client information that only applies to them, such as their user ID.
        // clientUpdate is accessed when the server doesnt want to give that info to every client. it also give the updated game in serverInfo
        // updateClientGame is called within updateClientInfo. updateClientInfo is only called when first logging on.
        socket.on('clientUpdate', (serverInfo: any) => {
            updateClientInfo(serverInfo);
        });

        // defining the Audio to be play apon your turn (it wouldnt work if i put it outside of onMount)
        turnSound = new Audio("/move-sound.mp3");
    });

    let soundPlayed = false;

    // sends a message from to the server to fetch new game data, useful when first logging on.
    function requestGameUpdate() {
        // client info to send to server so it knows who its sending this info back to.
        let clientInfo = {};

        // If logged in user
            clientInfo = {
                "username": username != undefined? username:"",
                "game_id": game_id != undefined? game_id:"invalid :("
            }

        // Send info
        socket.emit('getGame', clientInfo);
    }

    // automatically called when server sends update
    function updateClientGame(serverInfo: any) {

        // Set game data
        for (let key in serverInfo['gata']){
            game[key] = serverInfo['gata'][key]
        }

        // sets all player specific elements, such as hands and whatnot
        players = [];

        game['players'].forEach((element : any) => {
            if (serverInfo["users"].indexOf(element['username']) != -1){
                players.push(element);

                //sets u_dex
                if (user_id === element['id']) {
                    u_dex = players.indexOf(element);
                }
            }
        });

        //sets players, and sets orderedPlayers to the correct length in case of a fold.
        orderedPlayers = [... players];

        // If player is in game, make orderedPlayers proper
        if (u_dex != -1) {
            for (let i = 0; i < players.length; i++) {
                orderedPlayers[i] = players[(i + u_dex) % players.length];
            }
        }

        // Creat p(layer)s array
        let ps: any[] = [];

        // Prepare header var (p vs. p vs. p)
        header = "";

        // For every user in users
        for (let i = 0; i < serverInfo["users"].length; i++) {
            // Add vs. except on first loop through
            if (i != 0) {
                header += " vs. "
            }

            // Update player array
            ps[i] = serverInfo["users"][i];

            // Add username to header
            header += serverInfo["users"][i];
        }

        if (game["player_turn"] === user_id) {
            if (!soundPlayed) {
                turnSound.play();
                soundPlayed = true;
            }
        } else {
            soundPlayed = false;
        }
        dataToRender = true;
    }

    // this is only called as a consequence of requestGameUpdate, and accesses data that should only be updated by one client, such as user_id
    // calls updateClientGame within it to update the game as well. this is only called when a player opens the game, hence the updateClientGame
    function updateClientInfo(serverInfo: any){
        if (username === serverInfo["username"]) {
            // Set user ID
            user_id = serverInfo["user_id"];
        }
        updateClientGame(serverInfo);
    }

    function renderCard(cardValue: {'suit': string, 'val':number, 'prot':boolean}){
        let returnText: string = "background-image:url(";

        let darkPath = "../../../../modern-theme-images/dark/"
        let lightPath = "../../../../modern-theme-images/light/"
        let pescadoPath = "../../../../modern-theme-images/pescado/"

        if (cardDesign === "classic"){
            returnText += "../../../../images/rebels-card-back.png);"
            return returnText
        }

        else if (cardDesign === "auto"){
            returnText += dark? darkPath:lightPath
        }

        else if (cardDesign === "dark"){
            returnText += darkPath
        }

        else if (cardDesign === "light"){
            returnText += lightPath
        }

        else if (cardDesign === "pescado"){
            returnText += pescadoPath
        }

        returnText += {"flasks":"b", "sabers":"r", "staves":"g", "coins":"y", "negative/neutral":"p"}[cardValue["suit"]];
        returnText += cardValue["val"].toString();
        returnText += ".png);";
        return returnText;
    }

    function renderBack(){
        if (cardDesign === "pescado"){
            return "background-image:url(../../../../modern-theme-images/pescado/back.png);"
        }
        return "background-image:url(../../../../images/rebels-card-back.png);"
    }

    // protect doesnt request any data, it just sends it. when the server recieves it, it updates the game, and sends the new info to every client through updateClientGame
    // this applies to bet, card, shift, and playAgain.
    function protect(protCard : {[id: string]: any}) {
        let clientInfo = {
            "username": username,
            "password": password,
            "game_id": game_id,
            "protect": protCard
        }

        socket.emit('protect', clientInfo)
    }

    // Betting Phase

    let betCreds: number;
    let betErr = "";

    let raising = false;

    function bet(action: string) {
        if (potsActive) {
            if ((isNaN(betCreds) || betCreds < 0 || betCreds > players[u_dex]['credits']) && action != "fold") {
                betErr = "Please input a number of credits you would like to bet(an integer 0 to " + players[u_dex]['credits'] + ")";
            } else {

                let tempCreds = betCreds;
                if (raising && !isNaN(players[u_dex]['bet'])) {
                    tempCreds = betCreds - players[u_dex]['bet'];
                }

                let clientInfo = {
                    "username": username,
                    "password": password,
                    "game_id": game_id,
                    "action": action,
                    "amount": tempCreds
                }
                socket.emit('bet', clientInfo);
            }
            raising = false;
            betCreds = 0;
        }
    }

    function check() {
        if (u_dex === 0) {
            betCreds = 0;
            bet("bet");
        }
    }

    $: {
        if (game["completed"] == 0 && game["player_turn"] === user_id && game["phase"] === "betting"){
            if (u_dex === 0 && players[u_dex + 1]['bet'] === null){
                if (betCreds == null){
                    betCreds = 0;
                }
                chipInput = true;
            }
            if (raising && (betCreds <= raiseAmount || betCreds == null)){
                betCreds = raiseAmount+1;
            }
        }
    }

    let chipInput = false;
    function handleChipPress(chipValue: number){
        if (chipInput){
            betCreds += chipValue;
        }
    }

    let raiseAmount = 0;
    let followAmount = 0;

    let potsActive = false;
    $: {
        if (game["player_turn"] === user_id && game["phase"] === "betting") {
            potsActive = true;

            raiseAmount = 0;
            followAmount = 0;

            for (let i = 0; i < players.length; i++) {
                if (players[i]['bet'] != null) {
                    if (players[i]['bet'] > raiseAmount) {
                        raiseAmount = players[i]['bet'];
                    }
                }
            }
            followAmount = raiseAmount - players[u_dex]['bet'];
            if (isNaN(followAmount)) {
                followAmount = raiseAmount;
            }

        } else {
            potsActive = false;
        }
    }

    function call() {
        betCreds = followAmount;
        bet("call");
    }

    function raise() {
        if (betCreds > raiseAmount && betCreds <= players[u_dex]['credits']) {
            bet("raise");
        }
        else {
            betErr = "Invalid amount of credits";
        }
    }

    function fold() {
        bet("fold");
    }

    // Card Phase

    let cardBool = false;
    let alderaanActive = false;

    let tradeOpen = false;
    let tradeCard = {
        'val': 0,
        'suit': 'none',
        'prot': false
    };

    $: {
        if (game["player_turn"] === user_id) {

            if (game["phase"] === "card") {
                cardBool = true;
                if (game["cycle_count"] != 0) {
                    alderaanActive = true;
                }
            }

            if (game["phase"] === "alderaan") {
                cardBool = true;
                alderaanActive = false;
            }
        } else {
            cardBool = false;
            alderaanActive = false;
        }
    }

    function card(action: string) {
        if (cardBool) {

            let clientInfo = {
                "username": username,
                "password": password,
                "game_id": game_id,
                "action": action,
                "trade": tradeCard
            }

            socket.emit('card', clientInfo);
            tradeOpen = false;
        }
    }

    function draw() {
        card("draw");
    }

    function tradeBtn() {
        tradeOpen = true;
    }

    function trade(traCard: {'val':number, 'suit':string, 'prot':boolean}) {
        if (tradeOpen) {
            tradeCard = traCard;
            card("trade");
        }
    }

    function stand() {
        card("stand");
    }

    function alderaan() {
        if (alderaanActive) {
            card("alderaan");
        }
    }

    // Shift Phase
    let shiftActive = false;
    $: {
        if (game["phase"] === "shift" && user_id === game["player_turn"]) {
            shiftActive = true;
        }
        else {
            shiftActive = false;
        }
    }

    function shift() {
        if (shiftActive) {

            let clientInfo = {
                "username": username,
                "password": password,
                "game_id": game_id
            }

            socket.emit('shift', clientInfo);
        }
    }

    // Play Again
    function playAgain() {

        let clientInfo = {
            "username": username,
            "password": password,
            "game_id": game_id
        }

        socket.emit('cont', clientInfo);
    }

</script>

<svelte:head>
  <title>Sabacc: Game {game_id}</title>
</svelte:head>

{#if dataToRender}
    <h1 class="header">{header}</h1>
    <h2 class="header">{game["phase"]} phase</h2>

    <div id="tableCont">
        <div id="table"></div>
        <h2 id="pAction">{game["p_act"]}</h2>
        <div id="gameInfo" class="parent">

            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div on:dblclick={check} class:active={potsActive} id="pots" class="child {potsActive}">
                <h5>Sabacc: <span id="sabacc_pot">{game["sabacc_pot"]}</span></h5>
                <h5>Hand: <span id="hand_pot">{game["hand_pot"]}</span></h5>
            </div>

            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div on:click={draw} class:active={cardBool} id="deck" class="card child" style="{renderBack()}"></div>

            <div class:active={cardBool} id="discard" class="card child">
                {#if game["completed"] == 0}
                    {#if game["player_turn"] === user_id}
                        {#if game["phase"] === "card" || game["phase"] === "alderaan"}
                            <button on:click={tradeBtn} type="button" id="tradeBtn" class="btn btn-primary smol">Trade</button>
                            <br>
                            <button on:click={stand} type="button" id="standBtn" class="btn btn-primary smol">Stand</button>
                        {/if}
                    {/if}
                {/if}
            </div>

            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <span on:click={shift} class:shiftActive={shiftActive} class="dieContainer">
                <div id="dieOne" class="child die"></div>
                <div id="dieTwo" class="child die shift{game["shift"]}"></div>
            </span>

            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div on:click={alderaan} class:active={alderaanActive} id="alderaan" class="child alderaan {game["phase"]}Blown"></div>
        </div>

        {#each players as p, i}
            <div id="{p['username']}Stuff" class="parent player{orderedPlayers.indexOf(p)} playerStuff">

                <!-- Bet boxes -->
                {#if p['username'] === username}
                    <div id="{p['username']}BetBox" class="betBox backBlue {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div><span id="betSpan">{p['bet']===null? '':p['bet']}</span></h5> <div id="{p['username']}BetPile"></div></div>
                {:else}
                    <div id="{p['username']}BetBox" class="betBox backRed {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div>{p['bet']===null? '':p['bet']}</h5></div>
                {/if}

                <!-- Cards -->
                <div class="cardsContainer">
                    {#each players[i]["hand"] as c, ci}
                        <div class="cardContainer">
                            {#if p['username'] === username}
                                {#if !c['prot']}
                                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                                    <div
                                    on:click={() => trade(c)}
                                    on:dblclick={() => protect(c)}
                                    id="card{ci.toString()}"
                                    class="card child own"
                                    style="{renderCard(c)}">
                                    </div>
                                    <h5>{cardDesign === "pescado"? "":c['val']}</h5>
                                {:else}
                                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                                    <div
                                    on:click={() => trade(c)}
                                    id="card{ci.toString()}"
                                    class="card child own protected"
                                    style="{renderCard(c)}">
                                    </div>
                                    <h5 class="protected">{cardDesign === "pescado"? "":c['val']}</h5>
                                {/if}
                            {:else}
                                {#if game["completed"] == 0}
                                    {#if !c['prot']}
                                        <div class="card child" style="{renderBack()}"></div>
                                    {:else}
                                        <div class="card child protected" style="{renderCard(c)}"></div>
                                        <h5 class="protected">{cardDesign === "pescado"? "":c['val']}</h5>
                                    {/if}
                                {:else if game["completed"] == 1}
                                    <div class="card child" style="{renderCard(c)}"></div>
                                    <h5>{cardDesign === "pescado"? "":c['val']}</h5>
                                {/if}
                            {/if}
                        </div>
                    {/each}
                </div>

                <!-- Player boxes -->
                {#if p['username'] === username}
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div id="{p['username']}Box" class="backBlue {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox">
                        <h5>{p['username']}</h5> 
                        <div class="parent">
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div class="ownChip child chip bigChip" on:click={() => handleChipPress(10)}></div>
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div class="ownChip child chip midChip" on:click={() => handleChipPress(5)}></div>
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div class="ownChip child chip lowChip" on:click={() => handleChipPress(1)}></div> 
                        </div>
                        <h5><div class="imperial-credits-logo"></div><span id="credits">{p['credits']}</span></h5>
                    </div>
                {:else}
                    <div id="{p['username']}Box" class="backRed {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox"> <h5>{p['username']}</h5> <div class="parent"> <div class="chip bigChip child"></div> <div class="chip midChip child"></div> <div class="chip lowChip child"></div> </div> <h5><div class="imperial-credits-logo"></div><span id="{p['username']}_credits">{p['credits']}</span></h5></div>
                {/if}

            </div>

        {/each}

        <div id="actBox">

            {#if !game["completed"]}
                {#if game["player_turn"] === user_id}
                    {#if game["phase"] === "betting"}
                        {#if u_dex === 0}
                            {#if players[u_dex + 1]['bet'] === null}
                                <div id="betDiv" class="backBlue brightBlue">
                                    <input bind:value={betCreds} id="betCredits" type="number" class="form-control form-group" min="0" max={players[u_dex]['credits']} placeholder="Credits" required>
                                    <button on:click={() => {bet("bet"); chipInput=false}} id="betBtn" type="button" class="btn btn-primary">Bet</button>
                                    <p class="red">{betErr}</p>
                                </div>
                            {:else}
                                {#if raising === false}
                                    <div id="betDiv" class="backBlue brightBlue"> 
                                        <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                        <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                        <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                    </div>
                                {:else}
                                    <div id="betDiv" class="backBlue brightBlue">
                                        <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={players[u_dex]['credits']} placeholder="Credits" required>
                                        <button on:click={() => {raise(); chipInput = false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                        <p class="red">{betErr}</p>
                                    </div>
                                {/if}
                            {/if}

                        {:else}

                            {#if raising === false}
                                <div id="betDiv" class="backBlue brightBlue">
                                    <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                    <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                    <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                </div>
                            {:else}
                                <div id="betDiv" class="backBlue brightBlue">
                                    <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={players[u_dex]['credits']} placeholder="Credits" required>
                                    <button on:click={() => {raise(); chipInput=false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                    <p class="red">{betErr}</p>
                                </div>
                            {/if}

                        {/if}
                    {/if}

                {/if}
            {:else}
                <div id="betDiv" class="backBlue brightBlue">
                    <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
                </div>
            {/if}

        </div>
        <div class="mobileActBox"></div>
    </div>
    {#if theme == 'modern'}
        <div class="credit-attribution-container">
            <div class="credit-attribution">
                <a href="http://creativecommons.org/licenses/by-sa/4.0/"><div id="jacob-densford-credit-attribution"></div></a>
                <a href="http://creativecommons.org/licenses/by-sa/4.0/">Credit to Jacob Densford for table and betting chip design</a>
            </div>
        </div>
        <div class="mobileActSpacer"></div>
    {/if}
{/if}


<style>
    .shift1 {
        background-color: #0cc23c;
    }
</style>