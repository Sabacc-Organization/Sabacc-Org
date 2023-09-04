<script lang="ts">
    function changePassword() {    
        jQuery("#remove").remove();

        jQuery("#em1").attr("type", "password");
        jQuery("#em1").attr("required", "");

        jQuery("#em2").attr("type", "password");
        jQuery("#em2").attr("required", "");

        jQuery("#hid").attr("value", "true");
    }

    export let form;
</script>

<form action="/login" method="POST">
    <input autocomplete="off" autofocus class="form-control form-group" name="username" placeholder="Username" type="text" required>
    <br>
    <input class="form-control form-group" name="password" placeholder="Password" type="password" required>
    <br>
    <div id="remove">
        <p>Don't like your password? <button type="button" on:click={changePassword} class="btn btn-primary">Change it.</button></p>
    </div>

    <input id="hid" type="hidden" name="change" value="false">

    <div><input id="em1" type="hidden" class="form-control form-group" placeholder="New Password" name="pass"></div>

    <div><input id="em2" type="hidden" class="form-control form-group" placeholder="Confirmation" name="passCon"></div>

    <button class="btn btn-primary" type="submit">Login</button>
</form>

{#if form?.success}
  <!-- this message is ephemeral; it exists because the page was rendered in
       response to a form submission. it will vanish if the user reloads -->
  <p>{form?.err}</p>
{/if}