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

    let traditionalGames: {[id: string]: any}[] = [];
    let corellianSpikeGames: {[id: string]: any}[] = [];
    let kesselGames: {[id: string]: any}[] = [];

    $: {
        if (gamesData != undefined){
            traditionalGames = gamesZip(gamesData["traditional_games"], gamesData["traditional_player_turn_usernames"]);
            corellianSpikeGames = gamesZip(gamesData["corellian_spike_games"], gamesData["corellian_spike_player_turn_usernames"]);
            kesselGames = gamesZip(gamesData["kessel_games"], gamesData["kessel_player_turn_usernames"])
        }
    }

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
        // console.log(viewportSize);
        if (viewportSize[0] < 560){
            vidX = viewportSize[0] - 120;
        }
    });

    function gamesZip(listA: {[id: string]: any}[], listB: any[]){
        let minListLen = Math.min(listA.length, listB.length);
        let outputList = [... listA];

        for (let i = 0; i < minListLen; i++){
            outputList[i]["player_turn"] = listB[i];
        }
        return outputList;
    }

    function gameSortEval(descending: boolean, valueA: {[id: string]: any}, valueB: {[id: string]: any}, sortType: string){
        let answer = 0;
        if (sortType === "id"){
            answer = valueA["id"] - valueB["id"];
        } else if (sortType === "numOfPlayers"){
            answer = valueA["players"].length - valueB["players"].length;
        } else if (sortType === "playerTurn"){
            answer = valueA["player_turn"].localeCompare(valueB["player_turn"]);
        } else if (sortType === "created"){
            let crA = new Date(valueA["created_at"]);
            let crB = new Date(valueB["created_at"]);
            answer = crB.getTime() - crA.getTime();
        } else if (sortType === "lastMove"){
            let lmA: Date;
            let lmB: Date;

            if (valueA["move_history"] != null){
                lmA = new Date(valueA["move_history"].at(-1)["timestamp"]);
            } else {
                lmA = new Date(valueA["created_at"]);
            }

            if (valueB["move_history"] != null){
                lmB = new Date(valueB["move_history"].at(-1)["timestamp"]);
            } else {
                lmB = new Date(valueB["created_at"]);
            }

            answer = lmB.getTime() - lmA.getTime();
        }

        if (descending){
            return -1 * answer;
        }
        return answer;
    }

    function canShowGame(game: {[id: string]: any}, showOnlyActive: boolean, canShowCompleted: boolean, showOnlyMyTurn: boolean, searchValue: string){
        let answer = true;
        if (!canShowCompleted && game["completed"]){
            answer = false;
        }

        if (showOnlyActive === true){
            let gameLM: Date;
            if (game["move_history"] != null){
                gameLM = new Date(game["move_history"][-1])
            } else {
                gameLM = new Date(Date.now())
            }

            if (Date.now() - gameLM.getTime() > 1.728e+8){
                answer = false
            }
        }

        if (showOnlyMyTurn === true && game["player_turn"] != username){
            answer = false
        }

        let isSearched = true;
        if (searchValue != ""){
            isSearched = false;
            if (
                String(game["id"]).toLowerCase().includes(searchValue.toLowerCase()) ||
                game["phase"].toLowerCase().includes(searchValue.toLowerCase()) ||
                game["p_act"].toLowerCase().includes(searchValue.toLowerCase())
            ){
                isSearched = true;
            }
            for (let i = 0; i < game["players"].length; i++){
                if (game["players"][i]["username"].toLowerCase().includes(searchValue.toLowerCase())){
                    isSearched = true
                    break
                }
            }
        }

        return (answer && isSearched);
    }

    let sortReverse = false;
    let sortType = 'id';
    let showOnlyActive = false;
    let showCompleted = false;
    let showOnlyMyTurn = false;
    let searchValue = '';

    $: {
        traditionalGames = traditionalGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(false, a, b, "id"));
        corellianSpikeGames = corellianSpikeGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(false, a, b, "id"));

        traditionalGames = traditionalGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(sortReverse, a, b, sortType));
        corellianSpikeGames = corellianSpikeGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(sortReverse, a, b, sortType));
    }

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

    <div class="sort-search-filter">
        <div class="searchContainer">
            <h4>Search</h4>
            <input bind:value={searchValue} type="text" name="search" id="searchBar" placeholder="Search">
        </div>
        <div class="sortContainer">
            <h4>Sort</h4>
            <label for="sort">sort by</label>
            <select bind:value={sortType} name="sort" id="sortDropdown">
                <option value="id">id</option>
                <option value="playerTurn">player turn</option>
                <option value="numOfPlayers">number of players</option>
                <option value="lastMove">time since last move</option>
                <option value="created">time since creation</option>
            </select>
            <button on:click={() => {sortReverse = !sortReverse}}>{sortReverse? "▼":"▲"}</button>
        </div>
        <div class="filterContainer">
            <h4>Filter</h4>
            <input bind:checked={showOnlyActive} type="checkbox" name="inactiveGames">
            <label for="inactiveGames">only show active games</label>
            <br>

            <input bind:checked={showCompleted} type="checkbox" name="completedGames">
            <label for="completedGames">show completed games</label>
            <br>

            <input bind:checked={showOnlyMyTurn} type="checkbox" name="myTurn">
            <label for="myTurn">only show games where its my turn</label>
        </div>
    </div>

    <h2>Your Games</h2>
    <br>
    <h3>Traditional Games</h3>
    <br>
    <table>
        <tr>
            <th style="width: 1%;">ID</th>
            <th style="width: 8%;">Players</th>
            <th style="width: 3%;">Turn</th>
            <th style="width: 2%;">Date Created</th>
            <th style="width: 11%;">Last Move</th>
            <th style="width: 1%;">Game Link</th>
        </tr>

        {#each traditionalGames || [] as game, i}
            {#if canShowGame(game, showOnlyActive, showCompleted, showOnlyMyTurn, searchValue)}
                <tr>
                    <td>
                        {game["id"]}
                    </td>
                    <td>
                        {#each game["players"] as player, j}
                            {player["username"] + (j+1 < game["players"].length? ", ":"")}
                        {/each}
                    </td>
                    <td>{game["player_turn"]}'s</td>
                    <td>
                        {#if game["created_at"] != null}
                            {new Date(game["created_at"]).toDateString()}
                        {:else}
                            N/A
                        {/if}
                    </td>
                    <td>{game["p_act"]}
                        {#if game["move_history"] !== null}
                            {#if game["p_act"] === ""}
                                new round
                            {/if}
                            on {new Date(game["move_history"].at(-1)["timestamp"]).toDateString()}
                        {/if}
                    </td>
                    <td><a href="/game/traditional/{game["id"]}">Play</a></td>
                </tr>
            {/if}
        {/each}

    </table>

    <br>
    <h3>Corellian Spike Games</h3>
    <br>
    <table>
        <tr>
            <th style="width: 1%;">ID</th>
            <th style="width: 8%;">Players</th>
            <th style="width: 3%;">Turn</th>
            <th style="width: 2%;">Date Created</th>
            <th style="width: 11%;">Last Move</th>
            <th style="width: 1%;">Game Link</th>
        </tr>

        {#each corellianSpikeGames || [] as game, i}
            {#if canShowGame(game, showOnlyActive, showCompleted, showOnlyMyTurn, searchValue)}
                <tr>
                    <td>
                        {game["id"]}
                    </td>
                    <td>
                        {#each game["players"] as player, j}
                        {player["username"] + (j+1 < game["players"].length? ", ":"")}
                        {/each}
                    </td>
                    <td>{game["player_turn"]}'s</td>
                    <td>
                        {#if game["created_at"] != null}
                            {new Date(game["created_at"]).toDateString()}
                        {:else}
                            N/A
                        {/if}
                    </td>
                    <td>{game["p_act"]}
                        {#if game["move_history"] !== null}
                            on {new Date(game["move_history"].at(-1)["timestamp"]).toDateString()}
                        {/if}
                    </td>
                    <td><a href="/game/corellian-spike/{game["id"]}">Play</a></td>
                </tr>
            {/if}
        {/each}
    </table>

    <br>
    <h3>Kessel Games</h3>
    <br>
    <table>
        <tr>
            <th style="width: 1%;">ID</th>
            <th style="width: 8%;">Players</th>
            <th style="width: 3%;">Turn</th>
            <th style="width: 2%;">Date Created</th>
            <th style="width: 11%;">Last Move</th>
            <th style="width: 1%;">Game Link</th>
        </tr>

        {#each kesselGames || [] as game, i}
            {#if canShowGame(game, showOnlyActive, showCompleted, showOnlyMyTurn, searchValue)}
                <tr>
                    <td>
                        {game["id"]}
                    </td>
                    <td>
                        {#each game["players"] as player, j}
                        {player["username"] + (j+1 < game["players"].length? ", ":"")}
                        {/each}
                    </td>
                    <td>{game["player_turn"]}'s</td>
                    <td>
                        {#if game["created_at"] != null}
                            {new Date(game["created_at"]).toDateString()}
                        {:else}
                            N/A
                        {/if}
                    </td>
                    <td>{game["p_act"]}
                        {#if game["move_history"] !== null}
                            on {new Date(game["move_history"].at(-1)["timestamp"]).toDateString()}
                        {/if}
                    </td>
                    <td><a href="/game/kessel/{game["id"]}">Play</a></td>
                </tr>
            {/if}
        {/each}
    </table>
{/if}

<div id="viewportProbe" style="z-index: -1; position: absolute; top: 0px; left: 0px; height: 100%; width: 100%;"></div> <!-- it will always be the same size as the viewport -->
