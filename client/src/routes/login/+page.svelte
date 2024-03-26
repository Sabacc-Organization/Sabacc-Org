<script lang="ts">
    import { goto } from '$app/navigation';
    import Cookies from 'js-cookie';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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
                Cookies.set("username", res["username"], {"expires": 30});
                Cookies.set("password", res["password"], {"expires": 30});
                Cookies.set("dark", false, {"expires": 30});
                Cookies.set("theme", "rebels", {"expires": 30});
                goto("/");
            }
            errorMsg = res["message"];
        } catch (e) {
            console.log(e);
        }
    }
  </script>
  
  <h1>Login</h1>
  

<div>
    <label for="username">Username</label>
    <input bind:value={username} id="username" name="username" type="text" required />
</div>

<div>
    <label for="password">Password</label>
    <input bind:value={password} id="password" name="password" type="password" required />
</div>

<button on:click={login} type="submit">Log in</button>


<p>{errorMsg}</p>