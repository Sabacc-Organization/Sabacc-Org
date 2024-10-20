<script lang="ts">

    import {
        orderedPlayers,
        username,
        game,
        cardDesign,
        game_variant,
        socket,
        password,
        game_id,
    } from "./sharedValues";

    import {
        trade,
        handleChipPress,
        clickOrDblclick,
        numOfActivePlayers
    } from "./gameLogic";

    export let p;
    export let i;
    export let renderCard;
    export let renderBack;

    function onDoubleClickCard(card : {[id: string]: any}) {
        if ($game_variant === "traditional") {
            let clientInfo = {
                "username": $username,
                "password": $password,
                "game_id": $game_id,
                "game_variant": $game_variant,
                "action": "protect",
                "protect": card
            }
            $socket!.emit('gameAction', clientInfo)
        }
    }
</script>

<div id="{p['username']}Stuff" class:folded={p['folded']} class="parent player{$orderedPlayers.indexOf(p)} playerStuff" class:playing={p['username'] === $username}>

    <!-- Bet boxes -->
    {#if p['username'] === $username}
        <div id="{p['username']}BetBox" class="betBox backBlue {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}">
            <h5>
                <div class="imperial-credits-logo"></div>
                {#if $game_variant !== "kessel"}
                    <span id="betSpan">{p['bet'] === null? '':p['bet']}</span>
                {:else}
                <span id="betSpan">{p['usedChips'] === null? '':p['usedChips']}</span>
                {/if}
            </h5>
            <div id="{p['username']}BetPile"></div>
        </div>
    {:else}
        <div id="{p['username']}BetBox" class="betBox backRed {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}">
            <h5>
                <div class="imperial-credits-logo"></div>
                {#if $game_variant !== "kessel"}
                    {p['bet']===null? '':p['bet']}
                {:else}
                    {p['usedChips'] === null? '' : p['usedChips']}
                {/if}
            </h5>
        </div>
    {/if}

    <!-- Cards -->
    <div class="cardsContainer">
        {#if $game_variant !== "kessel"}
            {#each $game["players"][i]["hand"] as c, ci}
                <div class="cardContainer">
                    {#if p['username'] === $username}
                        {#if !c['prot']}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div
                            on:click={() => clickOrDblclick(() => trade(c), () => onDoubleClickCard(c))}
                            id="card{ci.toString()}"
                            class="card child own"
                            style="{renderCard(c)}">
                            </div>
                            <h5>{$cardDesign === "pescado"? "":c['val']}</h5>
                        {:else}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <div
                            on:click={() => trade(c)}
                            id="card{ci.toString()}"
                            class="card child own protected"
                            style="{renderCard(c)}">
                            </div>
                            <h5 class="protected">{$cardDesign === "pescado"? "":c['val']}</h5>
                        {/if}
                    {:else}
                        {#if $game["completed"] == 0 || p['folded'] || numOfActivePlayers() <= 1}
                            {#if !c['prot']}
                                <div class="card child" style="{renderBack()}"></div>
                                <h5>{""}</h5>
                            {:else}
                                <div class="card child protected" style="{renderCard(c)}"></div>
                                <h5 class="protected">{$cardDesign === "pescado"? "":c['val']}</h5>
                            {/if}
                        {:else if $game["completed"] == 1}
                            <div class="card child" style="{renderCard(c)}"></div>
                            <h5>{$cardDesign === "pescado"? "":c['val']}</h5>
                        {/if}
                    {/if}
                </div>
            {/each}
        {:else}
            {#if p["username"] === $username}
                <div class="cardContainer">
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div
                    on:click={() => clickOrDblclick(() => trade(p["negativeCard"]), () => onDoubleClickCard(p["negativeCard"]))}
                    id="cardNegative"
                    class="card child own"
                    style="{renderCard(p["negativeCard"], true)}">
                    </div>
                    <h5>{""}</h5>
                </div>
                {#if p["extraCard"]}
                    <div class="cardContainer">
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                        <div
                        on:click={() => clickOrDblclick(() => trade(p["extraCard"]), () => onDoubleClickCard(p["extraCard"]))}
                        id="cardExtra"
                        class="card child own"
                        style="{renderCard(p["extraCard"], p["extraCardIsNegative"])}">
                        </div>
                        <h5>{""}</h5>
                    </div>
                {/if}
                <div class="cardContainer">
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div
                    on:click={() => clickOrDblclick(() => trade(p["positiveCard"]), () => onDoubleClickCard(p["positiveCard"]))}
                    id="cardPositive"
                    class="card child own"
                    style="{renderCard(p["positiveCard"], false)}">
                    </div>
                    <h5>{""}</h5>
                </div>
            {:else}
                <div class="cardContainer">
                    <div class="card child" style="{renderBack(true)}"></div>
                    <h5>{""}</h5>
                </div>
                {#if p["extraCard"]}
                    <div class="cardContainer">
                        <div class="card child" style="{renderBack(p["extraCardIsNegative"])}"></div>
                        <h5>{""}</h5>
                    </div>
                {/if}
                <div class="cardContainer">
                    <div class="card child" style="{renderBack(false)}"></div>
                    <h5>{""}</h5>
                </div>
            {/if}
        {/if}
    </div>

    <!-- Player boxes -->
    {#if p['username'] === $username}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div id="{p['username']}Box" class="backBlue {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox">
            <h5>{p['username']}</h5>
            {#if $game_variant !== "kessel"}
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
            {:else}
                <div class="cardsContainer">
                    {#each p["shiftTokens"] as shiftToken}
                        <div class="cardContainer">
                            <div class="card child shiftToken" style="{renderCard(shiftToken)}"></div>
                        </div>
                    {/each}
                </div>
            {/if}
            <h5><div class="imperial-credits-logo"></div>
                {#if $game_variant !== "kessel"}
                    <span id="credits">{p['credits']}</span>
                {:else}
                    <span id="chips">{p['chips']}</span>
                {/if}
            </h5>
        </div>
    {:else}
        <div id="{p['username']}Box" class="backRed {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox">
            <h5>{p['username']}</h5>
            {#if $game_variant !== "kessel"}
                <div class="parent">
                    <div class="chip bigChip child"></div>
                    <div class="chip midChip child"></div>
                    <div class="chip lowChip child"></div>
                </div>
            {/if}
            <h5>
                <div class="imperial-credits-logo"></div>
                    <span id="{p['username']}_credits">{$game_variant !== "kessel"? p['credits'] : p['chips']}</span>
            </h5>
        </div>
    {/if}

</div>