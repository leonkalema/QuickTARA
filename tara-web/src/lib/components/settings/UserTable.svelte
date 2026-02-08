<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { notifications } from '$lib/stores/notifications';
  import { userApi, type User, type CreateUserRequest } from '$lib/api/userApi';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';
  import { API_BASE_URL } from '$lib/config';
  import { UserRole, OrgRole, getAllOrgRoles, getOrgRoleLabel } from '$lib/types/roles';
  import { canCreateUsers, canEditUsers, canDeleteUsers } from '$lib/utils/permissions';
  import { Users, Plus, Search, Edit, Trash2, Key, X, Shield, UserCheck, UserX } from '@lucide/svelte';

  export let users: User[] = [];
  export let loading: boolean = false;
  export let isAddingNew: boolean = false;

  const dispatch = createEventDispatcher();

  let searchQuery = '';
  let statusFilter = 'all';
  
  $: filteredUsers = users.filter(user => {
    const matchesSearch = searchQuery === '' || 
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  let currentPage = 1;
  let pageSize = 10;
  $: totalPages = Math.ceil(filteredUsers.length / pageSize);
  $: paginatedUsers = filteredUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  
  $: if (searchQuery || statusFilter) {
    currentPage = 1;
  }

  let newUser = {
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    status: 'active',
    organization_id: '',
    organization_role: OrgRole.ANALYST
  };

  let organizations: Array<{organization_id: string, name: string}> = [];
  let userOrgIds: string[] = [];
  let isToolAdmin = false;
  let confirmDeleteId: string | null = null;
  let editingUserId: string | null = null;
  let editFormData = { email: '', username: '', first_name: '', last_name: '', status: 'active' };
  let showPasswordReset: string | null = null;
  let newPassword = '';
  let isSaving = false;

  const orgRoles = getAllOrgRoles().map(role => ({
    value: role,
    label: getOrgRoleLabel(role)
  }));

  onMount(() => {
    const auth = get(authStore);
    const isSuperuser = (auth.user as any)?.is_superuser === true;
    isToolAdmin = isSuperuser || authStore.hasRole('tool_admin');
    userOrgIds = auth.user?.organizations?.map(o => o.organization_id) || [];
    
    loadOrganizations();
  });

  async function loadOrganizations() {
    try {
      const auth = get(authStore);
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
          organizations = allOrgs.filter((org: any) => userOrgIds.includes(org.organization_id));
        } else {
          organizations = allOrgs;
        }
        
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
      status: 'active',
      organization_id: organizations.length > 0 ? organizations[0].organization_id : '',
      organization_role: OrgRole.ANALYST
    };
    dispatch('cancelAdd');
  }

  async function addNewUser() {
    if (!newUser.email.trim() || !newUser.password.trim()) {
      notifications.show('Email and password are required', 'error');
      return;
    }
    if (!newUser.organization_id || !newUser.organization_role) {
      notifications.show('Department and role are required', 'error');
      return;
    }

    isSaving = true;
    try {
      const userData: CreateUserRequest = {
        email: newUser.email,
        username: newUser.username,
        first_name: newUser.first_name,
        last_name: newUser.last_name,
        password: newUser.password,
        role: newUser.organization_role.toLowerCase() as UserRole,
        status: newUser.status
      };

      const response = await userApi.createUser(userData);
      
      if (newUser.organization_id && newUser.organization_role) {
        try {
          const auth = get(authStore);
          await fetch(`${API_BASE_URL}/organizations/${newUser.organization_id}/members`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${auth.token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              user_id: response.user_id,
              role: newUser.organization_role.toLowerCase()
            })
          });
        } catch (orgError) {
          notifications.show('User created but failed to add to department', 'warning');
        }
      }
      
      resetForm();
      notifications.show('User created', 'success');
      dispatch('userAdded', response);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create user';
      notifications.show(errorMessage, 'error');
    } finally {
      isSaving = false;
    }
  }

  function startDelete(userId: string) {
    confirmDeleteId = userId;
  }

  function cancelDelete() {
    confirmDeleteId = null;
  }

  async function confirmDelete(user: User) {
    try {
      await userApi.deleteUser(user.user_id);
      notifications.show('User deleted', 'success');
      dispatch('userDeleted', { user_id: user.user_id });
      confirmDeleteId = null;
    } catch (error) {
      notifications.show('Failed to delete user', 'error');
      confirmDeleteId = null;
    }
  }

  function startEdit(user: User) {
    editingUserId = user.user_id;
    editFormData = {
      email: user.email,
      username: user.username,
      first_name: user.first_name,
      last_name: user.last_name,
      status: user.status
    };
  }

  function cancelEdit() {
    editingUserId = null;
  }

  async function saveEdit(user: User) {
    isSaving = true;
    try {
      const updatedUser = await userApi.updateUser(user.user_id, editFormData);
      const index = users.findIndex(u => u.user_id === user.user_id);
      if (index !== -1) {
        users[index] = updatedUser;
        users = [...users];
      }
      notifications.show('User updated', 'success');
      editingUserId = null;
    } catch (error) {
      notifications.show('Failed to update user', 'error');
    } finally {
      isSaving = false;
    }
  }

  function openPasswordReset(userId: string) {
    showPasswordReset = userId;
    newPassword = '';
  }

  function cancelPasswordReset() {
    showPasswordReset = null;
    newPassword = '';
  }

  async function resetPassword(user: User) {
    if (!newPassword) return;
    
    isSaving = true;
    try {
      const auth = get(authStore);
      const response = await fetch(`${API_BASE_URL}/users/${user.user_id}/reset-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${auth.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ new_password: newPassword })
      });
      
      if (!response.ok) throw new Error('Failed');
      
      notifications.show('Password reset', 'success');
      showPasswordReset = null;
      newPassword = '';
    } catch (error) {
      notifications.show('Failed to reset password', 'error');
    } finally {
      isSaving = false;
    }
  }

  async function toggleStatus(user: User) {
    try {
      const updatedUser = await userApi.toggleUserStatus(user.user_id);
      const index = users.findIndex(u => u.user_id === user.user_id);
      if (index !== -1) {
        users[index] = updatedUser;
        users = [...users];
      }
      notifications.show(`User ${updatedUser.status === 'active' ? 'activated' : 'deactivated'}`, 'success');
    } catch (error) {
      notifications.show('Failed to update status', 'error');
    }
  }

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString();
  }
</script>

<div class="h-full">
  <!-- Header -->
  <div class="bg-white border-b border-slate-200 px-6 py-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Users class="w-5 h-5 text-slate-600" />
        <h1 class="text-lg font-semibold text-slate-900">Users</h1>
        <span class="text-sm text-slate-500">({users.length})</span>
      </div>
      <div class="flex items-center space-x-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search users..."
            bind:value={searchQuery}
            class="pl-9 pr-4 py-2 w-64 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-slate-50"
          />
        </div>
        <select
          bind:value={statusFilter}
          class="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        {#if canCreateUsers()}
          <button 
            class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            on:click={() => dispatch('toggleAddForm')}
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
        <div class="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
      </div>
    {:else if filteredUsers.length === 0 && users.length === 0}
      <div class="bg-white rounded-lg border border-slate-200 text-center py-12">
        <Users class="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-600 font-medium">No users yet</p>
        <p class="text-sm text-slate-400 mt-1">Create your first user to get started</p>
      </div>
    {:else if filteredUsers.length === 0}
      <div class="bg-white rounded-lg border border-slate-200 text-center py-12">
        <Search class="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <p class="text-slate-600 font-medium">No results found</p>
        <p class="text-sm text-slate-400 mt-1">Try a different search term</p>
      </div>
    {:else}
      <div class="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-200">
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">User</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider w-40">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <!-- Add User Row -->
            {#if isAddingNew && canCreateUsers()}
              <tr class="bg-blue-50">
                <td colspan="6" class="px-4 py-4">
                  <div class="space-y-3">
                    <div class="grid grid-cols-4 gap-3">
                      <input
                        type="email"
                        bind:value={newUser.email}
                        placeholder="Email *"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        bind:value={newUser.username}
                        placeholder="Username"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        bind:value={newUser.first_name}
                        placeholder="First Name"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        bind:value={newUser.last_name}
                        placeholder="Last Name"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div class="grid grid-cols-4 gap-3">
                      <input
                        type="password"
                        bind:value={newUser.password}
                        placeholder="Password *"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <select
                        bind:value={newUser.organization_id}
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Department *</option>
                        {#each organizations as org}
                          <option value={org.organization_id}>{org.name}</option>
                        {/each}
                      </select>
                      <select
                        bind:value={newUser.organization_role}
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        {#each orgRoles as role}
                          <option value={role.value}>{role.label}</option>
                        {/each}
                      </select>
                      <div class="flex space-x-2">
                        <button
                          on:click={addNewUser}
                          disabled={isSaving}
                          class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
                        >
                          {isSaving ? 'Adding...' : 'Add User'}
                        </button>
                        <button
                          on:click={resetForm}
                          class="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            {/if}

            {#each paginatedUsers as user (user.user_id)}
              <!-- Main Row -->
              <tr class="hover:bg-slate-50 transition-colors">
                <td class="px-4 py-3">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-slate-500 to-slate-600 flex items-center justify-center text-white text-xs font-bold">
                      {user.first_name?.charAt(0) || ''}{user.last_name?.charAt(0) || ''}
                    </div>
                    <div>
                      <div class="font-medium text-slate-900">{user.first_name} {user.last_name}</div>
                      <div class="text-xs text-slate-500">@{user.username}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-sm text-slate-700">{user.email}</span>
                </td>
                <td class="px-4 py-3">
                  {#if user.is_superuser}
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                      <Shield class="w-3 h-3 mr-1" />
                      Admin
                    </span>
                  {:else}
                    <span class="text-sm text-slate-500">User</span>
                  {/if}
                </td>
                <td class="px-4 py-3">
                  <button
                    on:click={() => toggleStatus(user)}
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium transition-colors {user.status === 'active' ? 'bg-green-100 text-green-800 hover:bg-green-200' : 'bg-red-100 text-red-800 hover:bg-red-200'}"
                    disabled={user.is_superuser}
                  >
                    {#if user.status === 'active'}
                      <UserCheck class="w-3 h-3 mr-1" />
                    {:else}
                      <UserX class="w-3 h-3 mr-1" />
                    {/if}
                    {user.status}
                  </button>
                </td>
                <td class="px-4 py-3">
                  <span class="text-sm text-slate-500">{formatDate(user.created_at)}</span>
                </td>
                <td class="px-4 py-3 text-right">
                  {#if confirmDeleteId === user.user_id}
                    <div class="flex items-center justify-end space-x-2">
                      <span class="text-xs text-slate-500">Delete?</span>
                      <button
                        class="px-2 py-1 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded transition-colors"
                        on:click={() => confirmDelete(user)}
                      >
                        Yes
                      </button>
                      <button
                        class="px-2 py-1 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded transition-colors"
                        on:click={cancelDelete}
                      >
                        No
                      </button>
                    </div>
                  {:else if user.is_superuser}
                    <span class="text-xs text-slate-400">Protected</span>
                  {:else}
                    <div class="flex items-center justify-end space-x-1">
                      {#if canEditUsers()}
                        <button
                          class="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded transition-colors"
                          on:click={() => startEdit(user)}
                          title="Edit"
                        >
                          <Edit class="w-4 h-4" />
                        </button>
                        <button
                          class="p-1.5 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded transition-colors"
                          on:click={() => openPasswordReset(user.user_id)}
                          title="Reset Password"
                        >
                          <Key class="w-4 h-4" />
                        </button>
                      {/if}
                      {#if canDeleteUsers()}
                        <button
                          class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                          on:click={() => startDelete(user.user_id)}
                          title="Delete"
                        >
                          <Trash2 class="w-4 h-4" />
                        </button>
                      {/if}
                    </div>
                  {/if}
                </td>
              </tr>

              <!-- Edit Row -->
              {#if editingUserId === user.user_id}
                <tr class="bg-amber-50">
                  <td colspan="6" class="px-4 py-4">
                    <div class="flex items-end space-x-3">
                      <div class="flex-1 grid grid-cols-4 gap-3">
                        <div>
                          <label class="block text-xs font-medium text-slate-600 mb-1">Email</label>
                          <input
                            type="email"
                            bind:value={editFormData.email}
                            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-slate-600 mb-1">Username</label>
                          <input
                            type="text"
                            bind:value={editFormData.username}
                            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-slate-600 mb-1">First Name</label>
                          <input
                            type="text"
                            bind:value={editFormData.first_name}
                            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-slate-600 mb-1">Last Name</label>
                          <input
                            type="text"
                            bind:value={editFormData.last_name}
                            class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                      <div class="flex space-x-2">
                        <button
                          on:click={cancelEdit}
                          class="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          on:click={() => saveEdit(user)}
                          disabled={isSaving}
                          class="px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
                        >
                          {isSaving ? 'Saving...' : 'Save'}
                        </button>
                      </div>
                    </div>
                  </td>
                </tr>
              {/if}

              <!-- Password Reset Row -->
              {#if showPasswordReset === user.user_id}
                <tr class="bg-amber-50">
                  <td colspan="6" class="px-4 py-4">
                    <div class="flex items-center space-x-3">
                      <span class="text-sm text-slate-600">New password for <strong>{user.email}</strong>:</span>
                      <input
                        type="password"
                        bind:value={newPassword}
                        placeholder="Enter new password"
                        class="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                      />
                      <button
                        on:click={cancelPasswordReset}
                        class="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        on:click={() => resetPassword(user)}
                        disabled={isSaving || !newPassword}
                        class="px-3 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {isSaving ? 'Resetting...' : 'Reset'}
                      </button>
                    </div>
                  </td>
                </tr>
              {/if}
            {/each}
          </tbody>
        </table>

        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="px-4 py-3 border-t border-slate-200 flex items-center justify-between">
            <div class="text-sm text-slate-500">
              {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, filteredUsers.length)} of {filteredUsers.length}
            </div>
            <div class="flex items-center space-x-1">
              <button
                on:click={() => currentPage--}
                disabled={currentPage === 1}
                class="px-3 py-1 text-sm border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Prev
              </button>
              {#each Array(totalPages) as _, i}
                {#if totalPages <= 5 || i === 0 || i === totalPages - 1 || Math.abs(i - currentPage + 1) <= 1}
                  <button
                    on:click={() => currentPage = i + 1}
                    class="px-3 py-1 text-sm border rounded {currentPage === i + 1 ? 'bg-blue-600 text-white border-blue-600' : 'border-slate-200 hover:bg-slate-50'}"
                  >
                    {i + 1}
                  </button>
                {:else if i === 1 || i === totalPages - 2}
                  <span class="px-2 text-slate-400">...</span>
                {/if}
              {/each}
              <button
                on:click={() => currentPage++}
                disabled={currentPage === totalPages}
                class="px-3 py-1 text-sm border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>
