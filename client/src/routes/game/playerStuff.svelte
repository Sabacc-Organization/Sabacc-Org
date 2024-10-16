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
        <div id="{p['username']}BetBox" class="betBox backBlue {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div><span id="betSpan">{p['bet']===null? '':p['bet']}</span></h5> <div id="{p['username']}BetPile"></div></div>
    {:else}
        <div id="{p['username']}BetBox" class="betBox backRed {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"}"><h5><div class="imperial-credits-logo"></div>{p['bet']===null? '':p['bet']}</h5></div>
    {/if}

    <!-- Cards -->
    <div class="cardsContainer">
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
    </div>

    <!-- Player boxes -->
    {#if p['username'] === $username}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div id="{p['username']}Box" class="backBlue {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox">
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
    <div id="{p['username']}Box" class="backRed {$game["player_turn"] == p['id']? "turnGlow" : "noTurnGlow"} playerBox"> <h5>{p['username']}</h5> <div class="parent"> <div class="chip bigChip child"></div> <div class="chip midChip child"></div> <div class="chip lowChip child"></div> </div> <h5><div class="imperial-credits-logo"></div><span id="{p['username']}_credits">{p['credits']}</span></h5></div>
    {/if}

</div>