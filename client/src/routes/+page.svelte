<script lang="ts">

    import { onMount } from 'svelte';

    /** @type {import('./$types').PageData} */
	export let data;
    $: loggedIn = data.loggedIn;
    $: username = data.username;
    $: dark = data.dark;
    $: cardDesign = data.cardDesign;
    $: theme = data.theme;
    $: gamesData = data.gamesData;

    // let gamesData: {[id:string] : any} = {
    //     "traditional_games": [],
    //     "traditional_player_turn_usernames": [],
    //     "corellian_spike_games": [],
    //     "corellian_spike_player_turn_usernames": []
    // };

    let vidX = 420;

    let viewportProbe: undefined|HTMLElement = undefined;

    onMount( async () => {
        viewportProbe = document.getElementById('viewportProbe')!;
        let viewportSize = [viewportProbe?.clientWidth, viewportProbe?.clientHeight];
        console.log(viewportSize);
        if (viewportSize[0] < 560){
            vidX = viewportSize[0] - 120;
        }
    });

</script>

<svelte:head>
  <title>Sabacc: Home</title>
</svelte:head>

{#if loggedIn === false}

    <h2>Sabacc</h2>
    <p>Step into the thrilling universe of Sabacc - the iconic space card game. Test your luck and skill as you navigate shifting card values in a race to achieve the coveted hand with a value of 23. Play for fortunes, strategize your moves, and experience the excitement of Sabacc like never before. Welcome to the ultimate online Sabacc destination, where the cards are your allies and the stakes are high. <b>Log In</b> or <b>Register</b> to play!</p>

    <div class="parent">
        <div class="child video vidOne">
            <iframe width="{vidX}" height="235" src="https://www.youtube.com/embed/ZjGsiEtmU-w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            <p>Or read <a target="_blank"href="https://hyperspaceprops.com/wp-content/uploads/2021/11/Rebels-Inspired-Sabacc-Deck-Rules.pdf">this</a> for a comprehensive rulebook.</p>
        </div>

        <div class="child video">
            <p>Learn more about this web application:</p>
            <iframe width="{vidX}" height="235" src="https://www.youtube.com/embed/tgRam9fhVJQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        </div>

        <div class="child video vidOne">
            <iframe width="{vidX}" height="235" src="https://www.youtube.com/embed/T4V_vwR2pnw?autoplay=1&mute=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
            <p>⠀</p>
        </div>
    </div>

{:else if loggedIn}

    <h2>Your Active Games</h2>
    <br>
    <h3>Traditional Games</h3>
    <br>
    <table>
        <tr>
            <th>Players</th>
            <th>Turn</th>
            <th>Game Link</th>
        </tr>

        {#each gamesData["traditional_games"] || [] as game, i}

            <tr>
                <td>
                    {#each game["players"] as player, j}
                        {player["username"]}{#if j+1 < game["players"].length},&nbsp;{/if}
                    {/each}
                </td>
                <td>{gamesData["traditional_player_turn_usernames"][i]}'s</td>
                <td><a href="/game/traditional/{game["id"]}">Play</a></td>
            </tr>

        {/each}

    </table>

    <br>
    <h3>Corellian Spike Games</h3>
    <br>
    <table>
        <tr>
            <th>Players</th>
            <th>Turn</th>
            <th>Game Link</th>
        </tr>

        {#each gamesData["corellian_spike_games"] || [] as game, i}

            <tr>
                <td>
                    {#each game["players"] as player, j}
                        {player["username"]}{#if j+1 < game["players"].length},&nbsp;{/if}
                    {/each}
                </td>
                <td>{gamesData["corellian_spike_player_turn_usernames"][i]}'s</td>
                <td><a href="/game/corellian-spike/{game["id"]}">Play</a></td>
            </tr>

        {/each}

    </table>

    

{/if}

<div id="viewportProbe" style="z-index: -1; position: absolute; top: 0px; left: 0px; height: 100%; width: 100%;"></div> <!-- it will always be the same size as the viewport -->
