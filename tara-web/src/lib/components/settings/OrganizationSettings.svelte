<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Plus, Edit, Trash2, Building2, Users, ChevronDown, Search } from '@lucide/svelte';
	import { notifications } from '$lib/stores/notifications';
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';
	import { API_BASE_URL } from '$lib/config';
	import OrganizationMembers from './OrganizationMembers.svelte';
	import OrganizationCreateModal from './OrganizationCreateModal.svelte';
	import OrganizationEditRow from './OrganizationEditRow.svelte';
	import OrganizationProductPills from './OrganizationProductPills.svelte';
	import { productApi } from '$lib/api/productApi';
	import type { Product } from '$lib/types/product';
	import { productEvents } from '$lib/stores/productEvents';

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
	let canCreateOrgs = false;
	let expandedOrgId: string | null = null;
	let confirmDeleteId: string | null = null;
	let searchQuery = '';
	let userOrgIds: string[] = [];
	let productsByOrgId: Record<string, Product[]> = {};
	let unsubscribeProductEvents: (() => void) | null = null;

	let createName = '';
	let createDescription = '';
	let editName = '';
	let editDescription = '';

	$: filteredOrganizations = organizations.filter(org => 
		org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
		org.description?.toLowerCase().includes(searchQuery.toLowerCase())
	);

	onMount(() => {
		const auth = get(authStore);
		const isSuperuser = (auth.user as any)?.is_superuser === true;
		const isToolAdmin = isSuperuser || authStore.hasRole('tool_admin');
		const isOrgAdmin = authStore.hasRole('org_admin');
		
		canManageOrgs = isToolAdmin || isOrgAdmin;
		canCreateOrgs = isToolAdmin;
		
		userOrgIds = auth.user?.organizations?.map(o => o.organization_id) || [];
		
		loadOrganizations();
		loadProducts();
		unsubscribeProductEvents = productEvents.subscribe(() => {
			loadProducts();
		});
	});

	onDestroy(() => {
		unsubscribeProductEvents?.();
		unsubscribeProductEvents = null;
	});

	async function loadProducts() {
		try {
			const response = await productApi.getAll({ skip: 0, limit: 500 });
			const grouped: Record<string, Product[]> = {};
			for (const scope of response.scopes) {
				const orgId = scope.organization_id ?? '';
				if (!grouped[orgId]) grouped[orgId] = [];
				grouped[orgId].push(scope);
			}
			productsByOrgId = grouped;
		} catch {
			productsByOrgId = {};
		}
	}

	async function loadOrganizations() {
		loading = true;
		try {
			const auth = get(authStore);
			const isSuperuser = (auth.user as any)?.is_superuser === true;
			const isToolAdmin = isSuperuser || authStore.hasRole('tool_admin');
			
			const response = await fetch(`${API_BASE_URL}/organizations`, {
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				}
			});
			if (response.ok) {
				const data = await response.json();
				let allOrgs = data.organizations || [];
				
				if (!isToolAdmin && userOrgIds.length > 0) {
					organizations = allOrgs.filter((org: Organization) => userOrgIds.includes(org.organization_id));
				} else {
					organizations = allOrgs;
				}
			} else {
				organizations = [];
			}
		} catch (error) {
			organizations = [];
		} finally {
			loading = false;
		}
	}

	function startEdit(org: Organization) {
		editingId = org.organization_id;
		editName = org.name;
		editDescription = org.description;
	}

	function cancelEdit() {
		editingId = null;
		editName = '';
		editDescription = '';
	}

	async function saveEdit(org: Organization) {
		if (!editName.trim()) {
			notifications.show('Department name is required', 'error');
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
				body: JSON.stringify({ name: editName, description: editDescription })
			});

			if (response.ok) {
				notifications.show('Department updated successfully', 'success');
				editingId = null;
				editName = '';
				editDescription = '';
				await loadOrganizations();
			} else {
				throw new Error('Failed to update department');
			}
		} catch (error) {
			notifications.show('Failed to save department', 'error');
		}
	}

	async function createOrganization() {
		if (!createName.trim()) {
			notifications.show('Department name is required', 'error');
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
				body: JSON.stringify({ name: createName, description: createDescription })
			});

			if (response.ok) {
				notifications.show('Department created successfully', 'success');
				showCreateForm = false;
				createName = '';
				createDescription = '';
				await loadOrganizations();
			} else {
				throw new Error('Failed to create department');
			}
		} catch (error) {
			notifications.show('Failed to create department', 'error');
		}
	}

	function cancelCreate() {
		showCreateForm = false;
		createName = '';
		createDescription = '';
	}

	function startDelete(org: Organization) {
		confirmDeleteId = org.organization_id;
	}

	function cancelDelete() {
		confirmDeleteId = null;
	}

	async function confirmDelete(org: Organization) {
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
				notifications.show('Department deleted', 'success');
				confirmDeleteId = null;
				await loadOrganizations();
			} else {
				throw new Error('Failed to delete department');
			}
		} catch (error) {
			notifications.show('Failed to delete department', 'error');
			confirmDeleteId = null;
		}
	}

	function toggleExpand(orgId: string) {
		expandedOrgId = expandedOrgId === orgId ? null : orgId;
	}
