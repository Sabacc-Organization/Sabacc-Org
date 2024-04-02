<script lang="ts">
  import { checkLogin, customRedirect } from '$lib';


    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let loggedIn = false;
    let dark: boolean | string = Cookies.get("dark");
    if (dark === "true") {
        dark = true;
    }
    else if (dark === "false") {
        dark = false;
    }
    let theme = Cookies.get("theme");

    onMount(async() => {

        loggedIn = await checkLogin(username, password, BACKEND_URL);
        if (!loggedIn) {
            customRedirect(FRONTEND_URL + "/login");
        }

    });

    function save() {
        if (dark) {
            Cookies.set("dark", "true", {"expires": 30});
        }
        else {
            Cookies.set("dark", "false", {"expires": 30});
        }

        Cookies.set("theme", theme, {"expires": 30});

        customRedirect(FRONTEND_URL + "/");
    }


</script>

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

<label for="theme">Theme (Work in Progress)</label>

<select bind:value={theme} name="theme" id="theme">
    <option value="rebels">Rebels</option>
    <option value="solo">Solo</option>
    <option value="classic">Classic</option>
</select>

<br>

<br>
<button on:click={save} type="button" class="btn btn-primary">Save</button>