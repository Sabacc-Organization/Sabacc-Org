<script lang="ts">
    import { Socket, io } from "socket.io-client";
    import { onDestroy, onMount } from 'svelte';
    import {
        socket,
        BACKEND_URL,
        turnSound,
        game,
        thisPlayer,
        betCreds,
        user_id,
        activePlayers,
        chipInput,
        raising,
        raiseAmount,
        potsActive,
        followAmount,
        u_dex,
        game_variant,
        tradeCard,
        alderaanActive,
        cardBool,
        movesDone,
        currentMove,
        shiftActive,
        game_id
    } from './sharedValues'
    import {
        requestGameUpdate,
        updateClientGame,
        updateClientInfo
    } from './gameLogic'

    // Once page is mounted
    onMount(() => {
        // defines a new socket object for real-time communication with server
        $socket = io(BACKEND_URL);

        // code to catch errors
        $socket.io.on('error', (err: any) => {console.log(err)});

        // when there is a connection established with the server, it will explicitely ask the server for a game update. 
        // this is the only time it will explicitly ask for a game update.
        $socket.on('connect', () => {
            requestGameUpdate();
        });

        // when the server responds to a game update request or recieves new information, it will pass that info on to updateClientGame as serverInfo
        $socket.on('gameUpdate', (serverInfo: any) => {
            updateClientGame(serverInfo);
        });

        // sometimes the server wants to give the client information that only applies to them, such as their user ID.
        // clientUpdate is accessed when the server doesnt want to give that info to every client. it also give the updated game in serverInfo
        // updateClientGame is called within updateClientInfo. updateClientInfo is only called when first logging on.
        $socket.on('clientUpdate', (serverInfo: any) => {
            updateClientInfo(serverInfo);
        });

        // defining the Audio to be play apon your turn (it wouldnt work if i put it outside of onMount)
        $turnSound = new Audio("/move-sound.mp3");
    });

    //cards are handled differently on different versions, so I export them to let each version decide for itself what to do.
    export let renderCard;
    export let renderBack;

    // Betting Phase

    $: {
        if ($game["completed"] == 0 && $game["player_turn"] === $user_id && $game["phase"] === "betting"){
            if ($activePlayers.indexOf(thisPlayer) === 0 && $activePlayers[1]['bet'] === null){
                if ($betCreds == null){
                    $betCreds = 0;
                }
                $chipInput = true;
            }
            if ($raising && ($betCreds! <= $raiseAmount || $betCreds == null)){
                $betCreds = $raiseAmount+1;
            }
        }
    }

    $: {
        let players = $game["players"];
        if ($game["player_turn"] === user_id && $game["phase"] === "betting") {
            $potsActive = true;

            $raiseAmount = 0;
            $followAmount = 0;

            for (let i = 0; i < players.length; i++) {
                if (players[i]['bet'] != null) {
                    if (players[i]['bet'] > $raiseAmount) {
                        $raiseAmount = players[i]['bet'];
                    }
                }
            }
            $followAmount = $raiseAmount - players[$u_dex]['bet'];
            if (isNaN($followAmount)) {
                $followAmount = $raiseAmount;
            }

        } else {
            $potsActive = false;
        }
    }

    // Card Phase
    if ($game_variant === "traditional"){
        $tradeCard = {
            'val': 0,
            'suit': 'none',
            'prot': false
        };
    } else {
        $tradeCard = {
            'val': 0,
            'suit': 'none',
        };
    }

    $: {
        if ($game["player_turn"] === $user_id) {

            if ($game["phase"] === "card") {
                $cardBool = true;
                if ($game["cycle_count"] != 0) {
                    $alderaanActive = true;
                }
            }

            if ($game["phase"] === "alderaan") {
                $cardBool = true;
                $alderaanActive = false;
            }
        } else {
            $cardBool = false;
            $alderaanActive = false;
        }
    }

    // Shift Phase
    $: {
        if ($game["phase"] === "shift" && $user_id === $game["player_turn"] && ($currentMove === $movesDone - 1 || $movesDone === 0)) {
            $shiftActive = true;
        }
        else {
            $shiftActive = false;
        }
    }

    onDestroy(() => {
        if ($socket) {
            $socket.disconnect();
            console.log('Socket disconnected');
        }
    });

    // game replay stuff
    $: {
        if (($game["move_history"] !== null && $game["move_history"] !== undefined) && $currentMove === undefined) {
            $currentMove = $game["move_history"].length - 1;
        }
    }

</script>

<svelte:head>
  <title>Sabacc: Game {$game_id}</title>
</svelte:head>

