<script lang="ts" context="module">
    import { page } from '$app/stores';
    import { onDestroy, onMount } from 'svelte';
    import { io } from 'socket.io-client';

    // URLs for Requests and Redirects
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    // /** @type {import('./$types').PageData} */
	// export let data;
    // let loggedIn = data.loggedIn;
    // let username = data.username;
    // let dark = data.dark;
    // let cardDesign = data.cardDesign;
    // let theme = data.theme;

    //socket.io
    let socket: any;

    export {BACKEND_URL, FRONTEND_URL, socket}
</script>

<script lang="ts">

    export let game_variant: string;
    export let username: string;
    export let password: string;
    export let dark: string;
    export let cardDesign: string;
    export let theme: string;

    $: game_id = $page.params.game_id;

    // dont render the page until dataToRender is true
    let dataToRender = false;


    // Page header (plaer vs. player vs. player)
    let header = "";

    // Error message for invalid inputs
    let errorMsg = "";

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

    let turnSound: HTMLAudioElement;

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
            "user_id": user_id != undefined? user_id:-1,
            "game_id": game_id != undefined? game_id:"invalid :(",
            "game_variant": game_variant
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
                header += " vs. ";
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

    let isWaitingOnClick: boolean = false;
    function clickOrDblclick(clickFunction: () => void, dblclickFunction: () => void, delay: number = 500) {
        if (isWaitingOnClick){
            isWaitingOnClick = false;
            dblclickFunction();
        } else {
            isWaitingOnClick = true;
            setTimeout(() => {
                if (isWaitingOnClick){
                    isWaitingOnClick = false;
                    clickFunction()
                }
            }, delay);
        }
    }

    //cards are handled differently on different versions, so I export them to let each version decide for itself what to do.
    export let renderCard;
    export let renderBack;

    export let onDBClickCard;

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
                    "game_variant": game_variant,
                    "action": action,
                    "amount": tempCreds
                }
                socket.emit('gameAction', clientInfo);
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

    let tradeType = 'none';

    let tradeCard = {}
    if (game_variant === "traditional"){
        tradeCard = {
            'val': 0,
            'suit': 'none',
            'prot': false
        };
    } else {
        tradeCard = {
            'val': 0,
            'suit': 'none',
        };
    }

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
                "game_variant": game_variant,
                "action": action,
                "trade": tradeCard
            }

            socket.emit('gameAction', clientInfo);
            tradeType = 'none';
        }
    }

    function draw(type: string) {
        if (game_variant === 'corellian_spike') {
            card(type);
        }
        card("draw");
    }

    function tradeBtn(type: string) {
        tradeType = type;
    }

    function trade(traCard: {'val':number, 'suit':string, 'prot':boolean}) {
        tradeCard = traCard;
        if (tradeType === 'traditional') {
            card("trade");
        } else {
            card(tradeType);
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
                "game_id": game_id,
                "game_variant": game_variant,
                "action": "shift"
            }

            socket.emit('gameAction', clientInfo);
        }
    }

    // Play Again
    function playAgain() {

        let clientInfo = {
            "username": username,
            "password": password,
            "game_id": game_id,
            "game_variant": game_variant,
            "action": "playAgain"
        }

        socket.emit('gameAction', clientInfo);
    }

    onDestroy(() => {
        if (socket) {
            socket.disconnect();
            console.log('Socket disconnected');
        }
    });

</script>

<svelte:head>
  <title>Sabacc: Game {game_id}</title>
</svelte:head>

