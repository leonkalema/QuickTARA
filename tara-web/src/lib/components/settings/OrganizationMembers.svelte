<script lang="ts">
	import { onMount } from 'svelte';
	import { Users, Plus, Edit, Trash2, Save, X } from '@lucide/svelte';
	import { notifications } from '$lib/stores/notifications';
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';
	import { API_BASE_URL } from '$lib/config';

	export let organizationId: string;
	export let organizationName: string;

	interface Member {
		user_id: string;
		email: string;
		username: string;
		first_name: string;
		last_name: string;
		role: string;
		joined_at: string;
	}

	interface User {
		user_id: string;
		email: string;
		username: string;
		first_name: string;
		last_name: string;
	}

	let members: Member[] = [];
	let availableUsers: User[] = [];
	let loading = false;
	let showAddForm = false;
	let editingUserId: string | null = null;
	let confirmingRemoveId: string | null = null;
	let canManageMembers = false;

	let addFormData = {
		user_id: '',
		role: 'analyst'
	};

	let editFormData: { [key: string]: { role: string } } = {};

	const roleOptions = [
		{ value: 'viewer', label: 'Viewer' },
		{ value: 'analyst', label: 'Analyst' },
		{ value: 'risk_manager', label: 'Risk Manager' },
		{ value: 'auditor', label: 'Auditor' },
		{ value: 'org_admin', label: 'Department Admin' }
	];

	onMount(() => {
		let unsubscribe: (() => void) | null = null;
		unsubscribe = authStore.subscribe((state) => {
			if (!state.isInitialized) return;
			const isSuperuser = (state.user as any)?.is_superuser === true;
			canManageMembers = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin');
			if (state.isAuthenticated && state.token) {
				loadMembers();
				loadAvailableUsers();
			}
			unsubscribe?.();
		});
		return () => unsubscribe?.();
	});

	async function loadMembers() {
		loading = true;
		try {
			const auth = get(authStore);
			const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
			const token = auth.token ?? tokenFromStorage;
			const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/members`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				members = await response.json();
			} else {
				notifications.show('Failed to load members', 'error');
			}
		} catch (error) {
			notifications.show('Failed to load members', 'error');
		} finally {
			loading = false;
		}
	}

	async function loadAvailableUsers() {
		try {
			const auth = get(authStore);
			const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
			const token = auth.token ?? tokenFromStorage;
			const response = await fetch(`${API_BASE_URL}/users`, {
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				const data = await response.json();
				// API returns array directly, not {users: []}
				availableUsers = Array.isArray(data) ? data : (data.users || []);
			}
		} catch (error) {
			console.error('Failed to load users:', error);
		}
	}

	function startEdit(member: Member) {
		editingUserId = member.user_id;
		editFormData[member.user_id] = {
			role: member.role
		};
	}

	function cancelEdit() {
		editingUserId = null;
		editFormData = {};
	}

	async function saveEdit(member: Member) {
		if (!canManageMembers) return;
		const formData = editFormData[member.user_id];
		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/members/${member.user_id}`, {
				method: 'PUT',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ role: formData.role })
			});

			if (response.ok) {
				notifications.show('Member role updated successfully', 'success');
				editingUserId = null;
				editFormData = {};
				await loadMembers();
			} else {
				throw new Error('Failed to update member role');
			}
		} catch (error) {
			notifications.show('Failed to update member role', 'error');
		}
	}

	async function addMember() {
		if (!canManageMembers) return;
		if (!addFormData.user_id) {
			notifications.show('Please select a user', 'error');
			return;
		}

		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/members`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(addFormData)
			});

			if (response.ok) {
				notifications.show('Member added successfully', 'success');
				showAddForm = false;
				addFormData = { user_id: '', role: 'analyst' };
				await loadMembers();
			} else {
				throw new Error('Failed to add member');
			}
		} catch (error) {
			notifications.show('Failed to add member', 'error');
		}
	}

	function cancelAdd() {
		showAddForm = false;
		addFormData = { user_id: '', role: 'analyst' };
	}

	function startRemove(member: Member) {
		confirmingRemoveId = member.user_id;
	}

	function cancelRemove() {
		confirmingRemoveId = null;
	}

	async function confirmRemove(member: Member) {
		if (!canManageMembers) return;

		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/members/${member.user_id}`, {
				method: 'DELETE',
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				notifications.show('Member removed', 'success');
				confirmingRemoveId = null;
				await loadMembers();
			} else {
				throw new Error('Failed to remove member');
			}
		} catch (error) {
			notifications.show('Failed to remove member', 'error');
			confirmingRemoveId = null;
		}
	}

	function getRoleLabel(role: string): string {
		const option = roleOptions.find(opt => opt.value === role);
		return option ? option.label : role;
	}

	function getAvailableUsersForAdd(): User[] {
		const memberUserIds = new Set(members.map(m => m.user_id));
		return availableUsers.filter(user => !memberUserIds.has(user.user_id));
	}
