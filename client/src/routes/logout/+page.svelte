<script lang="ts">
    import { goto } from '$app/navigation';
  import { customRedirect } from '$lib';
    import Cookies from 'js-cookie';
  import { onMount } from 'svelte';
    const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL;

    Cookies.remove("username");
    Cookies.remove("PASSWORD");
    Cookies.remove("theme");
    Cookies.remove("dark");
    Cookies.remove("cardDesign");

    customRedirect(FRONTEND_URL);

</script>

<svelte:head>
  <title>Sabacc: Logout</title>
</svelte:head>
