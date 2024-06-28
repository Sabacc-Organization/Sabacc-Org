<script lang="ts">
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
                Cookies.set("PASSWORD", password, {"expires": 30});
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
  

<div>
    <input bind:value={username} autocomplete="off" class="form-control form-group" name="username" placeholder="Username" type="text" required/>
</div>

<div>
    <input bind:value={password} class="form-control form-group" name="password" placeholder="Password" type="password" required/>
</div>

<button on:click={login} class="btn btn-primary" type="submit">Log in</button>


<p>{errorMsg}</p>