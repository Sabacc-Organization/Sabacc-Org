<script lang="ts">
    import { customRedirect } from '$lib';
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    customRedirect(FRONTEND_URL);
</script>
