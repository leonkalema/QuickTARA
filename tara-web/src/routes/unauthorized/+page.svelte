<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { getUserRoleDisplay } from '$lib/utils/permissions';
	import { AlertTriangle, ArrowLeft } from '@lucide/svelte';

	function goBack() {
		goto('/');
	}

	function logout() {
		authStore.logout();
		goto('/auth');
	}

</script>

<svelte:head>
	<title>Unauthorized - QuickTARA</title>
</svelte:head>

<div class="unauthorized-page">
	<div class="unauthorized-container">
		<div class="icon-container">
			<AlertTriangle class="w-16 h-16 text-red-500" />
		</div>
		
		<h1>Access Denied</h1>
		<p class="message">
			You don't have permission to access this page. Please contact your administrator if you believe this is an error.
		</p>
		
		<div class="actions">
			<button class="btn-secondary" on:click={goBack}>
				<ArrowLeft class="w-4 h-4" />
				Go Back
			</button>
			<button class="btn-primary" on:click={logout}>
				Sign Out
			</button>
		</div>
		
		{#if $authStore.user}
			<div class="user-info">
				<p class="text-sm text-gray-600">
					Signed in as: <strong>{$authStore.user.email}</strong>
				</p>
				<p class="text-sm text-gray-600">
					Role: <strong>
						{getUserRoleDisplay()}
					</strong>
				</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.unauthorized-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #f9fafb;
		padding: 1rem;
	}

	.unauthorized-container {
		max-width: 500px;
		text-align: center;
		background: white;
		padding: 3rem 2rem;
		border-radius: 12px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
	}

	.icon-container {
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #1f2937;
		margin: 0 0 1rem 0;
	}

	.message {
		color: #6b7280;
		font-size: 1.1rem;
		line-height: 1.6;
		margin: 0 0 2rem 0;
	}

	.actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		margin-bottom: 2rem;
	}

	.btn-primary, .btn-secondary {
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		text-decoration: none;
		border: none;
		font-size: 1rem;
	}

	.btn-primary {
		background: #3b82f6;
		color: white;
	}

	.btn-primary:hover {
		background: #2563eb;
	}

	.btn-secondary {
		background: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
	}

	.btn-secondary:hover {
		background: #e5e7eb;
	}

	.user-info {
		padding-top: 2rem;
		border-top: 1px solid #e5e7eb;
	}

	.user-info p {
		margin: 0.5rem 0;
	}
</style>
