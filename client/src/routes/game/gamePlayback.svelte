<script lang="ts">

    import {  
        game,
        currentMove,
        movesDone,
        playbackInput
    } from "./sharedValues";

    import { 
        playback_back,
        playback_forward,
        playback
    } from "./gameLogic";

    $: {
        if (($game["move_history"] !== null && $game["move_history"] !== undefined) && ($currentMove === undefined || $currentMove === null)) {
            $currentMove = $game["move_history"].length - 1;
        }
    }
</script>

<h5>Game Playback | Move {$currentMove + 1 || 0} of {$movesDone}</h5>
<h5>
    {#if $currentMove === -1}
        {new Date($game["created_at"]).toUTCString()}
    {:else}
        {new Date($game["move_history"].at($currentMove)["timestamp"]).toUTCString()}
    {/if}
</h5>
<div class="playback-buttons-container">
    <!-- Left arrow button -->
    <button on:click={playback_back} class="playback-button back-playback-arrow"></button>
    <!-- Number enter -->
    <input bind:value={$playbackInput} placeholder=". . ." class="playback-input" type="number" min="0" max={$movesDone} on:input={() => playback($playbackInput - 1)}/>
    <!-- Right arrow button -->
    <button on:click={playback_forward} class="playback-button forward-playback-arrow"></button>
</div>