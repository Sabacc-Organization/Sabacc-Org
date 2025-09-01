<script lang="ts">
    import { Socket, io } from "socket.io-client";
    import { onDestroy, onMount } from 'svelte';
    import { page } from "$app/stores";
    import {
        socket,
        turnSound,
        game,
        u_dex,
        game_variant,
        game_id,
        dataToRender,
        header,
        theme,
        username,
        password,
        dark,
        cardDesign,
        resetGameStores,
        tooltip
    } from './sharedValues'
    import {
        requestGameUpdate,
        updateClientGame,
        updateClientInfo,
        camelToSpaced
    } from './gameLogic'

    // Template Components
    import GameInfo from "./gameInfo.svelte";
    import PlayerStuff from "./playerStuff.svelte";
    import ActionBox from "./actionBox.svelte";
    import GamePlayback from "./gamePlayback.svelte";

    // Data passed from +page.svelte
    export let _game_variant: string;
    export let _username: string;
    export let _password: string;
    export let _dark: boolean;
    export let _cardDesign: string;
    export let _theme: string;

    // Updating sharedValues according to passed data
    $game_variant = _game_variant;
    $username = _username;
    $password = _password;
    $dark = _dark;
    $cardDesign = _cardDesign;
    $theme = _theme;

    //cards are handled differently on different versions, so I export them to let each version decide for itself what to do.
    export let renderCard;
    export let renderBack;

    // URLs for Requests and Redirects
    export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    export const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    let xMousePos = 0
    let yMousePos = 0

    // Once page is mounted
    onMount(() => {
        onmousemove = (event) => {
            xMousePos = event.pageX;
            yMousePos = window.innerHeight - event.pageY;
        }

        // defines a new socket object for real-time communication with server
        $socket = io(BACKEND_URL);

        // code to catch errors
        $socket.io.on('error', (err: any) => {console.log(err)});

        // when there is a connection established with the server, it will explicitely ask the server for a game update. 
        // this is the only time it will explicitly ask for a game update.
        $socket.on('connect', () => {
            requestGameUpdate();
        });

        // when the server responds to a game update request or recieves new information, it will pass that info on to updateClientGame as serverInfo
        $socket.on('gameUpdate', (serverInfo: any) => {
            updateClientGame(serverInfo);
        });

        // sometimes the server wants to give the client information that only applies to them, such as their user ID.
        // clientUpdate is accessed when the server doesnt want to give that info to every client. it also give the updated game in serverInfo
        // updateClientGame is called within updateClientInfo. updateClientInfo is only called when first logging on.
        $socket.on('clientUpdate', (serverInfo: any) => {
            updateClientInfo(serverInfo);
        });

        // defining the Audio to be play apon your turn (it wouldnt work if i put it outside of onMount)
        $turnSound = new Audio("/move-sound.mp3");
    });

    onDestroy(() => {
        if ($socket) {
            $socket.disconnect();
            console.log('Chewie removed your connection from its socket');
            resetGameStores();
        }
    });
</script>

<svelte:head>
  <title>Sabacc: Game {$game_id}</title>
</svelte:head>

<link rel="stylesheet" href="/styles/main/styles-game.css">
{#if $theme === "modern"}
    <link rel="stylesheet" href="/styles/modern/modern-game.css">
    <link rel="stylesheet" href="/styles/modern/modern-players.css">
    <link rel="stylesheet" href="/styles/modern/modern-mobile.css">
    {#if $game_variant === "kessel"}
        <link rel="stylesheet" href="/styles/modern/modern-kessel.css">
    {/if}
{:else}
    <h3 style:color="red">You are using a theme that is no longer supported!</h3>
    <h3>Please go to <a href="/settings">Settings</a> to change your theme</h3>
    <br>
    <br>
{/if}

{#if $dataToRender}
    <h1 class="header">{$header}</h1>
    <h2 class="header">round {$game["cycle_count"] + 1} during {camelToSpaced($game["phase"])} phase</h2>

    <div id="tableCont">
        <div id="table"></div>
        <h2 id="pAction" class:playing={$u_dex != -1}>{$game["p_act"]}</h2>
        <GameInfo {renderCard} {renderBack} />

        {#each $game["players"] as p, i}
            <PlayerStuff {p} {i} {renderCard} {renderBack}/>
        {/each}

        <ActionBox {renderCard}/>
    </div>

    {#if $game["move_history"] !== undefined && $game["move_history"] !== null}
        <GamePlayback />
    {/if}

    <br>

    <h5>Game Settings</h5>
    <table class="game-settings-display-table">
        <tr>
            <th>Setting</th>
            <th>Value</th>
        </tr>
        {#each Object.keys($game["settings"]) as key}
            <tr>
                <td>{key}</td>
                <td>{$game["settings"][key]}</td>
            </tr>
        {/each}
    </table>

    <br>

    {#if $theme == 'modern'}
        <div class="credit-attribution-container">
            <div class="credit-attribution">
                <a href="http://creativecommons.org/licenses/by-sa/4.0/"><div id="jacob-densford-credit-attribution"></div></a>
                <a href="http://creativecommons.org/licenses/by-sa/4.0/">Credit to Jacob Densford for table and betting chip design</a>
            </div>
        </div>
        <div class="mobileActSpacer"></div>
    {/if}

    <div class="tooltip-box" style="bottom: {yMousePos}px; left: {xMousePos}px; display: {$tooltip === ""? "none":"block"};">
        <p>{@html $tooltip}</p>
    </div>
{/if}
