<script lang="ts">
    let startingChips: number = 8;
    let playersChooseShiftTokens: boolean = false;
</script>

<h5>Game Settings</h5>

<br>

<table class="game-settings-table">
    <tr>
        <th colspan="2" class="text-center">General</th>
    </tr>
    <tr>
        <td>Starting Chips</td>
        <td><input bind:value={startingChips} name="startingChips" placeholder="Starting Chips" type="number" min="1" max="1000000" step="1" required></td>
    </tr>
    <tr>
        <th colspan="2" class="text-center">Players Choose Their Own Shift Tokens
            <label class="switch child">
                <input bind:checked={playersChooseShiftTokens} name="playersChooseShiftTokens" type="checkbox">
                <span class="slider round"></span>
            </label>
        </th>
    </tr>
</table>