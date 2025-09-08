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
	let canManageMembers = false;

	let addFormData = {
		user_id: '',
		role: 'TARA_ANALYST'
	};

	let editFormData: { [key: string]: { role: string } } = {};

	const roleOptions = [
		{ value: 'VIEWER', label: 'Viewer' },
		{ value: 'TARA_ANALYST', label: 'TARA Analyst' },
		{ value: 'RISK_MANAGER', label: 'Risk Manager' },
		{ value: 'ORG_ADMIN', label: 'Organization Admin' }
	];

	onMount(() => {
		loadMembers();
		loadAvailableUsers();
		const isSuperuser = (get(authStore).user as any)?.is_superuser === true;
		canManageMembers = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin');
	});

	async function loadMembers() {
		loading = true;
		try {
			const auth = get(authStore);
			const response = await fetch(`${API_BASE_URL}/organizations/${organizationId}/members`, {
				headers: {
					'Authorization': `Bearer ${auth.token}`,
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
			const response = await fetch(`${API_BASE_URL}/users`, {
				headers: {
					'Authorization': `Bearer ${auth.token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				const data = await response.json();
				availableUsers = data.users || [];
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
				addFormData = { user_id: '', role: 'TARA_ANALYST' };
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
		addFormData = { user_id: '', role: 'TARA_ANALYST' };
	}

	async function removeMember(member: Member) {
		if (!canManageMembers) return;
		if (!confirm(`Remove ${member.first_name} ${member.last_name} from ${organizationName}?`)) return;

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
				notifications.show('Member removed successfully', 'success');
				await loadMembers();
			} else {
				throw new Error('Failed to remove member');
			}
		} catch (error) {
			notifications.show('Failed to remove member', 'error');
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
			<Users class="w-5 h-5 text-gray-600" />
			<h4 class="text-base font-semibold text-gray-900">Team Members</h4>
			<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
				{members.length}
			</span>
		</div>
		{#if canManageMembers}
			<button
				class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
				on:click={() => showAddForm = !showAddForm}
			>
				<Plus class="w-4 h-4 mr-1.5" />
				Add Member
			</button>
		{/if}
	</div>

	{#if showAddForm && canManageMembers}
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
			<h5 class="text-sm font-medium text-blue-900 mb-3">Add New Member</h5>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div>
					<label for="user-select" class="block text-sm font-medium text-gray-700 mb-1">Select User</label>
					<select
						id="user-select"
						bind:value={addFormData.user_id}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						<option value="">Choose a user...</option>
						{#each getAvailableUsersForAdd() as user}
							<option value={user.user_id}>{user.first_name} {user.last_name} ({user.email})</option>
						{/each}
					</select>
				</div>
				<div>
					<label for="role-select" class="block text-sm font-medium text-gray-700 mb-1">Role</label>
					<select
						id="role-select"
						bind:value={addFormData.role}
						class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
					>
						{#each roleOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>
			</div>
			<div class="mt-4 flex justify-end space-x-3">
				<button
					class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors"
					on:click={cancelAdd}
				>
					<X class="w-4 h-4 mr-1.5" />
					Cancel
				</button>
				<button
					class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors"
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
			<div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
		</div>
	{:else if members.length === 0}
		<div class="text-center py-8">
			<div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
				<Users class="w-6 h-6 text-gray-400" />
			</div>
			<p class="text-sm text-gray-500">No members in this organization yet</p>
			<p class="text-xs text-gray-400 mt-1">Add users to get started</p>
		</div>
	{:else}
		<!-- Members Table -->
		<div class="overflow-hidden border border-gray-200 rounded-lg">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Member
						</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Role
						</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Joined
						</th>
						{#if canManageMembers}
							<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
						{:else}
							<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
						{/if}
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each members as member}
						<tr class="hover:bg-gray-50">
							{#if editingUserId === member.user_id}
								<td class="px-4 py-3">
									<div class="flex items-center">
										<div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
											<span class="text-sm font-medium text-blue-600">
												{member.first_name.charAt(0)}{member.last_name.charAt(0)}
											</span>
										</div>
										<div>
											<div class="text-sm font-medium text-gray-900">{member.first_name} {member.last_name}</div>
											<div class="text-sm text-gray-500">{member.email}</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									{#if canManageMembers}
									<select
										bind:value={editFormData[member.user_id].role}
										class="w-full px-2 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
									>
										{#each roleOptions as option}
											<option value={option.value}>{option.label}</option>
										{/each}
									</select>
									{:else}
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{getRoleLabel(member.role)}</span>
									{/if}
								</td>
								<td class="px-4 py-3 text-sm text-gray-500">
									{new Date(member.joined_at).toLocaleDateString()}
								</td>
								<td class="px-4 py-3 text-right">
									<div class="flex justify-end space-x-2">
										{#if canManageMembers}
										<button
											class="inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 transition-colors"
											on:click={cancelEdit}
										>
											<X class="w-3 h-3 mr-1" />
											Cancel
										</button>
										<button
											class="inline-flex items-center px-2 py-1 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors"
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
										<div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
											<span class="text-sm font-medium text-blue-600">
												{member.first_name.charAt(0)}{member.last_name.charAt(0)}
											</span>
										</div>
										<div>
											<div class="text-sm font-medium text-gray-900">{member.first_name} {member.last_name}</div>
											<div class="text-sm text-gray-500">{member.email}</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
										{getRoleLabel(member.role)}
									</span>
								</td>
								<td class="px-4 py-3 text-sm text-gray-500">
									{new Date(member.joined_at).toLocaleDateString()}
								</td>
								<td class="px-4 py-3 text-right">
									<div class="flex justify-end space-x-1">
										{#if canManageMembers}
										<button
											class="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
											on:click={() => startEdit(member)}
											title="Edit member role"
										>
											<Edit class="w-4 h-4" />
										</button>
										<button
											class="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
											on:click={() => removeMember(member)}
											title="Remove member"
										>
											<Trash2 class="w-4 h-4" />
										</button>
										{/if}
									</div>
								</td>
							{/if}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

