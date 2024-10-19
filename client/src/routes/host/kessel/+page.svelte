<script lang="ts">
    import HostTemplate from "../hostTemplate.svelte";
    export let form;
    let game_variant = "kessel";
</script>

<HostTemplate {game_variant} {form} />