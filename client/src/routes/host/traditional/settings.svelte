<script lang="ts">

    let pokerStyleBetting: boolean;
    let smallBlind = 1;
    let bigBlind = 2;
    let startingCredits = 1000;
    let handPotAnte = 5;
    let sabaccPotAnte = 10;

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
    }
</script>

<h5>Game Settings</h5>

<br>

<table class="game-settings-table">
    <tr>
        <th colspan="2" class="text-center">Game Settings</th>
    </tr>
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