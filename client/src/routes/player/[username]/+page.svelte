<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    
    /** @type {import('./$types').PageData} */
    export let data;
    $: playerData = data.playerData;
    $: username = $page.params.username;
    
    // Game data arrays
    $: traditionalGames = playerData?.games?.traditional || [];
    $: corellianSpikeGames = playerData?.games?.corellianSpike || [];
    $: kesselGames = playerData?.games?.kessel || [];

    let loading = true;
    let chartCanvas: HTMLCanvasElement;
    let Chart: any;
    let selectedTimeRange = 'month';
    let chart: any;
    
    // Search and filter functionality (similar to index page)
    let sortReverse = true;
    let sortType = 'id';
    let showOnlyActive = false;
    let showCompleted = false;
    let showOnlyMyTurn = false;
    let searchValue = '';

    onMount(async () => {
        loading = false;
        
        // Dynamically import Chart.js to avoid SSR issues
        const chartModule = await import('chart.js/auto');
        Chart = chartModule.default;
        
        console.log('Player data:', playerData);
        
        // Create chart after ensuring everything is loaded
        if (playerData && playerData.gameHistory && chartCanvas) {
            createChart();
        }
    });
    
    function onTimeRangeChange() {
        // Recreate chart with new time range data
        if (chart && playerData && playerData.gameHistory) {
            createChart();
        }
    }
    
    function createChart() {
        if (!chartCanvas || !Chart) {
            console.error('Missing requirements:', { chartCanvas: !!chartCanvas, Chart: !!Chart });
            return;
        }
        
        const ctx = chartCanvas.getContext('2d');
        if (!ctx) {
            console.error('Could not get 2D context');
            return;
        }
        
        // Check if we have data for the selected time range
        if (!playerData?.gameHistory?.[selectedTimeRange]) {
            console.warn('No game history data for range:', selectedTimeRange);
            return;
        }
        
        const currentData = playerData.gameHistory[selectedTimeRange];
        console.log('Creating chart with data for', selectedTimeRange, ':', currentData);
        
        // Destroy existing chart if it exists
        if (chart) {
            chart.destroy();
        }
        
        const getChartTitle = (timeRange: string) => {
            switch(timeRange) {
                case 'week': return 'Games Played Over Time (Last 7 Days)';
                case 'month': return 'Games Played Over Time (Last 30 Days)';
                case 'year': return 'Games Played Over Time (Last 12 Months)';
                case 'lifetime': return 'Games Played Over Time (Lifetime)';
                default: return 'Games Played Over Time';
            }
        };

        try {
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: currentData.dates || [],
                    datasets: [
                        {
                            label: 'Total',
                            data: currentData.total || [],
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.1)',
                            borderWidth: 3,
                            tension: 0.1
                        },
                        {
                            label: 'Traditional',
                            data: currentData.traditional || [],
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            tension: 0.1
                        },
                        {
                            label: 'Corellian Spike',
                            data: currentData.corellianSpike || [],
                            borderColor: 'rgb(75, 192, 75)',
                            backgroundColor: 'rgba(75, 192, 75, 0.1)',
                            tension: 0.1
                        },
                        {
                            label: 'Kessel',
                            data: currentData.kessel || [],
                            borderColor: 'rgb(255, 206, 86)',
                            backgroundColor: 'rgba(255, 206, 86, 0.1)',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: getChartTitle(selectedTimeRange),
                            font: {
                                size: 16
                            }
                        },
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    }
                }
            });
            console.log('Chart created successfully for', selectedTimeRange);
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    }
    
    // Game filtering and sorting functions (from index page)
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
        if (!canShowCompleted && game["completed"] === true){
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
                game["player_turn"].toLowerCase().includes(searchValue.toLowerCase()) ||
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
    
    // Reactive sorting
    $: {
        traditionalGames = traditionalGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(false, a, b, "id"));
        corellianSpikeGames = corellianSpikeGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(false, a, b, "id"));
        kesselGames = kesselGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(false, a, b, "id"));

        traditionalGames = traditionalGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(sortReverse, a, b, sortType));
        corellianSpikeGames = corellianSpikeGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(sortReverse, a, b, sortType));
        kesselGames = kesselGames.sort((a: {[id: string]: any}, b: {[id: string]: any}) => gameSortEval(sortReverse, a, b, sortType));
    }
</script>

<svelte:head>
    <title>Sabacc: Player {username}</title>
</svelte:head>

