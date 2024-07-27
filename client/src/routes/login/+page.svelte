<script lang="ts">
    import { enhance } from "$app/forms";
    export let form;

    let username = "";
    let password = "";

</script>
<svelte:head>
  <title>Sabacc: Login</title>
</svelte:head>

<h1>Login</h1>

<form method="POST" use:enhance>
    <input bind:value={username} type="text" class="form-control form-group" name="username" placeholder="Username" autocomplete="off" required>
    <br>
    <input bind:value={password} type="password" class="form-control form-group" name="password" placeholder="Password" autocomplete="off" required>
    <br>
    <button type="submit" class="btn btn-primary">Login</button>
</form>

<p class="error"><b>{form?.error || ""}</b></p>