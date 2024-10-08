<script lang="ts">

    let pokerStyleBetting: boolean;
    let smallBlind = 1;
    let bigBlind = 2;
    let startingCredits = 1000;
    let handPotAnte = 5;
    let sabaccPotAnte = 10;

    let deckDrawCost = 5;
    let discardDrawCost = 10;
    let deckTradeCost = 10;
    let discardTradeCost = 15;
    let discardCosts = [15, 20, 25];

    let handRanking = "Wayne";

    $: {
        if (smallBlind >= bigBlind) {
            bigBlind = smallBlind + 1;
        }

        if (bigBlind >= startingCredits) {
            startingCredits = bigBlind + 1;
        }

        if (handPotAnte >= startingCredits) {
            startingCredits = handPotAnte + 1;
        }

        if (sabaccPotAnte >= startingCredits) {
            startingCredits = sabaccPotAnte + 1;
        }

        if (handRanking !== "Wayne") {
            handRanking = "Wayne";
        }
    }
</script>

<h5>Game Settings</h5>

<br>
<div class="stacked-input">
    <label for="handRanking">Hand Ranking</label>
    <select bind:value={handRanking} name="handRanking" class="form-control-sm" required>
        <option value="Wayne">Wayne</option>
    </select>
</div>

<div class="stacked-input">
    <label for="startingCredits">Starting Credits</label>
    <input bind:value={startingCredits} name="startingCredits" class="form-control-sm" placeholder="Starting Credits" type="number" min="1" max="1000000" step="1" required>
</div>

<div class="parent">
    <div class="stacked-input child">
        <label for="handPotAnte">Hand Pot Ante</label>
        <input bind:value={handPotAnte} name="handPotAnte" class="form-control-sm" placeholder="Hand Pot Ante" type="number" min="1" max="1000000" step="1" required>
    </div>

    <div class="stacked-input child">
        <label for="sabaccPotAnte">Sabacc Pot Ante</label>
        <input bind:value={sabaccPotAnte} name="sabaccPotAnte" class="form-control-sm" placeholder="Sabacc Pot Ante" type="number" min="2" max="1000000" step="1" required>
    </div>
</div>

<div class="parent">
    <div class="stacked-input child">
        <label for="deckDrawCost">Deck Draw Cost</label>
        <input bind:value={deckDrawCost} name="deckDrawCost" class="form-control-sm" placeholder="Deck Draw Cost" type="number" min="1" max="1000" step="1" required>
    </div>

    <div class="stacked-input child">
        <label for="discardDrawCost">Discard Draw Cost</label>
        <input bind:value={discardDrawCost} name="discardDrawCost" class="form-control-sm" placeholder="Discard Draw Cost" type="number" min="1" max="1000" step="1" required>
    </div>
</div>

<div class="parent">
    <div class="stacked-input child">
        <label for="deckTradeCost">Deck Trade Cost</label>
        <input bind:value={deckTradeCost} name="deckTradeCost" class="form-control-sm" placeholder="Deck Trade Cost" type="number" min="1" max="1000" step="1" required>
    </div>

    <div class="stacked-input child">
        <label for="discardTradeCost">Discard Trade Cost</label>
        <input bind:value={discardTradeCost} name="discardTradeCost" class="form-control-sm" placeholder="Discard Trade Cost" type="number" min="1" max="1000" step="1" required>
    </div>
</div>

<div class="parent">
    <div class="stacked-input child">
        <label for="r1DiscardCost">Round 1 Discard Cost</label>
        <input bind:value={discardCosts[0]} name="r1DiscardCost" class="form-control-sm" placeholder="Round 1 Discard Cost" type="number" min="1" max="1000" step="1" required>
    </div>

    <div class="stacked-input child">
        <label for="r2DiscardCost">Round 2 Discard Cost</label>
        <input bind:value={discardCosts[1]} name="r2DiscardCost" class="form-control-sm" placeholder="Round 2 Discard Cost" type="number" min="1" max="1000" step="1" required>
    </div>

    <div class="stacked-input child">
        <label for="r3DiscardCost">Round 3 Discard Cost</label>
        <input bind:value={discardCosts[2]} name="r3DiscardCost" class="form-control-sm" placeholder="Round 3 Discard Cost" type="number" min="1" max="1000" step="1" required>
    </div>
</div>


<div class="parent">
    <h6 class="child">Poker Style Betting</h6>
    <!-- Rounded switch -->
    <label class="switch child">
        <input bind:checked={pokerStyleBetting} name="pokerStyleBetting" type="checkbox">
        <span class="slider round"></span>
    </label>
</div>

{#if pokerStyleBetting}
    <div class="parent">
        <div class="stacked-input child">
            <label for="bigBlind">Big Blind</label>
            <input name="bigBlind" type="number" bind:value={bigBlind} class="form-control-sm" min="2" max="300" step="1" required>
        </div>

        <div class="stacked-input child">
            <label for="smallBlind">Small Blind</label>
            <input name="smallBlind" type="number" bind:value={smallBlind} class="form-control-sm" min="1" max="299" step="1" required>
        </div>
    </div>
{/if}