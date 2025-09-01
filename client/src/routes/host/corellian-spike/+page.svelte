<script lang="ts">
    import HostTemplate from "../hostTemplate.svelte";
    export let form;
    let game_variant = "corellian-spike";
</script>

<HostTemplate {game_variant} {form} />