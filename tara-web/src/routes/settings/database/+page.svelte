<script lang="ts">
	import { onMount } from 'svelte';
	import DatabaseSettings from '$lib/components/settings/DatabaseSettings.svelte';
	import { requireSystemSettings } from '$lib/utils/routeGuards';

	onMount(() => {
		// Check authentication and permissions
		requireSystemSettings();
	});
</script>

<svelte:head>
	<title>Database Configuration - QuickTARA</title>
</svelte:head>

<DatabaseSettings />
