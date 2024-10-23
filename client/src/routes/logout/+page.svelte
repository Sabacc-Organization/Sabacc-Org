<script lang="ts">
    import { customRedirect } from '$lib';
    import { onMount } from 'svelte';
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    onMount( async () => {
        console.log(FRONTEND_URL)
        customRedirect(FRONTEND_URL);
    });

</script>
