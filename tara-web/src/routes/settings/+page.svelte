<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';

	onMount(() => {
		// Check authentication
		if (!$authStore.isAuthenticated) {
			goto('/auth');
			return;
		}
		
		// Redirect to users by default
		goto('/settings/users');
	});
</script>

<svelte:head>
	<title>Settings - QuickTARA</title>
</svelte:head>

<div class="settings-content">
	<div class="flex items-center justify-center h-64">
		<div class="text-center">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
			<p class="text-gray-600">Redirecting to settings...</p>
		</div>
	</div>
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
