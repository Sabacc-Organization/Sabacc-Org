
<script lang="ts"> 

    import { page } from '$app/stores'
    import { onMount } from 'svelte';

    /** @type {import('./$types').PageData} */
	export let data;
    $: loggedIn = data.loggedIn;
    $: username = data.username;
    $: dark = data.dark;
    $: cardDesign = data.cardDesign;
    $: theme = data.theme;

    function initializeDropdown() {
        if (window.jQuery && window.jQuery.fn.dropdown) {
            window.jQuery(document).ready(() => {
                window.jQuery('.dropdown-toggle').dropdown();
        });
        }
        return '';
    }

    onMount( async () => {
        initializeDropdown();
    });

</script>

<svelte:head>
    <title>Sabacc</title>
</svelte:head>

<html lang="en">

    <head>

        <meta charset="utf-8">
        <meta name="viewport" content="initial-scale=1, width=device-width">
        <meta name="description" content="Play Sabacc!"/>

        <!-- http://getbootstrap.com/docs/4.5/ -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">

        <!-- http://getbootstrap.com/docs/4.5/ -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js" integrity="sha512-894YE6QWD5I59HgZOGReFYm4dnWc1Qt5NtvYSaNcOP+u1T9qYdvdihz0PPSiiqn/+/3e7Jo4EaG7TubfWGUrMQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <script src="https://code.jquery.com/ui/1.13.0/jquery-ui.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous"></script>

        <!-- font awesome -->
        <script src="https://kit.fontawesome.com/75b19c7a56.js" crossorigin="anonymous"></script>

        <!-- Favicon -->
        <link href="favicon.png" rel="icon">

        <!-- General CSS -->
        <link href="/styles/main/styles.css" rel="stylesheet">
        <link rel="stylesheet" href="/styles/main/styles-homepage.css">

        {#if loggedIn === true}
            {#if dark === "true"}
                <!-- Light/Dark mode -->
                <link href="/styles/main/dark.css" rel="stylesheet">
            {/if}
        {/if}


    </head>

    <body>

        <nav class="navbar navbar-expand-md border" class:navbar-light={dark!="true"} class:bg-light={dark!="true"} class:navbar-dark={dark==="true"} class:bg-dark={dark==="true"}>
            <a class="navbar-brand" href="/"><span class="blue">Sabacc</span></a>
            <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-target="#navbar" data-toggle="collapse" type="button">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="nav nav-pills collapse navbar-collapse" id="navbar">
                {#if loggedIn}
                    <ul class="navbar-nav mr-auto mt-2">
                        <li class="nav-item">
                            <div class="dropdown">
                                <a class="nav-link dropdown-toggle" data-toggle="dropdown" href="#">Host a Game</a>
                                <div class="dropdown-menu">
                                  <a class="dropdown-item" href="/host/traditional">Traditional Sabacc</a>
                                  <a class="dropdown-item" href="/host/corellian-spike">Corellian Spike Sabacc</a>
                                </div>
                            </div>
                        </li>
                    </ul>
                    <!-- {initializeDropdown()} -->
                    <ul class="navbar-nav ml-auto mt-2">
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/how-to-play"} href="/how-to-play">How to Play</a></li>
                        <li class="nav-item"><a class="nav-link" href="https://discord.com/invite/AaYrNZjBus" target="_blank">Join the Discord</a></li>
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/settings"} href="/settings">Settings</a></li>
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/logout"} href="/logout">Log Out</a></li>
                    </ul>
                {:else}
                    <ul class="navbar-nav ml-auto mt-2">
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/how-to-play"} href="/how-to-play">How to Play</a></li>
                        <li class="nav-item"><a class="nav-link" href="https://discord.com/invite/AaYrNZjBus" target="_blank">Join the Discord</a></li>
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/register"} href="/register">Register</a></li>
                        <li class="nav-item"><a class="nav-link" class:active={$page.url.pathname==="/login"} href="/login">Log In</a></li>
                    </ul>
                {/if}
            </div>
        </nav>

        <main class="container-fluid p-5">
            <slot></slot>
        </main>

    </body>

</html>