</script>

<div class="h-full" style="background: var(--color-bg-primary);">
	<div class="px-6 py-4" style="background: var(--color-bg-surface); border-bottom: 1px solid var(--color-border-default);">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-3">
				<Building2 class="w-5 h-5" style="color: var(--color-text-secondary);" />
				<h1 class="text-sm font-semibold" style="color: var(--color-text-primary);">Departments</h1>
				<span class="text-xs" style="color: var(--color-text-tertiary);">({organizations.length})</span>
			</div>
			<div class="flex items-center space-x-3">
				<!-- Search -->
				<div class="relative">
					<Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color: var(--color-text-tertiary);" />
					<input
						type="text"
						placeholder="Search departments..."
						bind:value={searchQuery}
						class="pl-9 pr-4 py-2 w-64 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
					/>
				</div>
				{#if canCreateOrgs}
					<button 
						class="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
						on:click={() => showCreateForm = true}
					>
						<Plus class="w-4 h-4 mr-1.5" />
						New
					</button>
				{/if}
			</div>
		</div>
	</div>

	<!-- Content -->
	<div class="p-6">
		{#if loading}
			<div class="flex justify-center py-12">
				<div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary);"></div>
			</div>
		{:else if filteredOrganizations.length === 0 && organizations.length === 0}
			<div class="rounded-lg text-center py-12" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
				<Building2 class="w-10 h-10 mx-auto mb-3" style="color: var(--color-text-tertiary);" />
				<p class="text-xs font-medium" style="color: var(--color-text-primary);">No departments found</p>
				<p class="text-xs mt-1" style="color: var(--color-text-tertiary);">
					{#if canCreateOrgs}
						Create your first department to get started
					{:else}
						You are not assigned to any departments
					{/if}
				</p>
				{#if canCreateOrgs}
					<button 
						class="mt-4 inline-flex items-center px-4 py-2 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
						on:click={() => showCreateForm = true}
					>
						<Plus class="w-4 h-4 mr-1.5" />
						Create Department
					</button>
				{/if}
			</div>
		{:else if filteredOrganizations.length === 0}
			<div class="rounded-lg text-center py-12" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
				<Search class="w-10 h-10 mx-auto mb-3" style="color: var(--color-text-tertiary);" />
				<p class="text-xs font-medium" style="color: var(--color-text-primary);">No results found</p>
				<p class="text-xs mt-1" style="color: var(--color-text-tertiary);">Try a different search term</p>
			</div>
		{:else}
			<!-- Department Table -->
			<div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
				<table class="w-full">
					<thead>
						<tr style="background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border-subtle);">
							<th class="text-left px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary);">Department</th>
							<th class="text-left px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary);">Members</th>
							<th class="text-left px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary);">Created</th>
							<th class="text-right px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider w-32" style="color: var(--color-text-tertiary);">Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredOrganizations as org}
							<!-- Main Row -->
							<tr class="transition-colors" style="border-bottom: 1px solid var(--color-border-subtle); {expandedOrgId === org.organization_id ? 'background: var(--color-bg-elevated);' : ''}">
								<td class="px-4 py-3">
									<button 
										class="flex items-center space-x-3 text-left w-full"
										on:click={() => toggleExpand(org.organization_id)}
									>
										<ChevronDown class="w-4 h-4 transition-transform {expandedOrgId === org.organization_id ? 'rotate-180' : ''}" style="color: var(--color-text-tertiary);" />
										<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold" style="background: var(--color-bg-elevated); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">
											{org.name.substring(0, 2).toUpperCase()}
										</div>
										<div>
											<div class="text-xs font-medium" style="color: var(--color-text-primary);">{org.name}</div>
											{#if org.description}
												<div class="text-[10px] truncate max-w-xs" style="color: var(--color-text-tertiary);">{org.description}</div>
											{/if}
											<OrganizationProductPills products={productsByOrgId[org.organization_id] ?? []} />
										</div>
									</button>
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center space-x-2">
										<Users class="w-4 h-4" style="color: var(--color-text-tertiary);" />
										<span class="text-xs" style="color: var(--color-text-secondary);">{org.user_count}</span>
									</div>
								</td>
								<td class="px-4 py-3">
									<span class="text-xs" style="color: var(--color-text-tertiary);">{new Date(org.created_at).toLocaleDateString()}</span>
								</td>
								<td class="px-4 py-3 text-right">
									{#if confirmDeleteId === org.organization_id}
										<div class="flex items-center justify-end space-x-2">
											<span class="text-xs" style="color: var(--color-text-tertiary);">Delete?</span>
											<button
												class="px-2 py-1 text-xs font-medium rounded transition-colors" style="background: var(--color-error); color: var(--color-text-inverse);"
												on:click={() => confirmDelete(org)}
											>
												Yes
											</button>
											<button
												class="px-2 py-1 text-xs font-medium rounded transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
												on:click={cancelDelete}
											>
												No
											</button>
										</div>
									{:else if canManageOrgs}
										<div class="flex items-center justify-end space-x-1">
											<button
												class="p-1.5 rounded transition-colors" style="color: var(--color-text-tertiary);"
												on:click={() => startEdit(org)}
												title="Edit"
											>
												<Edit class="w-3.5 h-3.5" />
											</button>
											<button
												class="p-1.5 rounded transition-colors" style="color: var(--color-text-tertiary);"
												on:click={() => startDelete(org)}
												title="Delete"
											>
												<Trash2 class="w-3.5 h-3.5" />
											</button>
										</div>
									{/if}
								</td>
							</tr>
							
							{#if editingId === org.organization_id}
								<OrganizationEditRow bind:name={editName} bind:description={editDescription} on:cancel={cancelEdit} on:save={() => saveEdit(org)} />
							{/if}
							
							<!-- Expanded Members Row -->
							{#if expandedOrgId === org.organization_id && editingId !== org.organization_id}
								<tr>
									<td colspan="4" style="background: var(--color-bg-elevated); border-top: 1px solid var(--color-border-subtle);">
										<OrganizationMembers 
											organizationId={org.organization_id} 
											organizationName={org.name} 
										/>
									</td>
								</tr>
							{/if}
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>

	{#if canCreateOrgs}
		<OrganizationCreateModal bind:name={createName} bind:description={createDescription} isOpen={showCreateForm} on:cancel={cancelCreate} on:create={createOrganization} />
	{/if}
</div>

