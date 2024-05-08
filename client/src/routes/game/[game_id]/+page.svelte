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
    let dark = Cookies.get("dark");
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
    let players: any[] = [];
    let orderedPlayers: any[] = [];
    let player_ids: any[] = [];
    let player_hands: any[] = [];
    let player_credits: any[] = [];
    let player_bets: any[] = [];
    let player_protecteds: any[] = [];

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
        socket.io.on('error', (err) => {console.log(err)});

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
        player_ids = [];
        player_hands = [];
        player_credits = [];
        player_bets = [];
        player_protecteds = [];

        game['players'].forEach(element => {
            if (serverInfo["users"].indexOf(element['username']) != -1){
                let cardsvals: number[] = [];
                let cardsprots: number[] = [];

                element['hand'].forEach(card => {
                    cardsvals.push(card['val']);
                    cardsprots.push(card['prot'])
                });
                player_hands.push(cardsvals);
                player_protecteds.push(cardsprots);

                player_ids.push(element['id']);
                player_credits.push(element['credits']);
                player_bets.push(element['bet']);
            }
        });

        // Set u_dex
        u_dex = player_ids.indexOf(user_id);

        //sets players, and sets orderedPlayers to the correct length in case of a fold.
        players = [... serverInfo["users"]];
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
        updateClientGame(serverInfo)
    }

    // protect doesnt request any data, it just sends it. when the server recieves it, it updates the game, and sends the new info to every client through updateClientGame
    // this applies to bet, card, shift, and playAgain.
    function protect(id: string) {
        let protectCardDex = player_hands[u_dex].indexOf(parseInt(document.getElementById(id)?.innerText));
        let protCard = {
            'val': 0,
            'suit': 'blah',
            'prot': false
        };

        game['players'].forEach((player) => {
            if (player['id'] === user_id){
                protCard = player['hand'][protectCardDex];
            }
        });
        console.log(protCard);

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
            if ((isNaN(betCreds) || betCreds < 0 || betCreds > player_credits[u_dex]) && action != "fold") {
                betErr = "Please input a number of credits you would like to bet(an integer 0 to " + player_credits[u_dex] + ")";
            } else {

                let tempCreds = betCreds;
                if (raising && !isNaN(player_bets[u_dex])) {
                    tempCreds = betCreds - player_bets[u_dex];
                }

                let clientInfo = {
                    "username": username,
                    "password": password,
                    "game_id": game_id,
                    "action": action,
                    "amount": tempCreds
                }
                console.log(clientInfo)
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
            if (u_dex === 0 && player_bets[u_dex + 1] === null){
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

            for (let i = 0; i < player_bets.length; i++) {
                if (player_bets[i] != null) {
                    if (player_bets[i] > raiseAmount) {
                        raiseAmount = player_bets[i];
                    }
                }
            }
            followAmount = raiseAmount - player_bets[u_dex];
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
        if (betCreds > raiseAmount && betCreds <= player_credits[u_dex]) {
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
        'suit': null,
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

    function trade(c: string) {
        if (tradeOpen) {
            let tradeCardDex = player_hands[u_dex].indexOf(parseInt(document.getElementById(c)?.innerText));
            game['players'].forEach((player) => {
                if (player['id'] === user_id){
                    tradeCard = player['hand'][tradeCardDex];
                }
            });
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
    <h1>{header}</h1>
    <h2>{game["phase"]} phase</h2>

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
            <div on:click={draw} class:active={cardBool} id="deck" class="card child"></div>

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

            {#if game["completed"] == 1 && game["player_turn"] === user_id}
                <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
            {/if}

        </div>

        {#each players as p, i}
            <div id="{p}Stuff" class="parent player{orderedPlayers.indexOf(p)}">

                <!-- Bet boxes -->
                {#if p === username}
                    <div id="{p}BetBox" class="backBlue {game["player_turn"] == player_ids[i]? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div><span id="betSpan">{player_bets[i]===null? '':player_bets[i]}</span></h5> <div id="{p}BetPile"></div></div>
                {:else}
                    <div id="{p}BetBox" class="backRed {game["player_turn"] == player_ids[i]? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div>{player_bets[i]===null? '':player_bets[i]}</h5></div>
                {/if}

                <!-- Cards -->
                <div class="cardContainer">
                    {#each player_hands[i] as c, ci}

                        {#if p === username}
                            {#if !player_protecteds[i][ci]}
                                <!-- svelte-ignore a11y-click-events-have-key-events -->
                                <!-- svelte-ignore a11y-no-static-element-interactions -->
                                <div on:click={() => trade("card" + ci.toString())} on:dblclick={() => protect("card" + ci.toString())} id="card{ci.toString()}" class="card child own"><h5>{c}</h5></div>
                            {:else}
                                <!-- svelte-ignore a11y-click-events-have-key-events -->
                                <!-- svelte-ignore a11y-no-static-element-interactions -->
                                <div on:click={() => trade("card" + ci.toString())} id="card{ci.toString()}" class="card child own protected"><h5>{c}</h5></div>
                            {/if}
                        {:else}
                            {#if game["completed"] == 0}
                                {#if !player_protecteds[i][ci]}
                                    <div class="card child"></div>
                                {:else}
                                    <div class="card child protected"><h5>{c}</h5></div>
                                {/if}
                            {:else if game["completed"] == 1}
                                <div class="card child"><h5>{c}</h5></div>
                            {/if}
                        {/if}
                    {/each}
                </div>

                <!-- Player boxes -->
                {#if p === username}
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div id="{p}Box" class="backBlue {game["player_turn"] == player_ids[i]? "turnGlow" : "noTurnGlow"} playerBox">
                        <h5>{p}</h5> 
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
                        <h5><div class="imperial-credits-logo"></div><span id="credits">{player_credits[i]}</span></h5>
                    </div>
                {:else}
                    <div id="{p}Box" class="backRed {game["player_turn"] == player_ids[i]? "turnGlow" : "noTurnGlow"} playerBox"> <h5>{p}</h5> <div class="parent"> <div class="chip bigChip child"></div> <div class="chip midChip child"></div> <div class="chip lowChip child"></div> </div> <h5><div class="imperial-credits-logo"></div><span id="{p}_credits">{player_credits[i]}</span></h5></div>
                {/if}

            </div>

        {/each}

        <div id="actBox">

            {#if !game["completed"]}
                {#if game["player_turn"] === user_id}
                    {#if game["phase"] === "betting"}
                        {#if u_dex === 0}
                            {#if player_bets[u_dex + 1] === null}
                                <div id="betDiv" class="backBlue brightBlue"> 
                                    <input bind:value={betCreds} id="betCredits" type="number" class="form-control form-group" min="0" max={player_credits[u_dex]} placeholder="Credits" required> 
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
                                        <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={player_credits[u_dex]} placeholder="Credits" required> 
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
                                    <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={player_credits[u_dex]} placeholder="Credits" required> 
                                    <button on:click={() => {raise(); chipInput=false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button> 
                                    <p class="red">{betErr}</p>
                                </div>
                            {/if}

                        {/if}
                    {/if}

                {/if}
            {/if}

        </div>
    </div>
    {#if theme == 'modern'}
        <div class="credit-attribution">
            <a href="http://creativecommons.org/licenses/by-sa/4.0/"><div id="jacob-densford-credit-attribution"></div></a>
            <a href="http://creativecommons.org/licenses/by-sa/4.0/">Credit to Jacob Densford for table and betting chip design</a>
        </div>
    {/if}
{/if}


<style>
    .shift1 {
        background-color: #0cc23c;
    }
</style>