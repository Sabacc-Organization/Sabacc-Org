<script lang="ts">

    import {
        game,
        currentMove,
        movesDone,
        user_id,
        activePlayers,
        thisPlayer,
        u_dex,
        betCreds,
        chipInput,
        betErr,
        greatestBet,
        raising,
        game_variant,
        cardBool,
        shiftActive,
        alderaanActive,
        potsActive,
        followAmount,
        raiseAmount,
        tradeCard,
        SHIFT_TOKENS
    } from "./sharedValues";

    import {
        bet,
        check,
        fold,
        call,
        raise,
        tradeBtn,
        stand,
        shiftTokenSelect,
        playAgain,
        nextHand
    } from "./gameLogic";

    export let renderCard

    // actBox reacitivity

    // Betting Phase

    $: {
        if ($game["completed"] == 0 && $game["player_turn"] === $user_id && $game["phase"] === "betting"){
            if ($activePlayers.indexOf($thisPlayer) === 0 && $activePlayers[1]['bet'] === null){
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
        if ($game["player_turn"] === $user_id && $game["phase"] === "betting") {
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

    // Shift tokens
    $: shiftTokenBool = ($game["phase"] === "shiftTokenSelect" && $game["player_turn"] === $user_id)
</script>

<div id="actBox" class:shiftToken={shiftTokenBool}>
    {#if !$game["completed"] && ($currentMove === $movesDone - 1 || $movesDone === 0)}
        {#if $game["player_turn"] === $user_id}
            {#if $game["phase"] === "betting"}
                <div id="betDiv" class="backBlue brightBlue">
                    {#if $activePlayers.indexOf($thisPlayer) === 0}
                        {#if $game["players"][$u_dex + 1]['bet'] === null}
                            <input bind:value={$betCreds} id="betCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                            <button on:click={() => {bet("bet"); $chipInput=false}} id="betBtn" type="button" class="btn btn-primary">Bet</button>
                            <p class="red">{$betErr}</p>
                        {:else}
                            {#if $game["settings"]["PokerStyleBetting"] && $game["players"][$u_dex]['bet'] === $greatestBet && !$raising}
                                <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                                <button on:click={() => {$raising = true; $chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                            {:else if !$raising}
                                <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                                <button on:click={() => {$raising = true; $chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                                <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                            {:else}
                                <input bind:value={$betCreds} id="raiseCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                                <button on:click={() => {raise(); $chipInput = false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                                <p class="red">{$betErr}</p>
                            {/if}
                        {/if}

                    {:else if $game["settings"]["PokerStyleBetting"] && $game["players"][$u_dex]['bet'] === $greatestBet && !$raising}
                        <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                        <button on:click={() => {$raising = true; $chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                        <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                    {:else}

                        {#if $raising === false && $activePlayers[$activePlayers.indexOf($thisPlayer) - 1 % $activePlayers.length]['bet'] === 0}
                            <button on:click={check} type="button" id="checkOpt" class="btn btn-primary">Check</button>
                            <button on:click={() => {$raising = true; $chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                            <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                        {:else if $raising === false}
                            <button on:click={call} type="button" id="callOpt" class="btn btn-primary">Call</button>
                            <button on:click={() => {$raising = true; $chipInput = true}} type="button" id="raiseOpt" class="btn btn-primary">Raise</button>
                            <button on:click={fold} type="button" id="foldOpt" class="btn btn-primary">Fold</button>
                        {:else}
                            <input bind:value={$betCreds} id="raiseCredits" type="number" class="form-control form-group" placeholder="Credits" required>
                            <button on:click={() => {raise(); $chipInput=false}} id="raiseBtn" type="button" class="btn btn-primary">Raise</button>
                            <p class="red">{$betErr}</p>
                        {/if}

                    {/if}
                </div>
            {:else if $game["phase"] === "card" || $game["phase"] === "alderaan"}
                <div id="betDiv" class="backBlue brightBlue">
                    {#if $game_variant === 'traditional'}
                        <button on:click={() => tradeBtn('traditional')} type="button" id="tradeBtn" class="btn btn-primary">Trade</button>
                    {:else}
                        <button on:click={() => tradeBtn('deckTrade')} type="button" id="tradeBtn" class="btn btn-primary">Deck Trade</button>
                        <button on:click={() => tradeBtn('discardTrade')} type="button" id="tradeBtn" class="btn btn-primary">Discard Trade</button>
                        {#if $game["players"][$u_dex]["hand"].length > 2}
                            <button on:click={() => tradeBtn('discard')} type="button" id="tradeBtn" class="btn btn-primary">Discard</button>
                        {/if}
                    {/if}
                    <button on:click={stand} type="button" id="standBtn" class="btn btn-primary">Stand</button>
                </div>
            {:else if $game["phase"] === "draw"}
                <div id="betDiv" class="backBlue brightBlue">
                    <button on:click={stand} class="btn btn-primary">Stand</button>
                </div>
            {:else if $game["phase"] === "shiftTokenSelect"}
                <div id="betDiv" class="backBlue brightBlue grid">
                    {#each SHIFT_TOKENS as shiftToken}
                        <div class="cardContainer">
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div on:click={() => shiftTokenSelect(shiftToken)}
                            class="card child shiftToken own active"
                            style="{renderCard(shiftToken)}"></div>
                        </div>
                    {/each}
                </div>
            {:else if $game["phase"] === "reveal"}
                <div id="betDiv" class="backBlue brightBlue">
                    <button on:click={nextHand} class="btn btn-primary">Next Hand</button>
                </div>
            {/if}
        {/if}
    {:else if $game["player_turn"] === $user_id && $game["completed"] && ($currentMove === $movesDone - 1)}
        <div id="betDiv" class="backBlue brightBlue">
            <button on:click={playAgain} type="button" id="pAgainBtn" class="btn btn-primary">Play Again</button>
        </div>
    {/if}
</div>
<div class="mobileActBox" class:playing={$u_dex != -1}></div>