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

<table class="game-settings-table">
    <tr>
        <td>Hand Ranking</td>
        <td>
            <select bind:value={handRanking} name="handRanking" class="form-control-sm" required>
                <option value="Wayne" selected>Wayne</option>
            </select>
        </td>
    </tr>
</table>

<img id="cs-hand-ranking-img" src="/images/cs-hand-rankings/{handRanking}.png" alt="{handRanking} hand ranking">

<table class="game-settings-table">
    <tr>
        <th colspan="2" class="text-center">Credits & Antes</th>
    </tr>
    <tr>
        <td>Starting Credits</td>
        <td><input bind:value={startingCredits} name="startingCredits" placeholder="Starting Credits" type="number" min="1" max="1000000" step="1" required></td>
    </tr>
    <tr>
        <td>Hand Pot Ante</td>
        <td><input bind:value={handPotAnte} name="handPotAnte" placeholder="Hand Pot Ante" type="number" min="1" max="1000000" step="1" required></td>
    </tr>
    <tr>
        <td>Sabacc Pot Ante</td>
        <td><input bind:value={sabaccPotAnte} name="sabaccPotAnte" placeholder="Sabacc Pot Ante" type="number" min="2" max="1000000" step="1" required></td>
    </tr>

    <tr>
        <th colspan="2" class="text-center">Card Action Costs</th>
    </tr>
    <tr>
        <td>Deck Draw Cost</td>
        <td><input bind:value={deckDrawCost} name="deckDrawCost" placeholder="Deck Draw Cost" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Discard Draw Cost</td>
        <td><input bind:value={discardDrawCost} name="discardDrawCost" placeholder="Discard Draw Cost" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Deck Trade Cost</td>
        <td><input bind:value={deckTradeCost} name="deckTradeCost" placeholder="Deck Trade Cost" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Discard Trade Cost</td>
        <td><input bind:value={discardTradeCost} name="discardTradeCost" placeholder="Discard Trade Cost" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Round 1 Discard Cost</td>
        <td><input bind:value={discardCosts[0]} name="r1DiscardCost" placeholder="Discard Cost 1" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Round 2 Discard Cost</td>
        <td><input bind:value={discardCosts[1]} name="r2DiscardCost" placeholder="Discard Cost 2" type="number" min="1" max="1000" step="1" required></td>
    </tr>
    <tr>
        <td>Round 3 Discard Cost</td>
        <td><input bind:value={discardCosts[2]} name="r3DiscardCost" placeholder="Discard Cost 3" type="number" min="1" max="1000" step="1" required></td>
    </tr>

    <tr>
        <th colspan="2" class="text-center">Poker Style Betting
            <label class="switch child">
                <input bind:checked={pokerStyleBetting} name="pokerStyleBetting" type="checkbox">
                <span class="slider round"></span>
            </label>
        </th>
    </tr>
    {#if pokerStyleBetting}
        <tr>
            <td>Big Blind</td>
            <td><input bind:value={bigBlind} name="bigBlind" type="number" min="2" max="300" step="1" required></td>
        </tr>
        <tr>
            <td>Small Blind</td>
            <td><input bind:value={smallBlind} name="smallBlind" type="number" min="1" max="299" step="1" required></td>
        </tr>
    {/if}
</table>