<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import SystemSettings from '$lib/components/settings/SystemSettings.svelte';
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
	<title>System Settings - QuickTARA</title>
</svelte:head>

<SystemSettings />
