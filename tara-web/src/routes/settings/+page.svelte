<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import UserManagement from '$lib/components/settings/UserManagement.svelte';
	import OrganizationSettings from '$lib/components/settings/OrganizationSettings.svelte';
	import SystemSettings from '$lib/components/settings/SystemSettings.svelte';
	import { authStore } from '$lib/stores/auth';

	let activeTab = 'users';

	onMount(() => {
		// Get tab from URL params
		const urlTab = $page.url.searchParams.get('tab');
		if (urlTab) {
			activeTab = urlTab;
		}
		
		// Check authentication
		if (!$authStore.isAuthenticated) {
			goto('/auth');
			return;
		}
	});

	// Update URL when tab changes
	function setActiveTab(tabId: string) {
		activeTab = tabId;
		const url = new URL(window.location.href);
		if (tabId === 'users') {
			url.searchParams.delete('tab');
		} else {
			url.searchParams.set('tab', tabId);
		}
		window.history.pushState({}, '', url);
	}
</script>

<svelte:head>
	<title>Settings - QuickTARA</title>
</svelte:head>

<!-- Main Content Area -->
<div class="settings-content">
	{#if activeTab === 'users'}
		<UserManagement />
	{:else if activeTab === 'organizations'}
		<OrganizationSettings />
	{:else if activeTab === 'system'}
		<SystemSettings />
	{/if}
</div>

<style>
	.settings-content {
		background: white;
		border-radius: 8px;
		border: 1px solid #e5e7eb;
		padding: 2rem;
		min-height: 600px;
	}
</style>
