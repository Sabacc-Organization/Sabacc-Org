<script lang=ts>

    export let data;

</script>

<nav class="navbar navbar-expand-md navbar-light bg-light border">
    <a class="navbar-brand" href="/"><span class="blue">Sabacc</span></a>
    <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-target="#navbar" data-toggle="collapse" type="button">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbar">
        {#if data.user_id != undefined}
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