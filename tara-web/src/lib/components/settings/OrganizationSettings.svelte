<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus, Edit, Trash2, Building, Save, X, Users, Calendar } from '@lucide/svelte';
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
	let canManageOrgs = false;

	let createFormData = {
		name: '',
		description: ''
	};

	let editFormData: { [key: string]: { name: string; description: string } } = {};

	onMount(() => {
		loadOrganizations();
		const isSuperuser = (get(authStore).user as any)?.is_superuser === true;
		canManageOrgs = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin');
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

<div class="min-h-screen bg-gray-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Header -->
		<div class="bg-white shadow-sm border-b border-gray-200 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-6 mb-8">
			<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="text-2xl font-semibold text-gray-900">Organizations</h1>
					<p class="mt-1 text-sm text-gray-500">Manage your organization structure and team members</p>
				</div>
				{#if canManageOrgs}
					<div class="mt-4 sm:mt-0">
						<button 
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
							on:click={() => showCreateForm = true}
						>
							<Plus class="w-4 h-4 mr-2" />
							New Organization
						</button>
					</div>
				{/if}
			</div>
		</div>

		{#if organizations.length === 0}
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 text-center py-16">
				<div class="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
					<Building class="w-8 h-8 text-blue-500" />
				</div>
				<h3 class="text-lg font-semibold text-gray-900 mb-2">No organizations yet</h3>
				<p class="text-gray-500 mb-6 max-w-md mx-auto">Get started by creating your first organization to manage teams and access controls.</p>
				{#if canManageOrgs}
					<button 
						class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
						on:click={() => showCreateForm = true}
					>
						<Plus class="w-4 h-4 mr-2" />
						Create Organization
					</button>
				{/if}
			</div>
		{/if}

		{#if showCreateForm && canManageOrgs}
			<div class="bg-white shadow-sm rounded-lg border border-gray-200 mb-8">
				<div class="px-6 py-4 border-b border-gray-200">
					<h3 class="text-lg font-semibold text-gray-900">Create New Organization</h3>
					<p class="mt-1 text-sm text-gray-500">Add a new organization to manage teams and permissions</p>
				</div>
				<div class="px-6 py-6">
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<div>
							<label for="create-name" class="block text-sm font-medium text-gray-700 mb-2">Organization Name *</label>
							<input
								id="create-name"
								type="text"
								bind:value={createFormData.name}
								placeholder="e.g., Engineering Team"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
								required
							/>
						</div>
						<div>
							<label for="create-description" class="block text-sm font-medium text-gray-700 mb-2">Description</label>
							<input
								id="create-description"
								type="text"
								bind:value={createFormData.description}
								placeholder="Brief description of the organization"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
							/>
						</div>
					</div>
					<div class="mt-6 flex justify-end space-x-3">
						<button 
							class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
							on:click={cancelCreate}
						>
							<X class="w-4 h-4 mr-2" />
							Cancel
						</button>
						<button 
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
							on:click={createOrganization}
						>
							<Save class="w-4 h-4 mr-2" />
							Create Organization
						</button>
					</div>
				</div>
			</div>
		{/if}

		{#if loading}
			<div class="flex justify-center py-12">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
			</div>
		{:else if organizations.length > 0}
			<div class="space-y-6">
				{#each organizations as org}
					<div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
						{#if editingId === org.organization_id}
							<div class="px-6 py-4 border-b border-gray-200">
								<h4 class="text-lg font-semibold text-gray-900">Edit Organization</h4>
							</div>
							<div class="px-6 py-6">
								<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
									<div>
										<label for="edit-name-{org.organization_id}" class="block text-sm font-medium text-gray-700 mb-2">Organization Name *</label>
										<input
											id="edit-name-{org.organization_id}"
											type="text"
											bind:value={editFormData[org.organization_id].name}
											placeholder="Enter organization name"
											class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
											required
										/>
									</div>
									<div>
										<label for="edit-description-{org.organization_id}" class="block text-sm font-medium text-gray-700 mb-2">Description</label>
										<input
											id="edit-description-{org.organization_id}"
											type="text"
											bind:value={editFormData[org.organization_id].description}
											placeholder="Brief description"
											class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
										/>
									</div>
								</div>
								<div class="mt-6 flex justify-end space-x-3">
									<button 
										class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
										on:click={cancelEdit}
									>
										<X class="w-4 h-4 mr-2" />
										Cancel
									</button>
									<button 
										class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
										on:click={() => saveEdit(org)}
									>
										<Save class="w-4 h-4 mr-2" />
										Save Changes
									</button>
								</div>
							</div>
						{:else}
							<!-- Organization Header -->
							<div class="px-6 py-4 border-b border-gray-200">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-4">
										<div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
											<Building class="w-6 h-6 text-blue-600" />
										</div>
										<div>
											<h3 class="text-lg font-semibold text-gray-900">{org.name}</h3>
											<p class="text-sm text-gray-500">{org.description || 'No description provided'}</p>
										</div>
									</div>
									{#if canManageOrgs}
										<div class="flex items-center space-x-2">
											<button 
												class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
												on:click={() => startEdit(org)}
											>
												<Edit class="w-4 h-4 mr-1.5" />
												Edit
											</button>
											<button 
												class="inline-flex items-center px-3 py-1.5 border border-red-300 shadow-sm text-sm font-medium rounded-lg text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
												on:click={() => deleteOrganization(org)}
											>
												<Trash2 class="w-4 h-4 mr-1.5" />
												Delete
											</button>
										</div>
									{/if}
								</div>
								
								<!-- Organization Stats -->
								<div class="mt-4 flex items-center justify-between">
									<div class="flex items-center space-x-6">
										<div class="flex items-center text-sm text-gray-500">
											<Users class="w-4 h-4 mr-1.5" />
											<span class="font-medium">{org.user_count}</span>
											<span class="ml-1">{org.user_count === 1 ? 'member' : 'members'}</span>
										</div>
										<div class="flex items-center text-sm text-gray-500">
											<Calendar class="w-4 h-4 mr-1.5" />
											<span>Created {new Date(org.created_at).toLocaleDateString()}</span>
										</div>
									</div>
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
										Active
									</span>
								</div>
							</div>

							<!-- Organization Members -->
							<div class="bg-gray-50">
								<OrganizationMembers 
									organizationId={org.organization_id} 
									organizationName={org.name} 
								/>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