<link rel="stylesheet" href="/styles/main/styles-game.css">
{#if theme === "modern"}
    <link rel="stylesheet" href="/styles/modern/modern-game.css">
    <link rel="stylesheet" href="/styles/modern/modern-players.css">
{/if}

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

        {#each game["players"] as p, i}
            <div id="{p['username']}Stuff" class:folded={p['folded']} class="parent player{orderedPlayers.indexOf(p)} playerStuff" class:playing={p['username'] === username}>

                <!-- Bet boxes -->
                {#if p['username'] === username}
                    <div id="{p['username']}BetBox" class="betBox backBlue {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div><span id="betSpan">{p['bet']===null? '':p['bet']}</span></h5> <div id="{p['username']}BetPile"></div></div>
                {:else}
                    <div id="{p['username']}BetBox" class="betBox backRed {game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div>{p['bet']===null? '':p['bet']}</h5></div>
                {/if}

                <!-- Cards -->
                <div class="cardsContainer">
                    {#each game["players"][i]["hand"] as c, ci}
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
                                {#if game["completed"] == 0 || p['folded'] || numOfActivePlayers() <= 1}
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
            {#if !game["completed"] && (currentMove === movesDone - 1 || movesDone === 0)}
                {#if game["player_turn"] === user_id}
                    {#if game["phase"] === "betting"}
                        <div id="betDiv" class="backBlue brightBlue">
                            {#if activePlayers.indexOf(thisPlayer) === 0}
                                {#if game["players"][u_dex + 1]['bet'] === null}
                                    <input bind:value={betCreds} id="betCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                    <button on:click={() => {bet("bet"); chipInput=false}} id="betBtn" type="button" class="btn btn-primary">Bet</button>
                                    <p class="red">{betErr}</p>
                                {:else}
                                    {#if game["settings"]["PokerStyleBetting"] && game["players"][u_dex]['bet'] === greatestBet && !raising}
                                        <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                                        <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                        <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                    {:else if !raising}
                                        <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                        <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                        <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                    {:else}
                                        <input bind:value={betCreds} id="raiseCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                        <button on:click={() => {raise(); chipInput = false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                        <p class="red">{betErr}</p>
                                    {/if}
                                {/if}

                            {:else if game["settings"]["PokerStyleBetting"] && game["players"][u_dex]['bet'] === greatestBet && !raising}
                                <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                                <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                            {:else}

                                {#if raising === false && activePlayers[activePlayers.indexOf(thisPlayer) - 1 % activePlayers.length]['bet'] === 0}
                                    <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                                    <button on:click={() => {raising = true; chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                    <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                                {:else if raising === false}
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
                                {#if game["players"][u_dex]["hand"].length > 2}
                                    <button on:click={() => tradeBtn('discard')} type="button" id="tradeBtn" class="btn btn-primary">Discard</button>
                                {/if}
                            {/if}
                            <button on:click={stand} type="button" id="standBtn" class="btn btn-primary">Stand</button>
                        </div>
                    {/if}
                {/if}
            {:else if game["player_turn"] === user_id && game["completed"] && currentMove === movesDone - 1}
                <div id="betDiv" class="backBlue brightBlue">
                    <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
                </div>
            {/if}
        </div>
        <div class="mobileActBox" class:playing={u_dex != -1}></div>
    </div>

    {#if game["move_history"] !== undefined && game["move_history"] !== null}
        <h5>Game Playback | Move {currentMove + 1 || 0} of {movesDone}</h5>
        <h5>
            {#if currentMove === -1}
                {new Date(game["created_at"]).toUTCString()}
            {:else}
                {new Date(game["move_history"].at(currentMove)["timestamp"]).toUTCString()}
            {/if}
        </h5>
        <div class="playback-buttons-container">
            <!-- Left arrow button -->
            <button on:click={playback_back} class="playback-button back-playback-arrow"></button>
            <!-- Number enter -->
            <input bind:value={playbackInput} placeholder=". . ." class="playback-input" type="number" min="0" max={movesDone} on:input={() => playback(playbackInput - 1)}/>
            <!-- Right arrow button -->
            <button on:click={playback_forward} class="playback-button forward-playback-arrow"></button>
        </div>
    {/if}

    <br>

    <h5>Game Settings</h5>
    <table class="game-settings-display-table">
        <tr>
            <th>Setting</th>
            <th>Value</th>
        </tr>
        {#each Object.keys(game["settings"]) as key}
            <tr>
                <td>{key}</td>
                <td>{game["settings"][key]}</td>
            </tr>
        {/each}
    </table>

    <br>

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
