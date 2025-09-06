<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus, Edit, Trash2, Search } from '@lucide/svelte';
	import { authApi } from '$lib/api/auth';
	import { notifications } from '$lib/stores/notifications';
	import UserForm from './UserForm.svelte';

	interface User {
		user_id: string;
		email: string;
		username: string;
		first_name: string;
		last_name: string;
		status: string;
		is_verified: boolean;
		created_at: string;
		organizations: Array<{
			organization_id: string;
			name: string;
			role: string;
		}>;
	}

	let users: User[] = [];
	let filteredUsers: User[] = [];
	let searchTerm = '';
	let showUserForm = false;
	let editingUser: User | null = null;
	let loading = false;

	onMount(() => {
		loadUsers();
	});

	async function loadUsers() {
		loading = true;
		try {
			users = await authApi.getUsers();
			filterUsers();
		} catch (error) {
			notifications.show('Failed to load users', 'error');
		} finally {
			loading = false;
		}
	}

	function filterUsers() {
		if (!searchTerm) {
			filteredUsers = users;
		} else {
			filteredUsers = users.filter(user => 
				user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
				user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
				`${user.first_name} ${user.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
			);
		}
	}

	function openCreateForm() {
		editingUser = null;
		showUserForm = true;
	}

	function openEditForm(user: User) {
		editingUser = user;
		showUserForm = true;
	}

	function closeForm() {
		showUserForm = false;
		editingUser = null;
	}

	async function handleUserSaved() {
		closeForm();
		await loadUsers();
		notifications.show('User saved successfully', 'success');
	}

	async function deleteUser(user: User) {
		if (!confirm(`Are you sure you want to delete user ${user.email}?`)) return;

		try {
			await authApi.deleteUser(user.user_id);
			await loadUsers();
			notifications.show('User deleted successfully', 'success');
		} catch (error) {
			notifications.show('Failed to delete user', 'error');
		}
	}

	$: searchTerm, filterUsers();
</script>

<div class="user-management">
	<div class="header">
		<h2>User Management</h2>
		<button class="btn-primary" on:click={openCreateForm}>
			<Plus class="w-4 h-4" />
			Add User
		</button>
	</div>

	<div class="search-bar">
		<Search class="w-5 h-5 text-gray-400" />
		<input
			type="text"
			placeholder="Search users..."
			bind:value={searchTerm}
			class="search-input"
		/>
	</div>

	{#if loading}
		<div class="loading">Loading users...</div>
	{:else}
		<div class="users-table">
			<table>
				<thead>
					<tr>
						<th>Name</th>
						<th>Email</th>
						<th>Role</th>
						<th>Status</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredUsers as user}
						<tr>
							<td>{user.first_name} {user.last_name}</td>
							<td>{user.email}</td>
							<td>{user.organizations?.[0]?.role || 'No role'}</td>
							<td>
								<span class="status {user.status}">
									{user.status}
								</span>
							</td>
							<td>
								<div class="actions">
									<button class="btn-icon" on:click={() => openEditForm(user)}>
										<Edit class="w-4 h-4" />
									</button>
									<button class="btn-icon danger" on:click={() => deleteUser(user)}>
										<Trash2 class="w-4 h-4" />
									</button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

{#if showUserForm}
	<UserForm 
		user={editingUser} 
		on:saved={handleUserSaved}
		on:cancelled={closeForm}
	/>
{/if}

<style>
	.user-management {
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

	.search-bar {
		position: relative;
		display: flex;
		align-items: center;
		max-width: 400px;
	}

	.search-bar :global(svg) {
		position: absolute;
		left: 12px;
		z-index: 1;
	}

	.search-input {
		width: 100%;
		padding: 0.75rem 0.75rem 0.75rem 2.5rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.875rem;
	}

	.users-table {
		overflow-x: auto;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th, td {
		padding: 0.75rem 1rem;
		text-align: left;
		border-bottom: 1px solid #e5e7eb;
	}

	th {
		background: #f9fafb;
		font-weight: 600;
		color: #374151;
	}

	.status {
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: capitalize;
	}

	.status.active {
		background: #d1fae5;
		color: #065f46;
	}

	.status.inactive {
		background: #fee2e2;
		color: #991b1b;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
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
		background: none;
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

	.loading {
		text-align: center;
		padding: 2rem;
		color: #6b7280;
	}
</style>
