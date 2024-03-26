<script lang="ts">

    import Cookies from 'js-cookie'
    import { onMount } from 'svelte';
    import { checkLogin } from '$lib/index.js';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    let loggedIn = false;
    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let dark = Cookies.get("dark");
    let theme = Cookies.get("theme");

    onMount( async () => {
        loggedIn = await checkLogin(username, password, BACKEND_URL);
    });

</script>

{#if loggedIn === false}

    <h2>Sabacc</h2>
    <p>Step into the thrilling universe of Sabacc - the iconic space card game. Test your luck and skill as you navigate shifting card values in a race to achieve the coveted hand with a value of 23. Play for fortunes, strategize your moves, and experience the excitement of Sabacc like never before. Welcome to the ultimate online Sabacc destination, where the cards are your allies and the stakes are high. <b>Log In</b> or <b>Register</b> to play!</p>
    
    <div class="parent">
        <div class="child video vidOne">
            <iframe width="420" height="235" src="https://www.youtube.com/embed/ZjGsiEtmU-w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            <p>Or read <a target="_blank"href="https://hyperspaceprops.com/wp-content/uploads/2021/11/Rebels-Inspired-Sabacc-Deck-Rules.pdf">this</a> for a comprehensive rulebook.</p>
        </div>

        <div class="child video">
            <p>Learn more about this web application:</p>
            <iframe width="420" height="235" src="https://www.youtube.com/embed/tgRam9fhVJQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        </div>
    </div>

    <iframe width="560" height="315" src="https://www.youtube.com/embed/T4V_vwR2pnw?autoplay=1&mute=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

{:else}

    <!-- <meta id="games-data" data-games="{{ games }}">
    <meta id="users-data" data-usernames="{{ usernames }}">
    <meta id="turns-data" data-turns="{{ player_turns }}">

    <h2>Your Active Games</h2>
    <br>
    <table>
        <tr>
            <th>Players</th>
            <th>Turn</th>
            <th>Game Link</th>
        </tr>

        {#each i in range(gamesLen)}

            <tr>
                <td>{{ usernames[i] }}</td>
                <td>{{ player_turns[i] }}'s</td>
                <td><a href="/game/{{ games[i]['game_id'] }}">Play</a></td>
            </tr>

        {/each}

    </table> -->

    <p>logged in</p>

{/if}