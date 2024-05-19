<script lang="ts">
  import { checkLogin, customRedirect } from '$lib';


    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let loggedIn = false;

    let dark: boolean | string | undefined = Cookies.get("dark");
    dark = (dark == "true");

    let theme = Cookies.get("theme");
    if (theme == undefined){
        theme = "modern"
    }
    let cardDesign = Cookies.get("cardDesign");
    if (cardDesign == undefined){
        cardDesign = "auto"
    }

    onMount(async() => {

        loggedIn = await checkLogin(username, password, BACKEND_URL);
        if (!loggedIn) {
            customRedirect(FRONTEND_URL + "/login");
        }

    });

    function save() {
        Cookies.set("dark", dark? "true":"false", {"expires": 30});

        Cookies.set("cardDesign", cardDesign, {"expires": 30});

        Cookies.set("theme", theme, {"expires": 30});

        customRedirect(FRONTEND_URL + "/");
    }


</script>

<svelte:head>
  <title>Sabacc: Settings</title>
</svelte:head>

<h2>Settings</h2>
<br>

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

<label for="theme">Theme (Work in Progress)</label>

<select bind:value={theme} name="theme" id="theme">
    <option value="modern">Modern</option>
    <option value="rebels">Rebels</option>
    <option value="solo">Solo</option>
    <option value="classic">Classic</option>
</select>

<br>

<br>
<button on:click={save} type="button" class="btn btn-primary">Save</button>