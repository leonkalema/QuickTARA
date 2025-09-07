<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import UserManagement from '$lib/components/settings/UserManagement.svelte';
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
	<title>User Management - QuickTARA</title>
</svelte:head>

<UserManagement />
