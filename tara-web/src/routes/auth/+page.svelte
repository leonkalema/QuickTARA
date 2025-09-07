<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import LoginForm from '$lib/components/LoginForm.svelte';
	let showSuccessMessage = false;
	let successMessage = '';
	const currentYear = new Date().getFullYear();

	// Check if user is already authenticated on mount only
	onMount(() => {
		// Check once on mount, don't subscribe to avoid redirect loops
		const auth = authStore;
		if (auth && typeof auth.subscribe === 'function') {
			const currentState = $authStore;
			if (currentState.isAuthenticated) {
				goto('/');
			}
		}
	});

	function handleLoginSuccess(event: CustomEvent) {
		// User is automatically logged in via the auth store
		// Redirect will happen via the onMount subscription
		showSuccessMessage = true;
		successMessage = 'Login successful! Redirecting...';
		
		setTimeout(() => {
			goto('/');
		}, 1000);
	}

</script>

<svelte:head>
	<title>Sign In - QuickTARA</title>
</svelte:head>

<div class="auth-page">
	<div class="auth-container">
		<div class="auth-header">
			<div class="logo">
				<h1>QuickTARA</h1>
				<p>Automotive Cybersecurity Platform</p>
			</div>
		</div>

		{#if showSuccessMessage}
			<div class="success-banner">
				<div class="success-content">
					<span class="success-icon">✅</span>
					<p>{successMessage}</p>
				</div>
			</div>
		{/if}

		<div class="auth-form-container">
			<LoginForm on:success={handleLoginSuccess} />
		</div>

		<div class="auth-footer">
			<p>&copy; {currentYear} All rights reserved.</p>
		</div>
	</div>
</div>

<style>
	.auth-page {
		min-height: 100vh;
		background: #0f0f0f;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}

	.auth-container {
		width: 100%;
		max-width: 420px;
		background: #1a1a1a;
		border: 1px solid #333;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
	}

	.auth-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.logo h1 {
		font-size: 2rem;
		font-weight: 700;
		color: #ffffff;
		margin: 0 0 0.5rem 0;
	}

	.logo p {
		color: #9ca3af;
		margin: 0;
		font-size: 0.9rem;
	}

	.success-banner {
		background: #065f46;
		border: 1px solid #10b981;
		border-radius: 8px;
		padding: 1rem;
		animation: slideIn 0.3s ease-out;
	}

	.success-content {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: #10b981;
	}

	.success-icon {
		font-size: 1.25rem;
	}

	.auth-form-container {
		flex: 1;
		animation: fadeIn 0.5s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.auth-footer {
		text-align: center;
		color: white;
		opacity: 0.8;
	}

	.auth-footer p {
		margin: 0;
		font-size: 0.875rem;
	}

	@media (max-width: 640px) {
		.auth-page {
			padding: 0.5rem;
		}

		.logo h1 {
			font-size: 2.5rem;
		}

		.logo p {
			font-size: 1rem;
		}
	}
</style>
