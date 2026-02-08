<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authApi, type LoginRequest, AuthApiError } from '$lib/api/auth';
	import { authStore } from '$lib/stores/auth';
	import { Eye, EyeOff, Mail, Lock, AlertCircle } from '@lucide/svelte';

	const dispatch = createEventDispatcher<{
		success: { user: any; token: string; refreshToken: string };
	}>();

	let email = '';
	let password = '';
	let isLoading = false;
	let error = '';
	let showPassword = false;

	async function handleLogin() {
		if (!email || !password) {
			error = 'Please fill in all fields';
			return;
		}

		isLoading = true;
		error = '';
		authStore.setLoading(true);

		try {
			const credentials: LoginRequest = { email, password };
			const loginResponse = await authApi.login(credentials);
			
			// Get user info with the new token
			const user = await authApi.getCurrentUser(loginResponse.access_token);
			
			// Update auth store
			authStore.login(user, loginResponse.access_token, loginResponse.refresh_token);
			
			// Dispatch success event
			dispatch('success', {
				user,
				token: loginResponse.access_token,
				refreshToken: loginResponse.refresh_token
			});

		} catch (err) {
			console.error('Login error:', err);
			
			if (err instanceof AuthApiError) {
				if (err.status === 401) {
					error = 'Invalid email or password';
				} else if (err.status === 422) {
					error = 'Please check your email format';
				} else {
					error = err.message || 'Login failed';
				}
			} else {
				error = 'Network error. Please try again.';
			}
		} finally {
			isLoading = false;
			authStore.setLoading(false);
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleLogin();
		}
	}
</script>

<div class="login-form">
	<div class="form-header">
		<h2>Welcome back</h2>
		<p>Sign in to your account to continue</p>
	</div>

	<form on:submit|preventDefault={handleLogin} class="form">
		<div class="form-group">
			<label for="email">Email address</label>
			<div class="input-wrapper">
				<div class="input-icon">
					<Mail size={18} />
				</div>
				<input
					id="email"
					type="email"
					bind:value={email}
					on:keypress={handleKeyPress}
					placeholder="name@company.com"
					disabled={isLoading}
					required
					class="with-icon"
				/>
			</div>
		</div>

		<div class="form-group">
			<label for="password">Password</label>
			<div class="input-wrapper">
				<div class="input-icon">
					<Lock size={18} />
				</div>
				<input
					id="password"
					type={showPassword ? 'text' : 'password'}
					bind:value={password}
					on:keypress={handleKeyPress}
					placeholder="Enter your password"
					disabled={isLoading}
					required
					class="with-icon"
				/>
				<button
					type="button"
					class="password-toggle"
					on:click={() => showPassword = !showPassword}
					disabled={isLoading}
					aria-label={showPassword ? 'Hide password' : 'Show password'}
				>
					{#if showPassword}
						<EyeOff size={18} />
					{:else}
						<Eye size={18} />
					{/if}
				</button>
			</div>
		</div>

		{#if error}
			<div class="error-message">
				<AlertCircle size={16} />
				<span>{error}</span>
			</div>
		{/if}

		<button type="submit" class="submit-btn" disabled={isLoading}>
			{#if isLoading}
				<span class="spinner"></span>
				Signing in...
			{:else}
				Sign in
			{/if}
		</button>
	</form>

	<div class="form-footer">
		<p>Need access? Contact your administrator</p>
	</div>
</div>

<style>
	.login-form {
		width: 100%;
	}

	.form-header {
		margin-bottom: 2rem;
	}

	.form-header h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.75rem;
		font-weight: 700;
		color: #f8fafc;
		letter-spacing: -0.025em;
	}

	.form-header p {
		margin: 0;
		color: #64748b;
		font-size: 0.95rem;
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		display: block;
		font-weight: 500;
		color: #cbd5e1;
		font-size: 0.875rem;
	}

	.input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
	}

	.input-icon {
		position: absolute;
		left: 0.875rem;
		color: #475569;
		display: flex;
		align-items: center;
		justify-content: center;
		pointer-events: none;
		z-index: 1;
	}

	.form-group input {
		width: 100%;
		padding: 0.875rem 1rem;
		border: 1px solid #1e293b;
		border-radius: 10px;
		font-size: 0.95rem;
		background: #0f172a;
		color: #f1f5f9;
		transition: all 0.2s ease;
	}

	.form-group input.with-icon {
		padding-left: 2.75rem;
	}

	.form-group input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
		background: #0c1322;
	}

	.form-group input::placeholder {
		color: #475569;
	}

	.form-group input:disabled {
		background-color: #1e293b;
		cursor: not-allowed;
		opacity: 0.6;
	}

	.password-toggle {
		position: absolute;
		right: 0.875rem;
		background: none;
		border: none;
		cursor: pointer;
		color: #475569;
		padding: 0.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 6px;
		transition: all 0.2s ease;
	}

	.password-toggle:hover {
		color: #94a3b8;
		background: rgba(255, 255, 255, 0.05);
	}

	.password-toggle:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.error-message {
		padding: 0.875rem 1rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid rgba(239, 68, 68, 0.2);
		border-radius: 10px;
		color: #f87171;
		font-size: 0.875rem;
		display: flex;
		align-items: center;
		gap: 0.625rem;
		animation: shake 0.4s ease-out;
	}

	@keyframes shake {
		0%, 100% { transform: translateX(0); }
		20% { transform: translateX(-4px); }
		40% { transform: translateX(4px); }
		60% { transform: translateX(-4px); }
		80% { transform: translateX(4px); }
	}

	.submit-btn {
		margin-top: 0.5rem;
		padding: 0.875rem 1.5rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
		color: white;
		border: none;
		border-radius: 10px;
		font-size: 0.95rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
	}

	.submit-btn:hover:not(:disabled) {
		background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
		box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
		transform: translateY(-1px);
	}

	.submit-btn:active:not(:disabled) {
		transform: translateY(0);
	}

	.submit-btn:disabled {
		background: #334155;
		box-shadow: none;
		cursor: not-allowed;
	}

	.spinner {
		width: 1.125rem;
		height: 1.125rem;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.form-footer {
		text-align: center;
		margin-top: 2rem;
		padding-top: 1.5rem;
		border-top: 1px solid #1e293b;
	}

	.form-footer p {
		margin: 0;
		color: #475569;
		font-size: 0.85rem;
	}
</style>
