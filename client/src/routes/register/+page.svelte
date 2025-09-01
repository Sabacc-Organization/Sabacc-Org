
<script lang="ts">
    import { enhance } from "$app/forms";


    /** @type {import('./$types').PageData} */
    export let form;

    let username = "";
    let password = "";
    let confirmPassword = "";

</script>

<svelte:head>
  <title>Sabacc: Register</title>
</svelte:head>

<form method="POST" use:enhance>
    <input bind:value={username} type="text" class="form-control form-group" name="username" placeholder="Username" autocomplete="off" required>
    <br>
    <input bind:value={password} type="password" class="form-control form-group" name="password" placeholder="Password" autocomplete="off" required>
    <br>
    <input bind:value={confirmPassword} type="password" class="form-control form-group" name="confirmationPassword" placeholder="Confirm Password" autocomplete="off" required>
    <br>
    <button type="submit" class="btn btn-primary">Register</button>
</form>

<p class="error"><b>{form?.error || ""}</b></p>
