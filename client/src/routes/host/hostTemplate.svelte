<script lang="ts">
    import { enhance } from "$app/forms";

    export let form;

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    /** @type {import('./$types').PageData} */
	// export let data;
    export let game_variant: string;
    let game_variant_string = {'traditional':'Traditional', 'corellian_spike':'Corellian Spike'}[game_variant]

    $: errorMsg = form?.error;

    let players: string[] = [];

    let player2 = "";
    let player3 = "";
    let player4 = "";
    let player5 = "";
    let player6 = "";
    let player7 = "";
    let player8 = "";

    function refresh() {
        players = [];
        if (player2 === "") {
            player3 = "";
        } else {
            players.push(player2);
        }

        if (player3 === "") {
            player4 = "";
        } else {
            players.push(player3);
        }

        if (player4 === "") {
            player5 = "";
        } else {
            players.push(player4);
        }
        
        if (player5 === "") {
            player6 = "";
        } else {
            players.push(player5);
        }
        
        if (player6 === "") {
            player7 = "";
        } else {
            players.push(player6);
        }
        
        if (player7 === "") {
            player8 = "";
        } else {
            players.push(player7);

            if (player8 != "") {
                players.push(player8);
            }
        }  
        
    }

</script>

<svelte:head>
  <title>Sabacc: Host</title>
</svelte:head>

<h2>Host a game of {game_variant_string} Sabacc</h2>
<br>
<h5>Who would you like to play {game_variant_string} Sabacc with? Enter your opponent's username.</h5>

<form method="POST" use:enhance>
    <input bind:value={player2} on:input={refresh} autocomplete="off" autofocus class="form-control form-group" id="player2" name="player2" placeholder="Player 2" type="text" required>
    {#if player2 != ""}
        <input bind:value={player3} on:input={refresh} autocomplete="off" class="form-control form-group" id="player3" name="player3" placeholder="Player 3" type="text">
    {/if}
    {#if player3 != ""}
        <input bind:value={player4} on:input={refresh} autocomplete="off" class="form-control form-group" id="player4" name="player4" placeholder="Player 4" type="text">
    {/if}
    {#if player4 != ""}
        <input bind:value={player5} on:input={refresh} autocomplete="off" class="form-control form-group" id="player5" name="player5" placeholder="Player 5" type="text">
    {/if}
    {#if player5 != ""}
        <input bind:value={player6} on:input={refresh} autocomplete="off" class="form-control form-group" id="player6" name="player6" placeholder="Player 6" type="text">
    {/if}
    {#if player6 != ""}
        <input bind:value={player7} on:input={refresh} autocomplete="off" class="form-control form-group" id="player7" name="player7" placeholder="Player 7" type="text">
    {/if}
    {#if player7 != ""}
        <input bind:value={player8} on:input={refresh} autocomplete="off" class="form-control form-group" id="player8" name="player8" placeholder="Player 8" type="text">
    {/if}
    <br>
    <button class="btn btn-primary" type="submit">Play</button>
</form>

<p>{errorMsg || ""}</p>
