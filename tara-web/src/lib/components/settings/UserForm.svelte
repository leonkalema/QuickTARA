<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { X } from '@lucide/svelte';
	import { authApi } from '$lib/api/auth';
	import { notifications } from '$lib/stores/notifications';

	export let user = null;

	const dispatch = createEventDispatcher();

	let formData = {
		email: user?.email || '',
		username: user?.username || '',
		first_name: user?.first_name || '',
		last_name: user?.last_name || '',
		password: '',
		confirm_password: '',
		role: user?.organizations?.[0]?.role || 'Risk Manager',
		status: user?.status || 'active'
	};

	let loading = false;
	let errors = {};

	const roles = [
		'Tool Admin',
		'Org Admin', 
		'Risk Manager',
		'Risk Analyst',
		'Viewer'
	];

	function validateForm() {
		errors = {};

		if (!formData.email) errors.email = 'Email is required';
		if (!formData.username) errors.username = 'Username is required';
		if (!formData.first_name) errors.first_name = 'First name is required';
		if (!formData.last_name) errors.last_name = 'Last name is required';

		if (!user) {
			if (!formData.password) errors.password = 'Password is required';
			if (formData.password !== formData.confirm_password) {
				errors.confirm_password = 'Passwords do not match';
			}
		}

		return Object.keys(errors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) return;

		loading = true;
		try {
			if (user) {
				await authApi.updateUser(user.user_id, {
					email: formData.email,
					username: formData.username,
					first_name: formData.first_name,
					last_name: formData.last_name,
					status: formData.status
				});
			} else {
				await authApi.createUser({
					email: formData.email,
					username: formData.username,
					first_name: formData.first_name,
					last_name: formData.last_name,
					password: formData.password,
					role: formData.role
				});
			}
			dispatch('saved');
		} catch (error) {
			notifications.show(`Failed to ${user ? 'update' : 'create'} user`, 'error');
		} finally {
			loading = false;
		}
	}

	function handleCancel() {
		dispatch('cancelled');
	}
</script>

<div class="modal-overlay" on:click={handleCancel}>
	<div class="modal" on:click|stopPropagation>
		<div class="modal-header">
			<h3>{user ? 'Edit User' : 'Create User'}</h3>
			<button class="close-btn" on:click={handleCancel}>
				<X class="w-5 h-5" />
			</button>
		</div>

		<form on:submit|preventDefault={handleSubmit} class="user-form">
			<div class="form-row">
				<div class="form-group">
					<label for="first_name">First Name</label>
					<input
						id="first_name"
						type="text"
						bind:value={formData.first_name}
						class:error={errors.first_name}
						required
					/>
					{#if errors.first_name}
						<span class="error-text">{errors.first_name}</span>
					{/if}
				</div>

				<div class="form-group">
					<label for="last_name">Last Name</label>
					<input
						id="last_name"
						type="text"
						bind:value={formData.last_name}
						class:error={errors.last_name}
						required
					/>
					{#if errors.last_name}
						<span class="error-text">{errors.last_name}</span>
					{/if}
				</div>
			</div>

			<div class="form-group">
				<label for="email">Email</label>
				<input
					id="email"
					type="email"
					bind:value={formData.email}
					class:error={errors.email}
					required
				/>
				{#if errors.email}
					<span class="error-text">{errors.email}</span>
				{/if}
			</div>

			<div class="form-group">
				<label for="username">Username</label>
				<input
					id="username"
					type="text"
					bind:value={formData.username}
					class:error={errors.username}
					required
				/>
				{#if errors.username}
					<span class="error-text">{errors.username}</span>
				{/if}
			</div>

			{#if !user}
				<div class="form-row">
					<div class="form-group">
						<label for="password">Password</label>
						<input
							id="password"
							type="password"
							bind:value={formData.password}
							class:error={errors.password}
							required
						/>
						{#if errors.password}
							<span class="error-text">{errors.password}</span>
						{/if}
					</div>

					<div class="form-group">
						<label for="confirm_password">Confirm Password</label>
						<input
							id="confirm_password"
							type="password"
							bind:value={formData.confirm_password}
							class:error={errors.confirm_password}
							required
						/>
						{#if errors.confirm_password}
							<span class="error-text">{errors.confirm_password}</span>
						{/if}
					</div>
				</div>
			{/if}

			<div class="form-row">
				<div class="form-group">
					<label for="role">Role</label>
					<select id="role" bind:value={formData.role}>
						{#each roles as role}
							<option value={role}>{role}</option>
						{/each}
					</select>
				</div>

				<div class="form-group">
					<label for="status">Status</label>
					<select id="status" bind:value={formData.status}>
						<option value="active">Active</option>
						<option value="inactive">Inactive</option>
					</select>
				</div>
			</div>

			<div class="form-actions">
				<button type="button" class="btn-secondary" on:click={handleCancel}>
					Cancel
				</button>
				<button type="submit" class="btn-primary" disabled={loading}>
					{loading ? 'Saving...' : user ? 'Update User' : 'Create User'}
				</button>
			</div>
		</form>
	</div>
</div>

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal {
		background: white;
		border-radius: 8px;
		width: 90%;
		max-width: 600px;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.modal-header h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
	}

	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #6b7280;
		padding: 0.25rem;
	}

	.user-form {
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
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

	label {
		font-weight: 500;
		color: #374151;
	}

	input, select {
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
	}

	input:focus, select:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	input.error {
		border-color: #dc2626;
	}

	.error-text {
		color: #dc2626;
		font-size: 0.75rem;
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.btn-primary, .btn-secondary {
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
		border: none;
	}

	.btn-primary {
		background: #3b82f6;
		color: white;
	}

	.btn-primary:disabled {
		background: #9ca3af;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
	}

	@media (max-width: 640px) {
		.form-row {
			grid-template-columns: 1fr;
		}
	}
</style>
