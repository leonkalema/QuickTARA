<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authApi, type RegisterRequest, AuthApiError } from '$lib/api/auth';

	const dispatch = createEventDispatcher<{
		success: { user: any };
		switchToLogin: void;
	}>();

	let email = '';
	let username = '';
	let firstName = '';
	let lastName = '';
	let password = '';
	let confirmPassword = '';
	let isLoading = false;
	let error = '';
	let showPassword = false;
	let showConfirmPassword = false;

	async function handleRegister() {
		// Validation
		if (!email || !username || !firstName || !lastName || !password || !confirmPassword) {
			error = 'Please fill in all fields';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			error = 'Password must be at least 8 characters long';
			return;
		}

		isLoading = true;
		error = '';

		try {
			const userData: RegisterRequest = {
				email,
				username,
				first_name: firstName,
				last_name: lastName,
				password
			};

			const user = await authApi.register(userData);
			
			dispatch('success', { user });

		} catch (err) {
			console.error('Registration error:', err);
			
			if (err instanceof AuthApiError) {
				if (err.status === 400) {
					error = 'User with this email or username already exists';
				} else if (err.status === 422) {
					// Handle validation errors
					if (err.details?.detail && Array.isArray(err.details.detail)) {
						const validationErrors = err.details.detail.map((e: any) => e.msg).join(', ');
						error = `Validation error: ${validationErrors}`;
					} else {
						error = 'Please check your input format';
					}
				} else {
					error = err.message || 'Registration failed';
				}
			} else {
				error = 'Network error. Please try again.';
			}
		} finally {
			isLoading = false;
		}
	}

	function handleKeyPress(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			handleRegister();
		}
	}
</script>

<div class="register-form">
	<div class="form-header">
		<h2>Create Account</h2>
		<p>Join QuickTARA to get started</p>
	</div>

	<form on:submit|preventDefault={handleRegister} class="form">
		<div class="form-row">
			<div class="form-group">
				<label for="firstName">First Name</label>
				<input
					id="firstName"
					type="text"
					bind:value={firstName}
					on:keypress={handleKeyPress}
					placeholder="First name"
					disabled={isLoading}
					required
				/>
			</div>
			<div class="form-group">
				<label for="lastName">Last Name</label>
				<input
					id="lastName"
					type="text"
					bind:value={lastName}
					on:keypress={handleKeyPress}
					placeholder="Last name"
					disabled={isLoading}
					required
				/>
			</div>
		</div>

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
			<label for="username">Username</label>
			<input
				id="username"
				type="text"
				bind:value={username}
				on:keypress={handleKeyPress}
				placeholder="Choose a username"
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
					placeholder="Create a password"
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
			<small class="password-hint">At least 8 characters</small>
		</div>

		<div class="form-group">
			<label for="confirmPassword">Confirm Password</label>
			<div class="password-input">
				<input
					id="confirmPassword"
					type={showConfirmPassword ? 'text' : 'password'}
					bind:value={confirmPassword}
					on:keypress={handleKeyPress}
					placeholder="Confirm your password"
					disabled={isLoading}
					required
				/>
				<button
					type="button"
					class="password-toggle"
					on:click={() => showConfirmPassword = !showConfirmPassword}
					disabled={isLoading}
				>
					{showConfirmPassword ? '👁️' : '👁️‍🗨️'}
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
				Creating Account...
			{:else}
				Create Account
			{/if}
		</button>
	</form>

	<div class="form-footer">
		<p>
			Already have an account?
			<button type="button" class="link-btn" on:click={() => dispatch('switchToLogin')}>
				Sign in
			</button>
		</p>
	</div>
</div>

<style>
	.register-form {
		width: 100%;
		max-width: 450px;
		margin: 0 auto;
		padding: 2rem;
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	.form-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.form-header h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.875rem;
		font-weight: 700;
		color: #1f2937;
	}

	.form-header p {
		margin: 0;
		color: #6b7280;
		font-size: 0.875rem;
	}

	.form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-weight: 500;
		color: #374151;
		font-size: 0.875rem;
	}

	.form-group input {
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 1rem;
		transition: border-color 0.2s, box-shadow 0.2s;
	}

	.form-group input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-group input:disabled {
		background-color: #f9fafb;
		cursor: not-allowed;
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
		padding: 0.25rem;
		color: #6b7280;
		font-size: 1.25rem;
	}

	.password-toggle:hover {
		color: #374151;
	}

	.password-toggle:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.password-hint {
		color: #6b7280;
		font-size: 0.75rem;
		margin-top: -0.25rem;
	}

	.error-message {
		padding: 0.75rem;
		background-color: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 6px;
		color: #dc2626;
		font-size: 0.875rem;
		text-align: center;
	}

	.submit-btn {
		padding: 0.75rem 1.5rem;
		background-color: #10b981;
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
		background-color: #059669;
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
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.form-footer p {
		margin: 0;
		color: #6b7280;
		font-size: 0.875rem;
	}

	.link-btn {
		background: none;
		border: none;
		color: #3b82f6;
		cursor: pointer;
		font-size: inherit;
		text-decoration: underline;
		padding: 0;
		margin-left: 0.25rem;
	}

	.link-btn:hover {
		color: #2563eb;
	}
</style>
