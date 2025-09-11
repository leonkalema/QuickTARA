<script lang="ts">
	import { onMount } from 'svelte';
	import { notifications } from '$lib/stores/notifications';
	import { userApi, type User } from '$lib/api/userApi';
	import UserTable from './UserTable.svelte';
	import { canViewUserManagement, canCreateUsers } from '$lib/utils/permissions';

	let users: User[] = [];
	let loading = false;
	let showAddForm = false;

	onMount(() => {
		loadUsers();
	});

	async function loadUsers() {
		loading = true;
		try {
			users = await userApi.getUsers();
		} catch (error) {
			console.error('Error loading users:', error);
			notifications.show('Failed to load users', 'error');
		} finally {
			loading = false;
		}
	}

	function handleUserAdded(event: CustomEvent) {
		users = [...users, event.detail];
		showAddForm = false;
	}

	function handleUserDeleted(event: CustomEvent) {
		users = users.filter(u => u.user_id !== event.detail.user_id);
	}
</script>

{#if canViewUserManagement()}
<div class="space-y-6">
	<!-- Header -->
	<div class="flex justify-between items-center">
		<div>
			<h2 class="text-2xl font-bold text-gray-900">User Management</h2>
			<p class="text-gray-600 mt-1">Manage user accounts and permissions</p>
		</div>
		{#if canCreateUsers()}
			<button
				on:click={() => showAddForm = !showAddForm}
				class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
			>
				{showAddForm ? 'Cancel' : 'Add User'}
			</button>
		{/if}
	</div>

	<!-- Loading State -->
	{#if loading}
		<div class="flex justify-center py-8">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
		</div>
	{:else}
		<!-- User Table -->
		<UserTable 
			{users}
			isAddingNew={showAddForm}
			on:userAdded={handleUserAdded}
			on:userDeleted={handleUserDeleted}
			on:cancelAdd={() => showAddForm = false}
		/>
	{/if}
</div>
{:else}
<div class="flex flex-col items-center justify-center py-12">
	<div class="text-center">
		<h2 class="text-xl font-semibold text-gray-900 mb-2">Access Restricted</h2>
		<p class="text-gray-600">You don't have permission to view user management.</p>
		<p class="text-sm text-gray-500 mt-2">Contact your administrator if you need access.</p>
	</div>
</div>
{/if}

