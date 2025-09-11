<script lang="ts">
	import { onMount } from 'svelte';
	import SystemSettings from '$lib/components/settings/SystemSettings.svelte';
	import { requireSystemSettings } from '$lib/utils/routeGuards';

	onMount(() => {
		// Check authentication and permissions
		requireSystemSettings();
	});
</script>

<svelte:head>
	<title>System Settings - QuickTARA</title>
</svelte:head>

<SystemSettings />