{#if loading}
    <p>Loading player information...</p>
{:else if playerData}
    <div class="player-container">
        <h2>Player Profile: {username}</h2>
        
        <div class="player-section">
            <h3>Basic Information</h3>
            <table>
                <tr>
                    <th>Information</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Username</td>
                    <td>{playerData?.username || username}</td>
                </tr>
                {#if playerData?.dateJoined}
                    <tr>
                        <td>Date Joined</td>
                        <td>{new Date(playerData.dateJoined).toDateString()}</td>
                    </tr>
                {/if}
                <tr>
                    <td>Total Games Played</td>
                    <td>{playerData?.totalGamesPlayed || 0}</td>
                </tr>
                <tr>
                    <td>Games Completed</td>
                    <td>{playerData?.gamesCompleted || 0}</td>
                </tr>
            </table>
        </div>

        <div class="player-section">
            <h3>Performance Statistics</h3>
            <table>
                <tr>
                    <th>Game Type</th>
                    <th>Games Played</th>
                    <th>Games Completed</th>
                    <th>Avg Payout</th>
                </tr>
                <tr>
                    <td><strong>Overall</strong></td>
                    <td>{playerData.totalGamesPlayed || 0}</td>
                    <td>{playerData.gamesCompleted || 0}</td>
                    <td>{playerData.overallAvgPayout != null ? playerData.overallAvgPayout.toFixed(1) + '%' : 'N/A'}</td>
                </tr>
                <tr>
                    <td>Traditional</td>
                    <td>{playerData.traditionalGamesPlayed || 0}</td>
                    <td>{playerData.traditionalGamesCompleted || 0}</td>
                    <td>{playerData.traditionalAvgPayout != null ? playerData.traditionalAvgPayout.toFixed(1) + '%' : 'N/A'}</td>
                </tr>
                <tr>
                    <td>Corellian Spike</td>
                    <td>{playerData.corellianSpikeGamesPlayed || 0}</td>
                    <td>{playerData.corellianSpikeGamesCompleted || 0}</td>
                    <td>{playerData.corellianSpikeAvgPayout != null ? playerData.corellianSpikeAvgPayout.toFixed(1) + '%' : 'N/A'}</td>
                </tr>
                <tr>
                    <td>Kessel</td>
                    <td>{playerData.kesselGamesPlayed || 0}</td>
                    <td>{playerData.kesselGamesCompleted || 0}</td>
                    <td>{playerData.kesselAvgPayout != null ? playerData.kesselAvgPayout.toFixed(1) + '%' : 'N/A'}</td>
                </tr>
            </table>
        </div>

        <div class="player-section chart-section">
            <div class="chart-header">
                <h3>Game History Timeline</h3>
                <div class="time-range-selector">
                    <label for="timeRange">Time Range:</label>
                    <select bind:value={selectedTimeRange} on:change={onTimeRangeChange} id="timeRange">
                        <option value="week">Last 7 Days</option>
                        <option value="month">Last 30 Days</option>
                        <option value="year">Last 12 Months</option>
                        <option value="lifetime">Lifetime</option>
                    </select>
                </div>
            </div>
            {#if playerData.gameHistory}
                <div class="chart-container">
                    <canvas bind:this={chartCanvas} width="800" height="400"></canvas>
                </div>
            {:else}
                <p>No game history data available.</p>
            {/if}
        </div>

        <div class="player-section">
            <h3>Game History</h3>
            
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
                    <label for="myTurn">only show games where it's {username}'s turn</label>
                </div>
            </div>

            <br>
            <h4>Traditional Games</h4>
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
                            <td>{game["player_turn"]}</td>
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
            <h4>Corellian Spike Games</h4>
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
                            <td>{game["player_turn"]}</td>
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
            <h4>Kessel Games</h4>
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
                            <td>{game["player_turn"]}</td>
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
        </div>
    </div>
{:else}
    <div class="player-container">
        <h2>Player Not Found</h2>
        <p>No player found with username: <strong>{username}</strong></p>
    </div>
{/if}

<style>
    .player-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }

    .player-section {
        margin-bottom: 40px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 8px;
    }


    h2 {
        margin-bottom: 30px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 10px;
    }

    h3 {
        margin-bottom: 20px;
    }

    .chart-container {
        position: relative;
        height: 400px;
        width: 100%;
        margin-top: 20px;
    }

    .chart-section {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 8px;
    }

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 10px;
    }

    .time-range-selector {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .time-range-selector label {
        font-weight: bold;
        font-size: 14px;
    }

    .time-range-selector select {
        padding: 6px 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        background-color: rgba(255, 255, 255, 0.1);
        color: inherit;
        font-size: 14px;
        cursor: pointer;
    }

    .time-range-selector select:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }

    .time-range-selector select:focus {
        outline: none;
        border-color: rgba(255, 255, 255, 0.4);
        background-color: rgba(255, 255, 255, 0.15);
    }
</style>