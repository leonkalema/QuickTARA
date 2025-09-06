<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '$lib/stores/notifications';
  import { userApi, type User, type CreateUserRequest } from '$lib/api/userApi';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';

  export let users: User[] = [];
  export let isAddingNew: boolean = false;

  const dispatch = createEventDispatcher();

  // Form state
  let newUser = {
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'tara_analyst',
    status: 'active'
  };

  // Delete confirmation
  let showDeleteDialog = false;
  let userToDelete: User | null = null;
  let isDeleting = false;

  // Inline editing
  let editingCell: { userId: string; field: string } | null = null;
  let editingValue = '';
  let isSaving = false;

  const roles = [
    'tool_admin',
    'org_admin', 
    'risk_manager',
    'tara_analyst',
    'auditor'
  ];

  function resetForm() {
    newUser = {
      email: '',
      username: '',
      first_name: '',
      last_name: '',
      password: '',
      role: 'tara_analyst',
      status: 'active'
    };
    dispatch('cancelAdd');
  }

  async function addNewUser() {
    if (!newUser.email.trim()) {
      notifications.show('Please enter an email address', 'error');
      return;
    }

    if (!newUser.password.trim()) {
      notifications.show('Please enter a password', 'error');
      return;
    }

    try {
      const userData: CreateUserRequest = {
        email: newUser.email,
        username: newUser.username,
        first_name: newUser.first_name,
        last_name: newUser.last_name,
        password: newUser.password,
        role: newUser.role,
        status: newUser.status
      };

      const response = await userApi.createUser(userData);
      users = [...users, response];
      resetForm();
      notifications.show('User created successfully', 'success');
      dispatch('userAdded', response);
    } catch (error) {
      console.error('Error creating user:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to create user';
      notifications.show(errorMessage, 'error');
    }
  }

  function confirmDelete(user: User) {
    userToDelete = user;
    showDeleteDialog = true;
  }

  async function deleteUser() {
    if (!userToDelete) return;
    
    isDeleting = true;
    try {
      await userApi.deleteUser(userToDelete.user_id);
      users = users.filter(u => u.user_id !== userToDelete!.user_id);
      notifications.show('User deleted successfully', 'success');
      dispatch('userDeleted', { user_id: userToDelete.user_id });
      
      showDeleteDialog = false;
      userToDelete = null;
    } catch (error) {
      console.error('Error deleting user:', error);
      notifications.show('Failed to delete user', 'error');
    } finally {
      isDeleting = false;
    }
  }

  function handleDeleteCancel() {
    showDeleteDialog = false;
    userToDelete = null;
    isDeleting = false;
  }

  // Inline editing functions
  function startEdit(user: User, field: string) {
    editingCell = { userId: user.user_id, field };
    editingValue = getFieldValue(user, field);
  }

  function getFieldValue(user: User, field: string): string {
    switch (field) {
      case 'email': return user.email;
      case 'first_name': return user.first_name;
      case 'last_name': return user.last_name;
      case 'username': return user.username;
      default: return '';
    }
  }

  async function saveEdit(user: User, field: string) {
    if (!editingCell || editingValue === getFieldValue(user, field)) {
      cancelEdit();
      return;
    }

    isSaving = true;
    try {
      const updates = { [field]: editingValue };
      const updatedUser = await userApi.updateUser(user.user_id, updates);
      
      const index = users.findIndex(u => u.user_id === user.user_id);
      if (index !== -1) {
        users[index] = updatedUser;
        users = [...users];
      }
      
      notifications.show('User updated successfully', 'success');
      cancelEdit();
    } catch (error) {
      console.error('Error updating user:', error);
      notifications.show('Failed to update user', 'error');
    } finally {
      isSaving = false;
    }
  }

  function cancelEdit() {
    editingCell = null;
    editingValue = '';
  }

  function handleKeyPress(event: KeyboardEvent, user: User, field: string) {
    if (event.key === 'Enter') {
      saveEdit(user, field);
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }

  async function toggleUserStatus(user: User) {
    try {
      const updatedUser = await userApi.toggleUserStatus(user.user_id);
      const index = users.findIndex(u => u.user_id === user.user_id);
      if (index !== -1) {
        users[index] = updatedUser;
        users = [...users];
      }
      notifications.show(`User ${updatedUser.status === 'active' ? 'activated' : 'deactivated'} successfully`, 'success');
    } catch (error) {
      console.error('Error toggling user status:', error);
      notifications.show('Failed to update user status', 'error');
    }
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }
</script>

<div class="space-y-6">
  {#if isAddingNew}
    <form on:submit|preventDefault={addNewUser} class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-6">
      <div class="grid grid-cols-2 gap-4 mb-4">
        <input bind:value={newUser.email} placeholder="Email address *" type="email" class="px-3 py-2 border rounded-md" />
        <input bind:value={newUser.username} placeholder="Username *" type="text" class="px-3 py-2 border rounded-md" />
        <input bind:value={newUser.first_name} placeholder="First Name *" type="text" class="px-3 py-2 border rounded-md" />
        <input bind:value={newUser.last_name} placeholder="Last Name *" type="text" class="px-3 py-2 border rounded-md" />
        <input bind:value={newUser.password} placeholder="Password *" type="password" class="px-3 py-2 border rounded-md" />
        <select bind:value={newUser.role} class="px-3 py-2 border rounded-md">
          {#each roles as role}
            <option value={role}>{role}</option>
          {/each}
        </select>
      </div>
      
      <div class="flex gap-2">
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium">
          Add User
        </button>
        <button type="button" on:click={resetForm} class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md font-medium">
          Cancel
        </button>
      </div>
    </form>
  {/if}

  <!-- Table -->
  <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each users as user (user.user_id)}
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4">
                {user.first_name} {user.last_name}
              </td>
              <td class="px-6 py-4">
                {user.email}
              </td>
              <td class="px-6 py-4">
                {user.is_superuser ? 'Tool Admin' : 'User'}
              </td>
              <td class="px-6 py-4">
                <button
                  on:click={() => toggleUserStatus(user)}
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}"
                >
                  {user.status === 'active' ? 'Active' : 'Inactive'}
                </button>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {formatDate(user.created_at)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <button
                  on:click={() => confirmDelete(user)}
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          {/each}
          
          {#if users.length === 0}
            <tr>
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                No users found. Add one above to get started.
              </td>
            </tr>
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- Delete Confirmation Dialog -->
<ConfirmDialog
  isOpen={showDeleteDialog}
  title="Delete User"
  message="Are you sure you want to delete this user? This action cannot be undone."
  confirmText="Delete"
  cancelText="Cancel"
  loading={isDeleting}
  on:confirm={deleteUser}
  on:cancel={handleDeleteCancel}
/>
