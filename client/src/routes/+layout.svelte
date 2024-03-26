
<script lang="ts"> 

    import Cookies from 'js-cookie'
    import { onMount } from 'svelte';
    import { checkLogin } from '$lib/index.js';

    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    let loggedIn = false;
    let username = Cookies.get("username");
    let password = Cookies.get("password");
    let dark = Cookies.get("dark");
    let theme = Cookies.get("theme");

    onMount( async () => {
        loggedIn = await checkLogin(username, password, BACKEND_URL);
    });


</script>

<html lang="en">

    <head>

        <meta charset="utf-8">
        <meta name="viewport" content="initial-scale=1, width=device-width">
        <meta name="description" content="Play Sabacc!"/>

        <!-- http://getbootstrap.com/docs/4.5/ -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">

        <!-- http://getbootstrap.com/docs/4.5/ -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous"></script>

        <!-- Favicon -->
        <link href="favicon.png" rel="icon">

        <!-- General CSS -->
        <link href="styles.css" rel="stylesheet">

        {#if loggedIn === true}
            {#if dark === true}
                <!-- Light/Dark mode -->
                <link href="dark.css" rel="stylesheet">
            {/if}

            {#if theme != undefined}
                <!-- Theme -->
                <link href="{theme}.css" rel="stylesheet">
            {/if}
        {/if}

        <title>Sabacc: <slot name="title"></slot></title>

    </head>

    <body>

        <nav class="navbar navbar-expand-md navbar-light bg-light border">
            <a class="navbar-brand" href="/"><span class="blue">Sabacc</span></a>
            <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-target="#navbar" data-toggle="collapse" type="button">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbar">
                {#if loggedIn}
                    <ul class="navbar-nav mr-auto mt-2">
                        <li class="nav-item"><a class="nav-link" href="/host">Host a Game</a></li>
                        <li class="nav-item"><a class="nav-link" href="/chat">GalactiChat</a></li>
                    </ul>
                    <ul class="navbar-nav ml-auto mt-2">
                        <li class="nav-item"><a class="nav-link" href="/settings">Settings</a></li>
                        <li class="nav-item"><a class="nav-link" href="/logout">Log Out</a></li>
                    </ul>
                {:else}
                    <ul class="navbar-nav ml-auto mt-2">
                        <li class="nav-item"><a class="nav-link" href="/register">Register</a></li>
                        <li class="nav-item"><a class="nav-link" href="/login">Log In</a></li>
                    </ul>
                {/if}
            </div>
        </nav>

        <main class="container p-5">
            <slot></slot>
        </main>

    </body>

</html>
