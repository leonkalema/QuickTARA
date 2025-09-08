<script lang="ts">
	import { onMount } from 'svelte';
	import { ChevronDown, Building } from '@lucide/svelte';
	import { activeOrgStore, type ActiveOrganization } from '$lib/stores/activeOrganization';
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';
	import { API_BASE_URL } from '$lib/config';

	interface Organization {
		organization_id: string;
		name: string;
		description: string;
		role: string;
	}

	let organizations: Organization[] = [];
	let showDropdown = false;
	let loading = false;

	$: activeOrg = $activeOrgStore.organization;

	onMount(() => {
		loadUserOrganizations();
	});

	async function loadUserOrganizations() {
		loading = true;
		try {
			const auth = get(authStore);
			if (!auth.user) return;

			// Get user's organizations from token or API
			if (auth.user.organizations && auth.user.organizations.length > 0) {
				organizations = auth.user.organizations.map(org => ({
					organization_id: org.organization_id,
					name: org.name,
					description: '',
					role: org.role
				}));

				// Set first org as active if none selected
				if (!activeOrg && organizations.length > 0) {
					selectOrganization(organizations[0]);
				}
			} else {
				// Fallback: fetch from API if not in token
				const response = await fetch(`${API_BASE_URL}/organizations`, {
					headers: {
						'Authorization': `Bearer ${auth.token}`,
						'Content-Type': 'application/json'
					}
				});

				if (response.ok) {
					const data = await response.json();
					organizations = data.organizations || [];
					
					if (!activeOrg && organizations.length > 0) {
						selectOrganization(organizations[0]);
					}
				}
			}
		} catch (error) {
			console.error('Failed to load organizations:', error);
		} finally {
			loading = false;
		}
	}

	function selectOrganization(org: Organization) {
		const activeOrg: ActiveOrganization = {
			organization_id: org.organization_id,
			name: org.name,
			description: org.description,
			role: org.role
		};
		
		activeOrgStore.setActive(activeOrg);
		showDropdown = false;
	}

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as Element;
		if (!target.closest('.org-selector')) {
			showDropdown = false;
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div class="org-selector">
	<button class="selector-button" on:click={toggleDropdown} disabled={loading}>
		<div class="selector-content">
			<Building class="w-4 h-4" />
			<span class="org-name">
				{#if loading}
					Loading...
				{:else if activeOrg}
					{activeOrg.name}
				{:else}
					Select Organization
				{/if}
			</span>
		</div>
		<ChevronDown class="w-4 h-4 chevron" class:rotated={showDropdown} />
	</button>

	{#if showDropdown && organizations.length > 0}
		<div class="dropdown">
			{#each organizations as org}
				<button 
					class="dropdown-item" 
					class:active={activeOrg?.organization_id === org.organization_id}
					on:click={() => selectOrganization(org)}
				>
					<div class="org-info">
						<div class="org-name">{org.name}</div>
						<div class="org-role">{org.role}</div>
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.org-selector {
		position: relative;
		min-width: 200px;
	}

	.selector-button {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 0.5rem 0.75rem;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.875rem;
		transition: all 0.2s;
	}

	.selector-button:hover {
		border-color: #9ca3af;
	}

	.selector-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.selector-content {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #374151;
	}

	.org-name {
		font-weight: 500;
		max-width: 150px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.chevron {
		color: #6b7280;
		transition: transform 0.2s;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	.dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		z-index: 50;
		margin-top: 0.25rem;
		max-height: 200px;
		overflow-y: auto;
	}

	.dropdown-item {
		display: block;
		width: 100%;
		padding: 0.75rem;
		text-align: left;
		border: none;
		background: none;
		cursor: pointer;
		transition: background-color 0.2s;
		border-bottom: 1px solid #f3f4f6;
	}

	.dropdown-item:last-child {
		border-bottom: none;
	}

	.dropdown-item:hover {
		background: #f9fafb;
	}

	.dropdown-item.active {
		background: #eff6ff;
		color: #1d4ed8;
	}

	.org-info {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.dropdown-item .org-name {
		font-weight: 500;
		font-size: 0.875rem;
		max-width: none;
	}

	.org-role {
		font-size: 0.75rem;
		color: #6b7280;
		text-transform: capitalize;
	}

	.dropdown-item.active .org-role {
		color: #1e40af;
	}
</style>
