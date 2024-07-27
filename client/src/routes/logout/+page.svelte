<script lang="ts">
    import { customRedirect } from '$lib';
    import { onMount } from 'svelte';
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    onMount( async () => {
        customRedirect(FRONTEND_URL);
    });

</script>
