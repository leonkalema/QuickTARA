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

<div class="members-section">
	<div class="members-header">
		<div class="header-info">
			<Users class="w-5 h-5" />
			<h4>Members ({members.length})</h4>
		</div>
		<div class="header-note">
			<span class="note-text">Add users to organizations from the Users page</span>
		</div>
	</div>

	{#if loading}
		<div class="loading">Loading members...</div>
	{:else if members.length === 0}
		<div class="empty-state">No members found</div>
	{:else}
		<div class="members-list">
			{#each members as member}
				<div class="member-item">
					{#if editingUserId === member.user_id}
						<div class="member-edit">
							<div class="member-info">
								<div class="member-name">{member.first_name} {member.last_name}</div>
								<div class="member-email">{member.email}</div>
							</div>
							<div class="form-group">
								<select bind:value={editFormData[member.user_id].role}>
									{#each roleOptions as option}
										<option value={option.value}>{option.label}</option>
									{/each}
								</select>
							</div>
							<div class="member-actions">
								<button class="btn-secondary btn-sm" on:click={cancelEdit}>
									<X class="w-4 h-4" />
								</button>
								<button class="btn-primary btn-sm" on:click={() => saveEdit(member)}>
									<Save class="w-4 h-4" />
								</button>
							</div>
						</div>
					{:else}
						<div class="member-display">
							<div class="member-info">
								<div class="member-name">{member.first_name} {member.last_name}</div>
								<div class="member-email">{member.email}</div>
							</div>
							<div class="member-role">{getRoleLabel(member.role)}</div>
							<div class="member-actions">
								<button class="btn-icon" on:click={() => startEdit(member)}>
									<Edit class="w-4 h-4" />
								</button>
								<button class="btn-icon danger" on:click={() => removeMember(member)}>
									<Trash2 class="w-4 h-4" />
								</button>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.members-section {
		margin-top: 1.5rem;
		padding-top: 1.5rem;
		border-top: 1px solid #e5e7eb;
	}

	.members-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.header-info {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.header-info h4 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: #111827;
	}

	.header-note {
		display: flex;
		align-items: center;
	}

	.note-text {
		font-size: 0.75rem;
		color: #6b7280;
		font-style: italic;
	}

	.members-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.member-item {
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		padding: 0.75rem;
		background: white;
	}

	.member-display,
	.member-edit {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.member-info {
		flex: 1;
	}

	.member-name {
		font-weight: 500;
		color: #111827;
		font-size: 0.875rem;
	}

	.member-email {
		color: #6b7280;
		font-size: 0.75rem;
	}

	.member-role {
		color: #374151;
		font-size: 0.875rem;
		font-weight: 500;
		min-width: 120px;
	}

	.member-actions {
		display: flex;
		gap: 0.25rem;
	}

	.btn-icon {
		padding: 0.25rem;
		background: none;
		border: 1px solid #d1d5db;
		border-radius: 4px;
		cursor: pointer;
		color: #6b7280;
	}

	.btn-icon:hover {
		background: #f9fafb;
	}

	.btn-icon.danger {
		color: #dc2626;
		border-color: #fca5a5;
	}

	.btn-icon.danger:hover {
		background: #fef2f2;
	}

	.btn-secondary,
	.btn-primary {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.5rem 0.75rem;
		border-radius: 4px;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
	}

	.btn-sm {
		padding: 0.375rem 0.5rem;
		font-size: 0.75rem;
	}

	.btn-secondary {
		background: #f3f4f6;
		color: #374151;
		border: 1px solid #d1d5db;
	}

	.btn-primary {
		background: #3b82f6;
		color: white;
		border: 1px solid #3b82f6;
	}

	.loading,
	.empty-state {
		text-align: center;
		padding: 1rem;
		color: #6b7280;
		font-size: 0.875rem;
	}
</style>
