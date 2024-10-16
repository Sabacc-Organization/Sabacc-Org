<script lang="ts">

    import {
        potsActive,
        game,
        u_dex,
        user_id,
        cardBool,
        alderaanActive,
        cardDesign,
        shiftActive,
        game_variant
    } from "./sharedValues";

    import { 
        check,
        draw,
        alderaan,
        shift
    } from "./gameLogic";

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

    export let renderCard;
    export let renderBack;
</script>
<div id="gameInfo" class="parent" class:playing={$u_dex != -1}>

    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div on:dblclick={check} class:active={$potsActive} id="pots" class="child {$potsActive}">
        <h5>Sabacc: <span id="sabacc_pot">{$game["sabacc_pot"]}</span></h5>
        <h5>Hand: <span id="hand_pot">{$game["hand_pot"]}</span></h5>
    </div>

    <div class="cardsContainer">
        <div class="cardContainer">
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div on:click={() => draw('deckDraw')} class:active={$cardBool} id="deck" class="card child" style="{renderBack($cardDesign)}"></div>
        </div>

        {#if $game_variant === "corellian_spike"}
            <div class="cardContainer">
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <!-- svelte-ignore a11y-no-static-element-interactions -->
                <div on:click={() => draw('discardDraw')} class:active={$cardBool} id="discard" class="card child" style={renderCard($game['discard_pile'][$game['discard_pile'].length - 1])}></div>
                <h5>{$cardDesign === "pescado"? "":$game['discard_pile'][$game['discard_pile'].length - 1]['val']}</h5>
            </div>
        {/if}
    </div>

    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <span on:click={shift} class:shiftActive={$shiftActive} class="dieContainer">
        <div id="dieOne" class="child die"></div>
        <div id="dieTwo" class="child die shift{$game["shift"]}"></div>
    </span>

    {#if $game_variant === 'traditional'}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div on:click={alderaan} class:active={alderaanActive} id="alderaan" class="child alderaan {$game["phase"]}Blown"></div>
    {/if}
</div>