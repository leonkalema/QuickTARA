<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import OrganizationSettings from '$lib/components/settings/OrganizationSettings.svelte';
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
	<title>Organizations - QuickTARA</title>
</svelte:head>

<OrganizationSettings />
