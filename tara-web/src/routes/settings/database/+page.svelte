<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import DatabaseSettings from '$lib/components/settings/DatabaseSettings.svelte';
	import { authStore } from '$lib/stores/auth';

	onMount(() => {
		// Check authentication
		if (!$authStore.isAuthenticated) {
			goto('/auth');
			return;
		}
	});
</script>

<svelte:head>
	<title>Database Configuration - QuickTARA</title>
</svelte:head>

<DatabaseSettings />
