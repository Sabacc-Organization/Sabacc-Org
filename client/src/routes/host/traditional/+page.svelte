<script lang="ts">
    import HostTemplate from "../hostTemplate.svelte";
    export let form;
    let game_variant = "traditional";
</script>

<HostTemplate {game_variant} {form} />