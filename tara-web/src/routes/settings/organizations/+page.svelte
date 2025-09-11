<script lang="ts">
	import { onMount } from 'svelte';
	import OrganizationSettings from '$lib/components/settings/OrganizationSettings.svelte';
	import { requireOrgManagement } from '$lib/utils/routeGuards';

	onMount(() => {
		// Check authentication and permissions
		requireOrgManagement();
	});
</script>

<svelte:head>
	<title>Organizations - QuickTARA</title>
</svelte:head>

<OrganizationSettings />
