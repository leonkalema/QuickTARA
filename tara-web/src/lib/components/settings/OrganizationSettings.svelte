<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus, Edit, Trash2, Building, Save, X } from '@lucide/svelte';
	import { notifications } from '$lib/stores/notifications';
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';
	import { API_BASE_URL } from '$lib/config';
	import OrganizationMembers from './OrganizationMembers.svelte';

	interface Organization {
		organization_id: string;
		name: string;
		description: string;
		created_at: string;
		user_count: number;
	}

	let organizations: Organization[] = [];
	let loading = false;
	let editingId: string | null = null;
	let showCreateForm = false;

	let createFormData = {
		name: '',
		description: ''
	};

	let editFormData: { [key: string]: { name: string; description: string } } = {};

	onMount(() => {
		loadOrganizations();
	});

	async function loadOrganizations() {
		loading = true;
		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations`, {
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				}
			});
			if (response.ok) {
				const data = await response.json();
				organizations = data.organizations || [];
			} else {
				// Fallback to mock data if API not available
				organizations = [
					{
						organization_id: '1',
						name: 'Default Organization',
						description: 'Main organization for QuickTARA',
						created_at: '2024-01-01',
						user_count: 5
					}
				];
			}
		} catch (error) {
			// Fallback to mock data
			organizations = [
				{
					organization_id: '1',
					name: 'Default Organization',
					description: 'Main organization for QuickTARA',
					created_at: '2024-01-01',
					user_count: 5
				}
			];
		} finally {
			loading = false;
		}
	}

	function startEdit(org: Organization) {
		editingId = org.organization_id;
		editFormData[org.organization_id] = {
			name: org.name,
			description: org.description
		};
	}

	function cancelEdit() {
		editingId = null;
		editFormData = {};
	}

	async function saveEdit(org: Organization) {
		const formData = editFormData[org.organization_id];
		if (!formData.name.trim()) {
			notifications.show('Organization name is required', 'error');
			return;
		}

		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${org.organization_id}`, {
				method: 'PUT',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(formData)
			});

			if (response.ok) {
				notifications.show('Organization updated successfully', 'success');
				editingId = null;
				editFormData = {};
				await loadOrganizations();
			} else {
				throw new Error('Failed to update organization');
			}
		} catch (error) {
			notifications.show('Failed to save organization', 'error');
		}
	}

	async function createOrganization() {
		if (!createFormData.name.trim()) {
			notifications.show('Organization name is required', 'error');
			return;
		}

		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(createFormData)
			});

			if (response.ok) {
				notifications.show('Organization created successfully', 'success');
				showCreateForm = false;
				createFormData = { name: '', description: '' };
				await loadOrganizations();
			} else {
				throw new Error('Failed to create organization');
			}
		} catch (error) {
			notifications.show('Failed to create organization', 'error');
		}
	}

	function cancelCreate() {
		showCreateForm = false;
		createFormData = { name: '', description: '' };
	}

	async function deleteOrganization(org: Organization) {
		if (!confirm(`Are you sure you want to delete "${org.name}"?`)) return;

		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${org.organization_id}`, {
				method: 'DELETE',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				notifications.show('Organization deleted successfully', 'success');
				await loadOrganizations();
			} else {
				throw new Error('Failed to delete organization');
			}
		} catch (error) {
			notifications.show('Failed to delete organization', 'error');
		}
	}
</script>

<div class="organization-settings">
	<div class="header">
		<h2>Organization Management</h2>
		<button class="btn-primary" on:click={() => showCreateForm = true}>
			<Plus class="w-4 h-4" />
			Add Organization
		</button>
	</div>

	{#if showCreateForm}
		<div class="create-form">
			<h3>Create New Organization</h3>
			<div class="form-grid">
				<div class="form-group">
					<label for="create-name">Organization Name</label>
					<input
						id="create-name"
						type="text"
						bind:value={createFormData.name}
						placeholder="Enter organization name"
					/>
				</div>
				<div class="form-group">
					<label for="create-description">Description</label>
					<input
						id="create-description"
						type="text"
						bind:value={createFormData.description}
						placeholder="Enter description"
					/>
				</div>
			</div>
			<div class="form-actions">
				<button class="btn-secondary" on:click={cancelCreate}>
					<X class="w-4 h-4" />
					Cancel
				</button>
				<button class="btn-primary" on:click={createOrganization}>
					<Save class="w-4 h-4" />
					Create
				</button>
			</div>
		</div>
	{/if}

	{#if loading}
		<div class="loading">Loading organizations...</div>
	{:else}
		<div class="organizations-grid">
			{#each organizations as org}
				<div class="org-card">
					{#if editingId === org.organization_id}
						<div class="edit-form">
							<div class="form-group">
								<label for="edit-name-{org.organization_id}">Organization Name</label>
								<input
									id="edit-name-{org.organization_id}"
									type="text"
									bind:value={editFormData[org.organization_id].name}
									placeholder="Enter organization name"
								/>
							</div>
							<div class="form-group">
								<label for="edit-description-{org.organization_id}">Description</label>
								<input
									id="edit-description-{org.organization_id}"
									type="text"
									bind:value={editFormData[org.organization_id].description}
									placeholder="Enter description"
								/>
							</div>
							<div class="form-actions">
								<button class="btn-secondary" on:click={cancelEdit}>
									<X class="w-4 h-4" />
									Cancel
								</button>
								<button class="btn-primary" on:click={() => saveEdit(org)}>
									<Save class="w-4 h-4" />
									Save
								</button>
							</div>
						</div>
					{:else}
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
							<button class="btn-icon" on:click={() => startEdit(org)}>
								<Edit class="w-4 h-4" />
							</button>
							<button class="btn-icon danger" on:click={() => deleteOrganization(org)}>
								<Trash2 class="w-4 h-4" />
							</button>
						</div>
					{/if}

					<!-- Members section for each organization -->
					<OrganizationMembers 
						organizationId={org.organization_id} 
						organizationName={org.name} 
					/>
				</div>
			{/each}
		</div>
	{/if}
</div>

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

	.create-form,
	.edit-form {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
	}

	.create-form h3 {
		margin: 0 0 1rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #111827;
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: 500;
		color: #374151;
		font-size: 0.875rem;
	}

	.form-group input {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
		background: white;
	}

	.form-group input:focus {
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