{#if dataToRender}
    <h1 class="header">{header}</h1>
    <h2 class="header">round {game["cycle_count"] + 1} during {game["phase"]} phase</h2>

    <div id="tableCont">
        <div id="table"></div>
        <h2 id="pAction" class:playing={u_dex != -1}>{game["p_act"]}</h2>
        <div id="gameInfo" class="parent" class:playing={u_dex != -1}>

            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div on:dblclick={check} class:active={potsActive} id="pots" class="child {potsActive}">
                <h5>Sabacc: <span id="sabacc_pot">{game["sabacc_pot"]}</span></h5>
                <h5>Hand: <span id="hand_pot">{game["hand_pot"]}</span></h5>
            </div>

            <div class="cardsContainer">
                <div class="cardContainer">
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div on:click={() => draw('deckDraw')} class:active={cardBool} id="deck" class="card child" style="{renderBack(cardDesign)}"></div>
                </div>

                {#if game_variant === "corellian_spike"}
                    <div class="cardContainer">
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                        <div on:click={() => draw('discardDraw')} class:active={cardBool} id="discard" class="card child" style={renderCard(game['discard_pile'][game['discard_pile'].length - 1])}></div>
                        <h5>{cardDesign === "pescado"? "":game['discard_pile'][game['discard_pile'].length - 1]['val']}</h5>
                    </div>
                {/if}
            </div>

            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <span on:click={shift} class:shiftActive={shiftActive} class="dieContainer">
                <div id="dieOne" class="child die"></div>
                <div id="dieTwo" class="child die shift{game["shift"]}"></div>
            </span>

            {#if game_variant === 'traditional'}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <!-- svelte-ignore a11y-no-static-element-interactions -->
                <div on:click={alderaan} class:active={alderaanActive} id="alderaan" class="child alderaan {game["phase"]}Blown"></div>
            {/if}
        </div>

        {#each players as p, i}
            <div id="{p['username']}Stuff" class="parent player{orderedPlayers.indexOf(p)} playerStuff" class:playing={p['username'] === username}>

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
                                    on:click={() => clickOrDblclick(() => trade(c), () => onDBClickCard(c))}
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
                                        <h5>{""}</h5>
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
                        <div id="betDiv" class="backBlue brightBlue">
                            {#if u_dex === 0}
                                {#if players[u_dex + 1]['bet'] === null}
                                    <input bind:value={betCreds} id="betCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                    <button on:click={() => {bet("bet"); chipInput=false}} id="betBtn" type="button" class="btn btn-primary">Bet</button>
                                    <p class="red">{betErr}</p>
                                {:else}
                                    {#if raising === false}
                                        <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                        <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                        <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                    {:else}
                                        <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                        <button on:click={() => {raise(); chipInput = false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                        <p class="red">{betErr}</p>
                                    {/if}
                                {/if}

                            {:else}

                                {#if raising === false}
                                    <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                    <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                    <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                {:else}
                                    <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                    <button on:click={() => {raise(); chipInput=false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                    <p class="red">{betErr}</p>
                                {/if}

                            {/if}
                        </div>
                    {:else if game["phase"] === "card" || game["phase"] === "alderaan"}
                        <div id="betDiv" class="backBlue brightBlue">
                            {#if game_variant === 'traditional'}
                                <button on:click={() => tradeBtn('traditional')} type="button" id="tradeBtn" class="btn btn-primary">Trade</button>
                            {:else}
                                <button on:click={() => tradeBtn('deckTrade')} type="button" id="tradeBtn" class="btn btn-primary">Deck Trade</button>
                                <button on:click={() => tradeBtn('discardTrade')} type="button" id="tradeBtn" class="btn btn-primary">Discard Trade</button>
                                {#if players[u_dex]["hand"].length > 2}
                                    <button on:click={() => tradeBtn('discard')} type="button" id="tradeBtn" class="btn btn-primary">Discard</button>
                                {/if}
                            {/if}
                            <button on:click={stand} type="button" id="standBtn" class="btn btn-primary">Stand</button>
                        </div>
                    {/if}
                {/if}
            {:else if game["player_turn"] === user_id}
                <div id="betDiv" class="backBlue brightBlue">
                    <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
                </div>
            {/if}
        </div>
        <div class="mobileActBox" class:playing={u_dex != -1}></div>
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
