<script lang="ts">

    let pokerStyleBetting: boolean;
    let smallBlind = 1;
    let bigBlind = 2;

    $: {
        if (smallBlind >= bigBlind) {
            bigBlind = smallBlind + 1;
        }
    }
</script>

<h5>Game Settings</h5>

<div class="parent">
    <h6 class="child">Poker Style Betting</h6>
    <!-- Rounded switch -->
    <label class="switch child">
        <input bind:checked={pokerStyleBetting} name="pokerStyleBetting" type="checkbox">
        <span class="slider round"></span>
    </label>
</div>

{#if pokerStyleBetting}
    <h6>Small Blind</h6>
    <input name="smallBlind" type="number" bind:value={smallBlind} min="1" max="99" step="1" required>

    <h6>Big Blind</h6>
    <input name="bigBlind" type="number" bind:value={bigBlind} min="2" max="100" step="1" required>
{/if}