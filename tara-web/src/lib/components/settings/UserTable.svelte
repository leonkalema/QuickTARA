<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { notifications } from '$lib/stores/notifications';
  import { userApi, type User, type CreateUserRequest } from '$lib/api/userApi';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';
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
    status: 'active',
    organization_id: '',
    organization_role: 'TARA_ANALYST'
  };

  let organizations: Array<{organization_id: string, name: string}> = [];

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

  const orgRoles = [
    { value: 'VIEWER', label: 'Viewer' },
    { value: 'TARA_ANALYST', label: 'TARA Analyst' },
    { value: 'RISK_MANAGER', label: 'Risk Manager' },
    { value: 'ORG_ADMIN', label: 'Organization Admin' }
  ];

  onMount(() => {
    loadOrganizations();
  });

  async function loadOrganizations() {
    try {
      const auth = get(authStore);
      const response = await fetch('http://127.0.0.1:8080/api/organizations', {
        headers: {
          'Authorization': `Bearer ${auth.token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const data = await response.json();
        organizations = data.organizations || [];
        if (organizations.length > 0 && !newUser.organization_id) {
          newUser.organization_id = organizations[0].organization_id;
        }
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
    }
  }

  function resetForm() {
    newUser = {
      email: '',
      username: '',
      first_name: '',
      last_name: '',
      password: '',
      role: 'tara_analyst',
      status: 'active',
      organization_id: organizations.length > 0 ? organizations[0].organization_id : '',
      organization_role: 'TARA_ANALYST'
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
      
      // Add user to organization if selected
      if (newUser.organization_id && newUser.organization_role) {
        try {
          const auth = get(authStore);
          await fetch(`http://127.0.0.1:8080/api/organizations/${newUser.organization_id}/members`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${auth.token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              user_id: response.user_id,
              role: newUser.organization_role
            })
          });
        } catch (orgError) {
          console.error('Failed to add user to organization:', orgError);
          notifications.show('User created but failed to add to organization', 'warning');
        }
      }
      
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
      
      <!-- Organization Assignment -->
      <div class="grid grid-cols-2 gap-4 mb-4 p-4 bg-gray-50 rounded-md">
        <div>
          <label for="org-select" class="block text-sm font-medium text-gray-700 mb-1">Organization</label>
          <select id="org-select" bind:value={newUser.organization_id} class="px-3 py-2 border rounded-md w-full">
            <option value="">Select Organization</option>
            {#each organizations as org}
              <option value={org.organization_id}>{org.name}</option>
            {/each}
          </select>
        </div>
        <div>
          <label for="org-role-select" class="block text-sm font-medium text-gray-700 mb-1">Organization Role</label>
          <select id="org-role-select" bind:value={newUser.organization_role} class="px-3 py-2 border rounded-md w-full">
            {#each orgRoles as role}
              <option value={role.value}>{role.label}</option>
            {/each}
          </select>
        </div>
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
