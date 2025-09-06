<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus, Edit, Trash2, Building } from '@lucide/svelte';
	import { notifications } from '$lib/stores/notifications';

	interface Organization {
		organization_id: string;
		name: string;
		description: string;
		created_at: string;
		user_count: number;
	}

	let organizations: Organization[] = [];
	let loading = false;
	let showForm = false;
	let editingOrg: Organization | null = null;

	let formData = {
		name: '',
		description: ''
	};

	onMount(() => {
		loadOrganizations();
	});

	async function loadOrganizations() {
		loading = true;
		try {
			// Mock data for now - replace with actual API call
			organizations = [
				{
					organization_id: '1',
					name: 'Default Organization',
					description: 'Main organization for QuickTARA',
					created_at: '2024-01-01',
					user_count: 5
				}
			];
		} catch (error) {
			notifications.show('Failed to load organizations', 'error');
		} finally {
			loading = false;
		}
	}

	function openCreateForm() {
		editingOrg = null;
		formData = { name: '', description: '' };
		showForm = true;
	}

	function openEditForm(org: Organization) {
		editingOrg = org;
		formData = {
			name: org.name,
			description: org.description
		};
		showForm = true;
	}

	function closeForm() {
		showForm = false;
		editingOrg = null;
		formData = { name: '', description: '' };
	}

	async function handleSubmit() {
		if (!formData.name.trim()) {
			notifications.show('Organization name is required', 'error');
			return;
		}

		try {
			if (editingOrg) {
				// Update organization
				notifications.show('Organization updated successfully', 'success');
			} else {
				// Create organization
				notifications.show('Organization created successfully', 'success');
			}
			closeForm();
			await loadOrganizations();
		} catch (error) {
			notifications.show('Failed to save organization', 'error');
		}
	}

	async function deleteOrganization(org: Organization) {
		if (!confirm(`Are you sure you want to delete "${org.name}"?`)) return;

		try {
			notifications.show('Organization deleted successfully', 'success');
			await loadOrganizations();
		} catch (error) {
			notifications.show('Failed to delete organization', 'error');
		}
	}
</script>

<div class="organization-settings">
	<div class="header">
		<h2>Organization Management</h2>
		<button class="btn-primary" on:click={openCreateForm}>
			<Plus class="w-4 h-4" />
			Add Organization
		</button>
	</div>

	{#if loading}
		<div class="loading">Loading organizations...</div>
	{:else}
		<div class="organizations-grid">
			{#each organizations as org}
				<div class="org-card">
					<div class="org-header">
						<div class="org-icon">
							<Building class="w-6 h-6" />
						</div>
						<div class="org-info">
							<h3>{org.name}</h3>
							<p>{org.description}</p>
						</div>
					</div>
					
					<div class="org-stats">
						<div class="stat">
							<span class="stat-value">{org.user_count}</span>
							<span class="stat-label">Users</span>
						</div>
					</div>

					<div class="org-actions">
						<button class="btn-icon" on:click={() => openEditForm(org)}>
							<Edit class="w-4 h-4" />
						</button>
						<button class="btn-icon danger" on:click={() => deleteOrganization(org)}>
							<Trash2 class="w-4 h-4" />
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showForm}
	<div class="modal-overlay" on:click={closeForm}>
		<div class="modal" on:click|stopPropagation>
			<div class="modal-header">
				<h3>{editingOrg ? 'Edit Organization' : 'Create Organization'}</h3>
				<button class="close-btn" on:click={closeForm}>×</button>
			</div>

			<form on:submit|preventDefault={handleSubmit} class="org-form">
				<div class="form-group">
					<label for="name">Organization Name</label>
					<input
						id="name"
						type="text"
						bind:value={formData.name}
						placeholder="Enter organization name"
						required
					/>
				</div>

				<div class="form-group">
					<label for="description">Description</label>
					<textarea
						id="description"
						bind:value={formData.description}
						placeholder="Enter organization description"
						rows="3"
					></textarea>
				</div>

				<div class="form-actions">
					<button type="button" class="btn-secondary" on:click={closeForm}>
						Cancel
					</button>
					<button type="submit" class="btn-primary">
						{editingOrg ? 'Update' : 'Create'} Organization
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<style>
	.organization-settings {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.header h2 {
		margin: 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: #1f2937;
	}

	.organizations-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1rem;
	}

	.org-card {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.org-header {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
	}

	.org-icon {
		background: #3b82f6;
		color: white;
		padding: 0.75rem;
		border-radius: 8px;
		flex-shrink: 0;
	}

	.org-info h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
	}

	.org-info p {
		margin: 0;
		color: #6b7280;
		font-size: 0.875rem;
	}

	.org-stats {
		display: flex;
		gap: 1rem;
	}

	.stat {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 0.75rem;
		background: white;
		border-radius: 6px;
		border: 1px solid #e5e7eb;
	}

	.stat-value {
		font-size: 1.25rem;
		font-weight: 600;
		color: #1f2937;
	}

	.stat-label {
		font-size: 0.75rem;
		color: #6b7280;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.org-actions {
		display: flex;
		gap: 0.5rem;
		justify-content: flex-end;
	}

	.btn-primary {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
	}

	.btn-icon {
		padding: 0.5rem;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		cursor: pointer;
		color: #6b7280;
	}

	.btn-icon:hover {
		background: #f3f4f6;
	}

	.btn-icon.danger {
		color: #dc2626;
		border-color: #fca5a5;
	}

	.btn-icon.danger:hover {
		background: #fef2f2;
	}

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
		max-width: 500px;
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
		font-size: 1.5rem;
		cursor: pointer;
		color: #6b7280;
	}

	.org-form {
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
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

	input, textarea {
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
	}

	input:focus, textarea:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-actions {
		display: flex;
		gap: 1rem;
		justify-content: flex-end;
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid #e5e7eb;
	}

	.btn-secondary {
		padding: 0.75rem 1.5rem;
		background: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
	}

	.loading {
		text-align: center;
		padding: 2rem;
		color: #6b7280;
	}
</style>
