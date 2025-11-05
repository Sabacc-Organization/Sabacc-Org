<script lang="ts">
    import { onMount } from 'svelte';
    
    /** @type {import('./$types').PageData} */
    export let data;
    $: stats = data.stats;

    let loading = true;
    let chartCanvas: HTMLCanvasElement;
    let Chart: any;
    let selectedTimeRange = 'month';
    let chart: any;
    
    // Leaderboard ranking options
    let overallRanking = 'byGames';
    let traditionalRanking = 'byGames';
    let corellianSpikeRanking = 'byGames';
    let kesselRanking = 'byGames';

    onMount(async () => {
        loading = false;
        
        // Dynamically import Chart.js to avoid SSR issues
        const chartModule = await import('chart.js/auto');
        Chart = chartModule.default;
        
        console.log('Stats data:', stats);
        console.log('Time series data:', stats?.timeSeriesData);
        
        // Create initial chart
        if (stats && stats.timeSeriesData && chartCanvas) {
            createChart();
        }
    });
    
    function onTimeRangeChange() {
        // Recreate chart with new time range data
        if (chart && stats && stats.timeSeriesData) {
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
        if (!stats?.timeSeriesData?.[selectedTimeRange]) {
            console.warn('No time series data for range:', selectedTimeRange);
            return;
        }
        
        const currentData = stats.timeSeriesData[selectedTimeRange];
        console.log('Creating chart with data for', selectedTimeRange, ':', currentData);
        
        // Destroy existing chart if it exists
        if (chart) {
            chart.destroy();
        }
        
        const getChartTitle = (timeRange: string) => {
            switch(timeRange) {
                case 'week': return 'Games Created Over Time (Last 7 Days)';
                case 'month': return 'Games Created Over Time (Last 30 Days)';
                case 'year': return 'Games Created Over Time (Last 12 Months)';
                case 'lifetime': return 'Games Created Over Time (Lifetime)';
                default: return 'Games Created Over Time';
            }
        };

        try {
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: currentData.dates || [],
                    datasets: [
                        {
                            label: 'Traditional',
                            data: currentData.traditional || [],
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.1)',
                            tension: 0.1
                        },
                        {
                            label: 'Corellian Spike',
                            data: currentData.corellianSpike || [],
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            tension: 0.1
                        },
                        {
                            label: 'Kessel',
                            data: currentData.kessel || [],
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.1)',
                            tension: 0.1
                        },
                        {
                            label: 'Total',
                            data: currentData.total || [],
                            borderColor: 'rgb(255, 206, 86)',
                            backgroundColor: 'rgba(255, 206, 86, 0.1)',
                            borderWidth: 3,
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
</script>

<svelte:head>
    <title>Sabacc: Game Stats</title>
</svelte:head>

<h2>Game Statistics</h2>

{#if loading}
    <p>Loading stats...</p>
{:else if stats}
    <div class="stats-container">
        <h3>Game Statistics</h3>
        <div class="stats-section">
            <h4>Overall Performance</h4>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Games Played</td>
                    <td>{stats.totalGames || 0}</td>
                </tr>
                <tr>
                    <td>Games Completed</td>
                    <td>{stats.gamesCompleted || 0}</td>
                </tr>
                <tr>
                    <td>Completion Rate</td>
                    <td>{stats.completionRate || '0'}%</td>
                </tr>
                <tr>
                    <td>Avg Players per Game</td>
                    <td>{stats.avgPlayersPerGame || 0}</td>
                </tr>
                <tr>
                    <td>Avg Moves per Game</td>
                    <td>{stats.avgMovesPerGame || 0}</td>
                </tr>
            </table>
        </div>

        <div class="stats-section">
            <h4>Game Type Breakdown</h4>
            <table>
                <tr>
                    <th>Game Type</th>
                    <th>Games Played</th>
                    <th>Completed</th>
                    <th>Completion Rate</th>
                    <th>Avg Players</th>
                    <th>Avg Moves</th>
                </tr>
                <tr>
                    <td>Traditional</td>
                    <td>{stats.traditionalGames || 0}</td>
                    <td>{stats.traditionalCompleted || 0}</td>
                    <td>{stats.traditionalCompletionRate || '0'}%</td>
                    <td>{stats.traditionalAvgPlayers || 0}</td>
                    <td>{stats.traditionalAvgMoves || 0}</td>
                </tr>
                <tr>
                    <td>Corellian Spike</td>
                    <td>{stats.corellianSpikeGames || 0}</td>
                    <td>{stats.corellianSpikeCompleted || 0}</td>
                    <td>{stats.corellianSpikeCompletionRate || '0'}%</td>
                    <td>{stats.corellianSpikeAvgPlayers || 0}</td>
                    <td>{stats.corellianSpikeAvgMoves || 0}</td>
                </tr>
                <tr>
                    <td>Kessel</td>
                    <td>{stats.kesselGames || 0}</td>
                    <td>{stats.kesselCompleted || 0}</td>
                    <td>{stats.kesselCompletionRate || '0'}%</td>
                    <td>{stats.kesselAvgPlayers || 0}</td>
                    <td>{stats.kesselAvgMoves || 0}</td>
                </tr>
            </table>
        </div>

        <div class="stats-section chart-section">
            <div class="chart-header">
                <h4>Game Creation Timeline</h4>
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
            {#if stats.timeSeriesData}
                <div class="chart-container">
                    <canvas bind:this={chartCanvas} width="800" height="400"></canvas>
                </div>
            {:else}
                <p>No timeline data available.</p>
            {/if}
        </div>

        <h3>Player Statistics</h3>
        
        <div class="stats-section">
            <div class="leaderboard-header">
                <h4>Overall Performance Leaderboard</h4>
                <div class="ranking-selector">
                    <label for="overallRanking">Rank by:</label>
                    <select bind:value={overallRanking} id="overallRanking">
                        <option value="byPayout">Average Payout</option>
                        <option value="byGames">Games Played</option>
                    </select>
                </div>
            </div>
            {#if stats.leaderboards?.overall?.[overallRanking]}
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Avg Payout</th>
                        <th>Games Played</th>
                    </tr>
                    {#each stats.leaderboards.overall[overallRanking] as player, index}
                        <tr>
                            <td>{index + 1}</td>
                            <td>{player.username}</td>
                            <td>{player.avgPayout.toFixed(1)}%</td>
                            <td>{player.gamesPlayed}</td>
                        </tr>
                    {/each}
                </table>
            {:else}
                <p>No player data available.</p>
            {/if}
        </div>

        <div class="stats-section">
            <div class="leaderboard-header">
                <h4>Traditional Games Leaderboard</h4>
                <div class="ranking-selector">
                    <label for="traditionalRanking">Rank by:</label>
                    <select bind:value={traditionalRanking} id="traditionalRanking">
                        <option value="byPayout">Average Payout</option>
                        <option value="byGames">Games Played</option>
                    </select>
                </div>
            </div>
            {#if stats.leaderboards?.traditional?.[traditionalRanking]}
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Avg Payout</th>
                        <th>Games Played</th>
                    </tr>
                    {#each stats.leaderboards.traditional[traditionalRanking] as player, index}
                        <tr>
                            <td>{index + 1}</td>
                            <td>{player.username}</td>
                            <td>{player.avgPayout.toFixed(1)}%</td>
                            <td>{player.gamesPlayed}</td>
                        </tr>
                    {/each}
                </table>
            {:else}
                <p>No traditional game data available.</p>
            {/if}
        </div>

        <div class="stats-section">
            <div class="leaderboard-header">
                <h4>Corellian Spike Games Leaderboard</h4>
                <div class="ranking-selector">
                    <label for="corellianSpikeRanking">Rank by:</label>
                    <select bind:value={corellianSpikeRanking} id="corellianSpikeRanking">
                        <option value="byPayout">Average Payout</option>
                        <option value="byGames">Games Played</option>
                    </select>
                </div>
            </div>
            {#if stats.leaderboards?.corellianSpike?.[corellianSpikeRanking]}
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Avg Payout</th>
                        <th>Games Played</th>
                    </tr>
                    {#each stats.leaderboards.corellianSpike[corellianSpikeRanking] as player, index}
                        <tr>
                            <td>{index + 1}</td>
                            <td>{player.username}</td>
                            <td>{player.avgPayout.toFixed(1)}%</td>
                            <td>{player.gamesPlayed}</td>
                        </tr>
                    {/each}
                </table>
            {:else}
                <p>No Corellian Spike game data available.</p>
            {/if}
        </div>

        <div class="stats-section">
            <div class="leaderboard-header">
                <h4>Kessel Games Leaderboard</h4>
                <div class="ranking-selector">
                    <label for="kesselRanking">Rank by:</label>
                    <select bind:value={kesselRanking} id="kesselRanking">
                        <option value="byPayout">Average Payout</option>
                        <option value="byGames">Games Played</option>
                    </select>
                </div>
            </div>
            {#if stats.leaderboards?.kessel?.[kesselRanking]}
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Avg Payout</th>
                        <th>Games Played</th>
                    </tr>
                    {#each stats.leaderboards.kessel[kesselRanking] as player, index}
                        <tr>
                            <td>{index + 1}</td>
                            <td>{player.username}</td>
                            <td>{player.avgPayout.toFixed(1)}%</td>
                            <td>{player.gamesPlayed}</td>
                        </tr>
                    {/each}
                </table>
            {:else}
                <p>No Kessel game data available.</p>
            {/if}
        </div>
    </div>
{:else}
    <p>No statistics available at this time.</p>
{/if}

<style>
    .stats-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }

    .stats-section {
        margin-bottom: 40px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 8px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }

    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    th {
        font-weight: bold;
        background-color: rgba(255, 255, 255, 0.05);
    }

    tr:hover {
        background-color: rgba(255, 255, 255, 0.02);
    }

    h3 {
        margin-bottom: 20px;
    }

    h4 {
        margin-bottom: 10px;
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

    .leaderboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 10px;
    }

    .ranking-selector {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .ranking-selector label {
        font-weight: bold;
        font-size: 14px;
    }

    .ranking-selector select {
        padding: 6px 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        background-color: rgba(255, 255, 255, 0.1);
        color: inherit;
        font-size: 14px;
        cursor: pointer;
    }

    .ranking-selector select:hover {
        background-color: rgba(255, 255, 255, 0.15);
    }

    .ranking-selector select:focus {
        outline: none;
        border-color: rgba(255, 255, 255, 0.4);
        background-color: rgba(255, 255, 255, 0.15);
    }
</style>