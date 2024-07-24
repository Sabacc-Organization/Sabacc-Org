<script lang="ts">
    import { enhance } from "$app/forms";
    import { onMount } from "svelte";

    export let form;

    /** @type {import('./$types').PageData} */
	export let data;
    $: loggedIn = data.loggedIn;
    $: username = data.username;
    let dark = data.dark;
    let cardDesign = data.cardDesign;
    let theme = data.theme;

    if (dark === "false") {
        dark = false;
    }


</script>

<svelte:head>
  <title>Sabacc: Settings</title>
</svelte:head>

<h2>Settings</h2>
<br>

<form method="POST" use:enhance>
    <div class="parent">
        <h5 class="child">Dark Mode</h5>
        <!-- Rounded switch -->
        <label class="switch child">
            <input bind:checked={dark} name="dark" type="checkbox">
            <span class="slider round"></span>
        </label>

    </div>

    <br>

    <label for="cardDesign">Card Design</label>

    <select bind:value={cardDesign} name="cardDesign" id="cardDesign">
        <option value="classic">Classic</option>
        <option value="auto">Auto</option>
        <option value="dark">Dark</option>
        <option value="light">Light</option>
        <option value="pescado">Pescado</option>
    </select>

    <br>

    <label for="theme">Theme</label>

    <select bind:value={theme} name="theme" id="theme">
        <option value="modern">Modern</option>
        <option value="rebels">Rebels</option>
        <option value="solo">Solo</option>
        <option value="classic">Classic</option>
    </select>
    <br>

    <br>
    <button type="submit" class="btn btn-primary">Save</button>
</form>

<p class="error"><b>{form?.error || ""}</b></p>