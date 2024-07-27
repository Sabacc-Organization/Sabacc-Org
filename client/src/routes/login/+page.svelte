<script lang="ts">
    import { enhance } from '$app/forms';
    import { customRedirect } from '$lib';
    import Cookies from 'js-cookie';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    let username = "";
    let password = "";

    let errorMsg = "";

    Cookies.remove("username");
    Cookies.remove("password");

    async function login() {

        try {

            let requestData = {
                "username": username,
                "password": password
            }

            const response = await fetch(BACKEND_URL + "/login", {
                method: 'POST', // Set the method to POST
                headers: {
                    'Content-Type': 'application/json' // Set the headers appropriately
                },
                body: JSON.stringify(requestData) // Convert your data to JSON
            });

            let res = await response.json();
            if (response.ok) {
                Cookies.set("username", username, {"expires": 30});
                Cookies.set("password", password, {"expires": 30});
                Cookies.set("dark", "false", {"expires": 30});
                Cookies.set("theme", "modern", {"expires": 30});
                Cookies.set("cardDesign", "auto", {"expires": 30});
                customRedirect(FRONTEND_URL);
            }
            errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }
    }
</script>

<svelte:head>
  <title>Sabacc: Login</title>
</svelte:head>
  
<h1>Login</h1>

<h1>Login</h1>

<form method="POST" use:enhance>
    <input bind:value={username} type="text" class="form-control form-group" name="username" placeholder="Username" autocomplete="off" required>
    <br>
    <input bind:value={password} type="password" class="form-control form-group" name="password" placeholder="Password" autocomplete="off" required>
    <br>
    <button type="submit" class="btn btn-primary">Login</button>
</form>

<p>{errorMsg}</p>
