<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authApi, type LoginRequest, AuthApiError } from '$lib/api/auth';
	import { authStore } from '$lib/stores/auth';

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
		<h2>Sign In</h2>
		<p>Welcome back</p>
	</div>

	<form on:submit|preventDefault={handleLogin} class="form">
		<div class="form-group">
			<label for="email">Email</label>
			<input
				id="email"
				type="email"
				bind:value={email}
				on:keypress={handleKeyPress}
				placeholder="Enter your email"
				disabled={isLoading}
				required
			/>
		</div>

		<div class="form-group">
			<label for="password">Password</label>
			<div class="password-input">
				<input
					id="password"
					type={showPassword ? 'text' : 'password'}
					bind:value={password}
					on:keypress={handleKeyPress}
					placeholder="Enter your password"
					disabled={isLoading}
					required
				/>
				<button
					type="button"
					class="password-toggle"
					on:click={() => showPassword = !showPassword}
					disabled={isLoading}
				>
					{showPassword ? '👁️' : '👁️‍🗨️'}
				</button>
			</div>
		</div>

		{#if error}
			<div class="error-message">
				{error}
			</div>
		{/if}

		<button type="submit" class="submit-btn" disabled={isLoading}>
			{#if isLoading}
				<span class="spinner"></span>
				Signing in...
			{:else}
				Sign In
			{/if}
		</button>
	</form>

	<div class="form-footer">
		<p class="text-center text-gray-600">
			Contact your administrator for access
		</p>
	</div>
</div>

<style>
	.login-form {
		width: 100%;
		max-width: 400px;
		margin: 0 auto;
	}

	.form-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.form-header h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.875rem;
		font-weight: 700;
		color: #ffffff;
	}

	.form-header p {
		margin: 0;
		color: #9ca3af;
		font-size: 1rem;
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #d1d5db;
		font-size: 0.875rem;
	}

	.form-group input {
		padding: 0.75rem;
		border: 1px solid #374151;
		border-radius: 6px;
		font-size: 1rem;
		background: #111827;
		color: #ffffff;
		transition: border-color 0.2s, box-shadow 0.2s;
	}

	.form-group input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
	}

	.form-group input::placeholder {
		color: #6b7280;
	}

	.form-group input:disabled {
		background-color: #1f2937;
		cursor: not-allowed;
		opacity: 0.5;
	}

	.password-input {
		position: relative;
		display: flex;
		align-items: center;
	}

	.password-input input {
		flex: 1;
		padding-right: 3rem;
	}

	.password-toggle {
		position: absolute;
		right: 0.75rem;
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.password-toggle:hover {
		color: #d1d5db;
	}

	.password-toggle:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.error-message {
		padding: 0.75rem;
		background-color: #450a0a;
		border: 1px solid #dc2626;
		border-radius: 6px;
		color: #fca5a5;
		font-size: 0.875rem;
		margin-bottom: 1rem;
	}

	.submit-btn {
		padding: 0.75rem 1.5rem;
		background-color: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.submit-btn:hover:not(:disabled) {
		background-color: #1d4ed8;
	}

	.submit-btn:disabled {
		background-color: #9ca3af;
		cursor: not-allowed;
	}

	.spinner {
		width: 1rem;
		height: 1rem;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.form-footer {
		text-align: center;
		padding-top: 1.5rem;
		border-top: 1px solid #374151;
	}

	.form-footer p {
		margin: 0;
		color: #9ca3af;
		font-size: 0.875rem;
	}

</style>
