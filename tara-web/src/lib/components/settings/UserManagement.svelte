<script lang="ts">
	import { onMount } from 'svelte';
	import { notifications } from '$lib/stores/notifications';
	import { userApi, type User } from '$lib/api/userApi';
	import UserTable from './UserTable.svelte';
	import { canViewUserManagement, canCreateUsers } from '$lib/utils/permissions';
	import { Users, Plus, ShieldX } from '@lucide/svelte';

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
<div class="h-full">
	<UserTable 
		{users}
		{loading}
		isAddingNew={showAddForm}
		on:userAdded={handleUserAdded}
		on:userDeleted={handleUserDeleted}
		on:cancelAdd={() => showAddForm = false}
		on:toggleAddForm={() => showAddForm = !showAddForm}
	/>
</div>
{:else}
<div class="h-full flex items-center justify-center">
	<div class="text-center">
		<ShieldX class="w-10 h-10 mx-auto mb-3" style="color: var(--color-text-tertiary);" />
		<h2 class="text-xs font-semibold mb-1" style="color: var(--color-text-primary);">Access Restricted</h2>
		<p class="text-[11px]" style="color: var(--color-text-tertiary);">You don't have permission to view user management.</p>
	</div>
</div>
{/if}