</script>

<div class="px-6 py-4">
	<div class="flex items-center justify-between mb-4">
		<div class="flex items-center space-x-2">
			<Users class="w-4 h-4" style="color: var(--color-text-secondary);" />
			<h4 class="text-xs font-semibold" style="color: var(--color-text-primary);">Team Members</h4>
			<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: var(--color-bg-elevated); color: var(--color-text-secondary);">
				{members.length}
			</span>
		</div>
		{#if canManageMembers}
			<button
				class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
				on:click={() => showAddForm = !showAddForm}
			>
				<Plus class="w-4 h-4 mr-1.5" />
				Add Member
			</button>
		{/if}
	</div>

	{#if showAddForm && canManageMembers}
		<div class="rounded-lg p-4 mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
			<h5 class="text-xs font-medium mb-3" style="color: var(--color-text-primary);">Add New Member</h5>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div>
					<label for="user-select" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">Select User</label>
					<select
						id="user-select"
						bind:value={addFormData.user_id}
						class="w-full px-3 py-2 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
					>
						<option value="">Choose a user...</option>
						{#each getAvailableUsersForAdd() as user}
							<option value={user.user_id}>{user.first_name} {user.last_name} ({user.email})</option>
						{/each}
					</select>
				</div>
				<div>
					<label for="role-select" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">Role</label>
					<select
						id="role-select"
						bind:value={addFormData.role}
						class="w-full px-3 py-2 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
					>
						{#each roleOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>
			</div>
			<div class="mt-4 flex justify-end space-x-3">
				<button
					class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
					on:click={cancelAdd}
				>
					<X class="w-4 h-4 mr-1.5" />
					Cancel
				</button>
				<button
					class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
					on:click={addMember}
				>
					<Plus class="w-4 h-4 mr-1.5" />
					Add Member
				</button>
			</div>
		</div>
	{/if}

	{#if loading}
		<div class="flex justify-center py-8">
			<div class="animate-spin rounded-full h-6 w-6 border-b-2" style="border-color: var(--color-accent-primary);"></div>
		</div>
	{:else if members.length === 0}
		<div class="text-center py-8">
			<div class="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3" style="background: var(--color-bg-elevated);">
				<Users class="w-5 h-5" style="color: var(--color-text-tertiary);" />
			</div>
			<p class="text-xs" style="color: var(--color-text-tertiary);">No members in this department yet</p>
			<p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">Add users to get started</p>
		</div>
	{:else}
		<!-- Members Table -->
		<div class="overflow-hidden rounded-lg" style="border: 1px solid var(--color-border-default);">
			<table class="min-w-full">
				<thead style="background: var(--color-bg-elevated);">
					<tr>
						<th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">
							Member
						</th>
						<th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">
							Role
						</th>
						<th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">
							Joined
						</th>
						{#if canManageMembers}
							<th class="px-4 py-2.5 text-right text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Actions</th>
						{:else}
							<th class="px-4 py-2.5 text-right" style="border-bottom: 1px solid var(--color-border-subtle);"></th>
						{/if}
					</tr>
				</thead>
				<tbody>
					{#each members as member}
						<tr style="border-bottom: 1px solid var(--color-border-subtle);">
							{#if editingUserId === member.user_id}
								<td class="px-4 py-3">
									<div class="flex items-center">
										<div class="w-7 h-7 rounded-full flex items-center justify-center mr-3" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
											<span class="text-[10px] font-medium" style="color: var(--color-text-secondary);">
												{member.first_name.charAt(0)}{member.last_name.charAt(0)}
											</span>
										</div>
										<div>
											<div class="text-xs font-medium" style="color: var(--color-text-primary);">{member.first_name} {member.last_name}</div>
											<div class="text-[10px]" style="color: var(--color-text-tertiary);">{member.email}</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									{#if canManageMembers}
									<select
										bind:value={editFormData[member.user_id].role}
										class="w-full px-2 py-1 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
									>
										{#each roleOptions as option}
											<option value={option.value}>{option.label}</option>
										{/each}
									</select>
									{:else}
									<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: color-mix(in srgb, var(--color-accent-primary) 15%, transparent); color: var(--color-accent-primary);">{getRoleLabel(member.role)}</span>
									{/if}
								</td>
								<td class="px-4 py-3 text-xs" style="color: var(--color-text-tertiary);">
									{new Date(member.joined_at).toLocaleDateString()}
								</td>
								<td class="px-4 py-3 text-right">
									<div class="flex justify-end space-x-2">
										{#if canManageMembers}
										<button
											class="inline-flex items-center px-2 py-1 text-xs font-medium rounded transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
											on:click={cancelEdit}
										>
											<X class="w-3 h-3 mr-1" />
											Cancel
										</button>
										<button
											class="inline-flex items-center px-2 py-1 text-xs font-medium rounded transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
											on:click={() => saveEdit(member)}
										>
											<Save class="w-3 h-3 mr-1" />
											Save
										</button>
										{/if}
									</div>
								</td>
							{:else}
								<td class="px-4 py-3">
									<div class="flex items-center">
										<div class="w-7 h-7 rounded-full flex items-center justify-center mr-3" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
											<span class="text-[10px] font-medium" style="color: var(--color-text-secondary);">
												{member.first_name.charAt(0)}{member.last_name.charAt(0)}
											</span>
										</div>
										<div>
											<div class="text-xs font-medium" style="color: var(--color-text-primary);">{member.first_name} {member.last_name}</div>
											<div class="text-[10px]" style="color: var(--color-text-tertiary);">{member.email}</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: color-mix(in srgb, var(--color-accent-primary) 15%, transparent); color: var(--color-accent-primary);">
										{getRoleLabel(member.role)}
									</span>
								</td>
								<td class="px-4 py-3 text-xs" style="color: var(--color-text-tertiary);">
									{new Date(member.joined_at).toLocaleDateString()}
								</td>
								<td class="px-4 py-3 text-right">
									{#if confirmingRemoveId === member.user_id}
										<div class="flex items-center justify-end space-x-2">
											<span class="text-xs" style="color: var(--color-text-tertiary);">Remove?</span>
											<button
												class="px-2 py-1 text-xs font-medium rounded transition-colors" style="background: var(--color-error); color: var(--color-text-inverse);"
												on:click={() => confirmRemove(member)}
											>
												Yes
											</button>
											<button
												class="px-2 py-1 text-xs font-medium rounded transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
												on:click={cancelRemove}
											>
												No
											</button>
										</div>
									{:else}
										<div class="flex justify-end space-x-1">
											{#if canManageMembers}
											<button
												class="p-1 rounded transition-colors" style="color: var(--color-text-tertiary);"
												on:click={() => startEdit(member)}
												title="Edit member role"
											>
												<Edit class="w-3.5 h-3.5" />
											</button>
											<button
												class="p-1 rounded transition-colors" style="color: var(--color-text-tertiary);"
												on:click={() => startRemove(member)}
												title="Remove member"
											>
												<Trash2 class="w-3.5 h-3.5" />
											</button>
											{/if}
										</div>
									{/if}
								</td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

