<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import LoginForm from '$lib/components/LoginForm.svelte';
	import { Shield, Lock, Zap, CheckCircle } from '@lucide/svelte';
	
	let showSuccessMessage = false;
	let successMessage = '';
	const currentYear = new Date().getFullYear();

	onMount(() => {
		const auth = authStore;
		if (auth && typeof auth.subscribe === 'function') {
			const currentState = $authStore;
			if (currentState.isAuthenticated) {
				goto('/');
			}
		}
	});

	function handleLoginSuccess(event: CustomEvent) {
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
	<!-- Left Panel - Branding -->
	<div class="brand-panel">
		<div class="brand-content">
			<div class="brand-logo">
				<div class="logo-icon">
					<Shield size={48} strokeWidth={1.5} />
				</div>
				<h1>QuickTARA</h1>
			</div>
			<p class="brand-tagline">Automotive Threat Analysis & Risk Assessment</p>
			
			<div class="features">
				<div class="feature">
					<div class="feature-icon">
						<Zap size={20} />
					</div>
					<div class="feature-text">
						<span class="feature-title">Fast Analysis</span>
						<span class="feature-desc">Streamlined TARA workflow</span>
					</div>
				</div>
				<div class="feature">
					<div class="feature-icon">
						<Lock size={20} />
					</div>
					<div class="feature-text">
						<span class="feature-title">ISO 21434 Compliant</span>
						<span class="feature-desc">Industry standard methodology</span>
					</div>
				</div>
				<div class="feature">
					<div class="feature-icon">
						<CheckCircle size={20} />
					</div>
					<div class="feature-text">
						<span class="feature-title">Risk Management</span>
						<span class="feature-desc">Track and mitigate threats</span>
					</div>
				</div>
			</div>
		</div>
		
		<div class="brand-footer">
			<p>&copy; {currentYear} QuickTARA. All rights reserved.</p>
		</div>
	</div>
	
	<!-- Right Panel - Login Form -->
	<div class="form-panel">
		<div class="form-wrapper">
			{#if showSuccessMessage}
				<div class="success-banner">
					<CheckCircle size={20} class="text-emerald-400" />
					<p>{successMessage}</p>
				</div>
			{/if}
			
			<div class="mobile-logo">
				<Shield size={32} />
				<span>QuickTARA</span>
			</div>
			
			<LoginForm on:success={handleLoginSuccess} />
		</div>
	</div>
</div>

<style>
	.auth-page {
		min-height: 100vh;
		display: flex;
		background: #030712;
	}

	/* Left Brand Panel */
	.brand-panel {
		flex: 1;
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 3rem;
		position: relative;
		overflow: hidden;
	}

	.brand-panel::before {
		content: '';
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: radial-gradient(circle at 30% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 50%);
		pointer-events: none;
	}

	.brand-content {
		position: relative;
		z-index: 1;
		max-width: 480px;
		margin: 0 auto;
	}

	.brand-logo {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.logo-icon {
		color: #3b82f6;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.brand-logo h1 {
		font-size: 2.5rem;
		font-weight: 700;
		color: #ffffff;
		margin: 0;
		letter-spacing: -0.025em;
	}

	.brand-tagline {
		color: #94a3b8;
		font-size: 1.125rem;
		margin: 0 0 3rem 0;
		line-height: 1.6;
	}

	.features {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.feature {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		padding: 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 12px;
		border: 1px solid rgba(255, 255, 255, 0.05);
		transition: all 0.3s ease;
	}

	.feature:hover {
		background: rgba(255, 255, 255, 0.05);
		border-color: rgba(59, 130, 246, 0.2);
		transform: translateX(4px);
	}

	.feature-icon {
		width: 40px;
		height: 40px;
		background: rgba(59, 130, 246, 0.1);
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #3b82f6;
		flex-shrink: 0;
	}

	.feature-text {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.feature-title {
		color: #f1f5f9;
		font-weight: 600;
		font-size: 0.95rem;
	}

	.feature-desc {
		color: #64748b;
		font-size: 0.85rem;
	}

	.brand-footer {
		position: absolute;
		bottom: 2rem;
		left: 3rem;
		right: 3rem;
	}

	.brand-footer p {
		color: #475569;
		font-size: 0.8rem;
		margin: 0;
	}

	/* Right Form Panel */
	.form-panel {
		flex: 1;
		max-width: 560px;
		background: #111827;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
	}

	.form-wrapper {
		width: 100%;
		max-width: 400px;
		animation: fadeIn 0.5s ease-out;
	}

	.mobile-logo {
		display: none;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		margin-bottom: 2rem;
		color: #3b82f6;
	}

	.mobile-logo span {
		font-size: 1.5rem;
		font-weight: 700;
		color: #ffffff;
	}

	.success-banner {
		background: rgba(16, 185, 129, 0.1);
		border: 1px solid rgba(16, 185, 129, 0.3);
		border-radius: 12px;
		padding: 1rem 1.25rem;
		margin-bottom: 1.5rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: #34d399;
		animation: slideDown 0.3s ease-out;
	}

	.success-banner p {
		margin: 0;
		font-size: 0.9rem;
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

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Responsive */
	@media (max-width: 1024px) {
		.brand-panel {
			display: none;
		}

		.form-panel {
			max-width: 100%;
			min-height: 100vh;
		}

		.mobile-logo {
			display: flex;
		}
	}

	@media (max-width: 480px) {
		.form-panel {
			padding: 1.5rem;
		}
	}
</style>
