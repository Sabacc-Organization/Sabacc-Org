<script>

    export let data;

    const sessLog = async () => {
        const res = await fetch("http://127.0.0.1:8080/userLog?log=gol");
    }

    const getSession = async () => {
        const res = await fetch("http://127.0.0.1:8080/userData");
        const sessionJson = await res.json();

        console.log(sessionJson);
    }
</script>

<!-- http://getbootstrap.com/docs/4.5/ -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
<!-- 
<nav class="navbar navbar-expand-md navbar-light bg-light border">
    <a class="navbar-brand" href="/"><span class="blue">Sabacc</span></a>
    <button aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation" class="navbar-toggler" data-target="#navbar" data-toggle="collapse" type="button">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbar">
        {#if session.user_id}
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
</nav> -->

<main class="container p-5">
    <slot></slot>
    <button on:click={sessLog}>Session Setup</button>
    <button on:click={getSession}>Get Session</button>
    <p>{data.o}</p>
    <p>{data.user_id}</p>
</main>