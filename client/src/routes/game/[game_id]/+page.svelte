<script lang="ts">
    import { page } from '$app/stores';

    import { checkLogin, customRedirect } from '$lib';
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let loggedIn = false;

    let errorMsg = "";

    // Accessing the 'username' parameter from the URL
    $: game_id = $page.params.game_id;

    let game = {};
    let players: any[] = [];
    let user_id = -1;

    onMount(async() => {

        loggedIn = await checkLogin(username, password, BACKEND_URL);
        if (!loggedIn) {
            customRedirect(FRONTEND_URL + "/login");
        }

        try {

            let requestData = {
                "username": username,
                "password": password
            }

            const response = await fetch(BACKEND_URL + "/game/" + game_id, {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });

            let res = await response.json();
            if (response.ok) {
                game = res["game"];
                players = res["users"];
                user_id = res["user_id"]
            }
            errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }
    });


</script>

<h1 id="psHeader"></h1>
<h2 id="phase"></h2>

<div id="tableCont">
    <div id="table"></div>
    <h2 id="pAction">{game["p_act"]}</h2>
    <div id="gameInfo" class="parent">

        <div id="pots" class="child">
            <h5>Sabacc: <span id="sabacc_pot">{game["sabacc_pot"]}</span></h5>
            <h5>Hand: <span id="hand_pot">{game["hand_pot"]}</span></h5>
        </div>

        <div id="deck" class="card child">
        </div>

        <div id="discard" class="card child">
            <button type="button" id="tradeBtn" class="btn btn-primary smol">Trade</button>
            <br>
            <button type="button" id="standBtn" class="btn btn-primary smol">Stand</button>
        </div>

        <div id="dieOne" class="child die"></div>

        <div id="dieTwo" class="child die"></div>

        <div id="alderaan" class="child alderaan"></div>

    </div>
    {#each players as p, i}

        <div id="{players[i]}Stuff" class="parent player{i}"></div>

    {/each}

    <div id="actBox"></div>
</div>