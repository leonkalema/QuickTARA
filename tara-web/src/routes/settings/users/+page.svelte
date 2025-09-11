<script lang="ts">
	import { onMount } from 'svelte';
	import UserManagement from '$lib/components/settings/UserManagement.svelte';
	import { requireUserManagement } from '$lib/utils/routeGuards';

	onMount(() => {
		// Check authentication and permissions
		requireUserManagement();
	});
</script>

<svelte:head>
	<title>User Management - QuickTARA</title>
</svelte:head>

<UserManagement />
