<script lang="ts">
    import { page } from '$app/stores';
    import { checkLogin, customRedirect } from '$lib';
    import Cookies from 'js-cookie';
    import { onDestroy, onMount } from 'svelte';

    // URLs for Requests and Redirects
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    // Cookie info
    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let loggedIn = false;
    let dark = Cookies.get("dark");
    let theme = Cookies.get("theme");

    // Page header (plaer vs. player vs. player)
    let header = "";

    // Error message for invalid inputs
    let errorMsg = "";

    // Accessing the 'username' parameter from the URL
    $: game_id = $page.params.game_id;

    // Game information
    let game = {
        "p_act": "",
        "hand_pot": 0,
        "sabacc_pot": 0,
        "player_hands": "",
        "player_protecteds": "",
        "phase": "",
        "player_bets": "",
        "player_credits": "",
        "shift": 0,
        "player_ids": "",
        "player_turn": -1,
        "completed": 0,
        "cycle_count": 0
    };
    let players: any[] = [];
    let orderedPlayers: any[] = [];

    // User ID
    let user_id = -1;

    // Index of user in list of users
    let u_dex = -1;


    // Game data refresh interval
    let refreshInterval: NodeJS.Timeout;

    // Clean up request cycle
    onDestroy(() => {
        clearInterval(refreshInterval);

    });

    // Once page is mounted
    onMount(async() => {

        // Popolate page content
        await refreshGame();

        // Set refresh intervla for game data (5000 ms)
        refreshInterval = setInterval(refreshGame, 5000);

    });

    // refresh game date function
    async function refreshGame() {
        try {

            // Request data

            let requestData = {};

            if (username != undefined) {
                requestData = {
                    "username": username,
                    "game_id": game_id
                }
            } else {
                requestData = {
                    "username": "",
                    "game_id": game_id
                }
            }

            const response = await fetch(BACKEND_URL + "/game", {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });

            let res = await response.json();
            if (response.ok) {
                game = res["gata"];
                user_id = res["user_id"];
                u_dex = game["player_ids"].split(",").indexOf(user_id.toString());

                let ps: any[] = []; 
                header = "";
                for (let i = 0; i < res["users"].length; i++) {
                    if (i != 0) {
                        header += " vs. "
                    }
                    players[i] = res["users"][i];
                    orderedPlayers[i] = res["users"][i];
                    ps[i] = res["users"][i];
                    header += res["users"][i];
                }

                if (u_dex != -1) {
                    let frontVal = ps.splice(u_dex, 1);
                    orderedPlayers = frontVal.concat(ps);
                }

            }
            errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }
    }


    async function protect(id) {

        let elem = document.getElementById(id);

        try {

        let requestData = {
            "username": username,
            "password": password,
            "game_id": game_id,
            "protect": elem.innerText
        }

        const response = await fetch(BACKEND_URL + "/protect", {
            method: 'POST', // Set the method to POST
            headers: {
                'Content-Type': 'application/json' // Set the headers appropriately
            },
            body: JSON.stringify(requestData) // Convert your data to JSON
        });

        let res = await response.json();
        if (response.ok) {
            game = res["gata"];
        }
        errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }

    }

    // Betting Phase

    let betCreds: number;
    let betErr = "";

    let raising = false;

    async function bet(action: string) {
        if (potsActive) {
            if ((isNaN(betCreds) || betCreds < 0 || betCreds > parseInt(game["player_credits"].split(",")[u_dex])) && action != "fold") {
                betErr = "Please input a number of credits you would like to bet(an integer 0 to " + game["player_credits"].split(",")[u_dex] + ")";
            } else {

                let tempCreds = betCreds;
                if (raising && !isNaN(parseInt(game["player_bets"].split(",")[u_dex]))) {
                    tempCreds = betCreds - parseInt(game["player_bets"].split(",")[u_dex]);
                }
                try {

                    let requestData = {
                        "username": username,
                        "password": password,
                        "game_id": game_id,
                        "action": action,
                        "amount": tempCreds
                    }

                    const response = await fetch(BACKEND_URL + "/bet", {
                        method: 'POST', // Set the method to POST
                        headers: {
                            'Content-Type': 'application/json' // Set the headers appropriately
                        },
                        body: JSON.stringify(requestData) // Convert your data to JSON
                    });

                    let res = await response.json();
                    if (response.ok) {
                        game = res["gata"];
                    }
                    errorMsg = res["message"];
                } catch (e) {
                    console.log(e);
                }
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
        if (game["completed"] === 0 && game["player_turn"] === user_id && game["phase"] === "betting"){
            if (u_dex === 0 && game["player_bets"].split(",")[u_dex + 1] === ""){
                if (betCreds == null){
                    betCreds = 0;
                }
                chipInput = true;
            }
            if (raising && betCreds <= raiseAmount){
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
        if (game["player_turn"] === user_id) {
            if (game["phase"] === "betting") {

                potsActive = true;

                raiseAmount = 0;
                followAmount = 0;

                for (let i = 0; i < game["player_bets"].split(",").length; i++) {
                    if (game["player_bets"].split(",")[i] != "") {
                        if (parseInt(game["player_bets"].split(",")[i]) > raiseAmount) {
                            raiseAmount = parseInt(game["player_bets"].split(",")[i]);
                        }
                    }
                }
                followAmount = raiseAmount - parseInt(game["player_bets"].split(",")[u_dex]);
                if (isNaN(followAmount)) {
                    followAmount = raiseAmount;
                }
                
            }
        }
    }

    async function call() {
        betCreds = followAmount;
        bet("call");
    }

    async function raise() {
        if (betCreds > raiseAmount && betCreds <= parseInt(game["player_credits"].split(",")[u_dex])) {
            bet("raise");
        }
        else {
            betErr = "Invalid amount of credits";
        }
    }

    async function fold() {
        bet("fold");
    }

    // Card Phase

    let cardBool = false;
    let alderaanActive = false;

    let tradeOpen = false;
    let tradeCard = "";

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

    async function card(action: string) {
        if (cardBool) {
            try {

                let requestData = {
                    "username": username,
                    "password": password,
                    "game_id": game_id,
                    "action": action,
                    "trade": tradeCard
                }

                const response = await fetch(BACKEND_URL + "/card", {
                    method: 'POST', // Set the method to POST
                    headers: {
                        'Content-Type': 'application/json' // Set the headers appropriately
                    },
                    body: JSON.stringify(requestData) // Convert your data to JSON
                });

                let res = await response.json();
                if (response.ok) {
                    game = res["gata"];
                }
                errorMsg = res["message"];
            } catch (e) {
                console.log(e);
            }
            tradeOpen = false;
        }
    }

    async function draw() {
        card("draw");
    }

    function tradeBtn() {
        tradeOpen = true;
    }

    async function trade(c: string) {
        if (tradeOpen) {
            tradeCard = document.getElementById(c)?.innerText;
            card("trade");
        }
    }

    async function stand() {
        card("stand");
    }

    async function alderaan() {
        if (alderaanActive) {
            card("alderaan");
        }
    }

    // Shift Phase

    // Play Again
    async function playAgain() {
        try {

            let requestData = {
                "username": username,
                "password": password,
                "game_id": game_id
            }

            const response = await fetch(BACKEND_URL + "/cont", {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });

            let res = await response.json();
            if (response.ok) {
                game = res["gata"];
            }
            errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }
    }

</script>

<svelte:head>
  <title>Sabacc: Game {game_id}</title>
</svelte:head>

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
            <button on:click={tradeBtn} type="button" id="tradeBtn" class="btn btn-primary smol">Trade</button>
            <br>
            <button on:click={stand} type="button" id="standBtn" class="btn btn-primary smol">Stand</button>
        </div>

        <div id="dieOne" class="child die"></div>

        <div id="dieTwo" class="child die shift{game["shift"]}"></div>

        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div on:click={alderaan} class:active={alderaanActive} id="alderaan" class="child alderaan {game["phase"]}Blown"></div>

        {#if game["completed"] === 1 && game["player_turn"] === user_id}
            <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
        {/if}

    </div>

    {#each players as p, i}

        <div id="{p}Stuff" class="parent player{orderedPlayers.indexOf(p)}">

            <!-- Bet boxes -->
            {#if p === username}
                <div id="{p}BetBox" class="backBlue"><h5>$<span id="betSpan">{game["player_bets"].split(",")[i]}</span></h5> <div id="{p}BetPile"></div></div>
            {:else}
                <div id="{p}BetBox" class="backRed"><h5>${game["player_bets"].split(",")[i]}</h5></div>
            {/if}

            <!-- Cards -->
            {#each game["player_hands"].split(";")[i].split(",") as c, ci}

                    {#if p === username}
                        {#if game["player_protecteds"].split(";")[i].split(",")[ci] === "0"}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div on:click={() => trade("card" + ci.toString())} on:dblclick={() => protect("card" + ci.toString())} id="card{ci.toString()}" class="card child own"><h5>{c}</h5></div>
                        {:else}
                            <div class="card child own protected"><h5>{c}</h5></div>
                        {/if}
                    {:else}
                        {#if game["completed"] === 0}
                            {#if game["player_protecteds"].split(";")[i].split(",")[ci] === "0"}
                                <div class="card child"></div>
                            {:else}
                                <div class="card child protected"><h5>{c}</h5></div>
                            {/if}
                        {:else if game["completed"] === 1}
                            <div class="card child"><h5>{c}</h5></div>
                        {/if}
                    {/if}

            {/each}

            <!-- Player boxes -->
            {#if p === username}
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                <div id="{p}Box" class="backBlue">
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
                    <h5>$<span id="credits">{game["player_credits"].split(",")[i]}</span></h5>
                </div>
            {:else}
                <div id="{p}Box" class="backRed"> <h5>{p}</h5> <div class="parent"> <div class="chip bigChip child"></div> <div class="chip midChip child"></div> <div class="chip lowChip child"></div> </div> <h5>$<span id="{p}_credits">{game["player_credits"].split(",")[i]}</span></h5></div>
            {/if}

        </div>

    {/each}

    <div id="actBox">

        {#if game["completed"] === 0}
            {#if game["player_turn"] === user_id}
        
                {#if game["phase"] === "betting"}
                    {#if u_dex === 0}
                        {#if game["player_bets"].split(",")[u_dex + 1] === ""}
                            <div id="betDiv" class="backBlue"> 
                                <input bind:value={betCreds} id="betCredits" type="number" class="form-control form-group" min="0" max={game["player_credits"].split(",")[u_dex]} placeholder="Credits" required> 
                                <button on:click={() => {bet("bet"); chipInput=false}} id="betBtn" type="button" class="btn btn-primary">Bet</button> 
                                <p class="red">{betErr}</p>
                            </div>
                        {:else}
                            {#if raising === false}
                                <div id="betDiv" class="backBlue"> 
                                    <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button> 
                                    <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button> 
                                    <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button> 
                                </div>
                            {:else}
                                <div id="betDiv" class="backBlue"> 
                                    <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={game["player_credits"].split(",")[u_dex]} placeholder="Credits" required> 
                                    <button on:click={() => {raise(); chipInput = false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button> 
                                    <p class="red">{betErr}</p>
                                </div>
                            {/if}
                        {/if}

                    {:else}

                        {#if raising === false}
                            <div id="betDiv" class="backBlue"> 
                                <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button> 
                                <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button> 
                                <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button> 
                            </div>
                        {:else}
                            <div id="betDiv" class="backBlue"> 
                                <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" min="{raiseAmount + 1}" max={game["player_credits"].split(",")[u_dex]} placeholder="Credits" required> 
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

<style>
    main {
        background-image: url("data:image/jpeg;base64,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");
        background-repeat: no-repeat, no-repeat;
        background-size: cover;
    }

    .shift1 {
        background-color: #0cc23c;
    }
</style>