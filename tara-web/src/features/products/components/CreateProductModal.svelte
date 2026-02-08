<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '../../../components/ui/Modal.svelte';
  import type { Product } from '../../../lib/types/product';
  import { API_BASE_URL } from '$lib/config';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';
  import { notifyProductsChanged } from '$lib/stores/productEvents';

  export let isOpen = false;

  const dispatch = createEventDispatcher<{
    close: void;
    create: Product;
  }>();

  let isLoading = false;
  let error = '';

  type OrganizationOption = {
    organizationId: string;
    name: string;
  };

  let organizations: OrganizationOption[] = [];
  let selectedOrganizationId = '';
  let isLoadingOrganizations = false;

  let formData = {
    name: '',
    description: '',
    product_type: 'automotive',
    version: '',
    status: 'development',
    owner_team: '',
    compliance_standards: [] as string[]
  };

  let complianceInput = '';

  const productTypes = [
    { value: 'automotive', label: 'Automotive', description: 'Vehicle systems and components' },
    { value: 'industrial', label: 'Industrial', description: 'Manufacturing and automation' },
    { value: 'iot', label: 'IoT', description: 'Internet of Things devices' },
    { value: 'medical', label: 'Medical', description: 'Healthcare and medical devices' },
    { value: 'aerospace', label: 'Aerospace', description: 'Aviation and space systems' }
  ];

  const statusOptions = [
    { value: 'development', label: 'Development', description: 'Early stage, design and prototyping' },
    { value: 'testing', label: 'Testing', description: 'Validation, QA, and security testing' },
    { value: 'production', label: 'Production', description: 'Live, deployed to customers' },
    { value: 'deprecated', label: 'Deprecated', description: 'End of life, legacy support only' }
  ];

  const commonStandards = [
    'ISO 21434', 'ISO 26262', 'SAE J3061', 'UNECE WP.29',
    'NIST Cybersecurity Framework', 'IEC 62443', 'GDPR',
    'HIPAA', 'SOX', 'PCI DSS', 'FIPS 140-2'
  ];

  function addComplianceStandard() {
    if (complianceInput.trim() && !formData.compliance_standards?.includes(complianceInput.trim())) {
      formData.compliance_standards = [...(formData.compliance_standards || []), complianceInput.trim()];
      complianceInput = '';
    }
  }

  function removeComplianceStandard(standard: string) {
    formData.compliance_standards = formData.compliance_standards?.filter(s => s !== standard) || [];
  }

  function addPresetStandard(standard: string) {
    if (!formData.compliance_standards?.includes(standard)) {
      formData.compliance_standards = [...(formData.compliance_standards || []), standard];
    }
  }

  const getAuthToken = (): string | null => {
    const auth = get(authStore);
    const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
    return auth.token ?? tokenFromStorage;
  };

  const loadOrganizations = async (): Promise<void> => {
    isLoadingOrganizations = true;
    try {
      const auth = get(authStore);
      const isSuperuser = (auth.user as any)?.is_superuser === true;
      const isToolAdmin = isSuperuser || authStore.hasRole('tool_admin');
      const orgsFromUser = auth.user?.organizations ?? [];
      if (!isToolAdmin) {
        organizations = orgsFromUser.map((o) => ({ organizationId: o.organization_id, name: o.name }));
      } else {
        const token = getAuthToken();
        const headers: HeadersInit = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const response = await fetch(`${API_BASE_URL}/organizations`, { headers });
        if (response.ok) {
          const data = await response.json();
          const orgList = (data.organizations ?? []) as Array<{ organization_id: string; name: string }>;
          organizations = orgList.map((o) => ({ organizationId: o.organization_id, name: o.name }));
        } else {
          organizations = [];
        }
      }
      if (organizations.length === 1) {
        selectedOrganizationId = organizations[0]?.organizationId ?? '';
      }
    } catch {
      organizations = [];
    } finally {
      isLoadingOrganizations = false;
    }
  };

  async function handleSubmit() {
    if (!formData.name.trim()) {
      error = 'Product name is required';
      return;
    }

    if (!selectedOrganizationId) {
      error = 'Department is required';
      return;
    }

    isLoading = true;
    error = '';

    try {
      const auth = get(authStore);
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };
      const token = getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(`${API_BASE_URL}/products`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          name: formData.name.trim(),
          product_type: formData.product_type,
          description: formData.description.trim() || null,
          organization_id: selectedOrganizationId,
          safety_level: 'QM',
          interfaces: [],
          access_points: [],
          boundaries: [],
          objectives: [],
          stakeholders: [],
          location: 'Internal',
          trust_zone: 'Standard'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error Response:', errorData);
        throw new Error(JSON.stringify(errorData) || `HTTP error! status: ${response.status}`);
      }

      const newProduct = await response.json();
      dispatch('create', newProduct);
      notifyProductsChanged();
      
      // Show success notification
      const { notifications } = await import('../../../lib/stores/notificationStore');
      notifications.show(`Product "${newProduct.name}" created successfully!`, 'success');
      
      resetForm();
      isOpen = false;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create product';
      console.error('Error creating product:', err);
    } finally {
      isLoading = false;
    }
  }

  function resetForm() {
    formData = {
      name: '',
      description: '',
      product_type: 'automotive',
      version: '',
      status: 'development',
      owner_team: '',
      compliance_standards: []
    };
    complianceInput = '';
    selectedOrganizationId = '';
    error = '';
  }

  function closeModal() {
    resetForm();
    isOpen = false;
    dispatch('close');
  }

  $: {
    if (isOpen) {
      loadOrganizations();
    }
  }
</script>

<!-- Modal Backdrop -->
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
  <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200">
      <h2 class="text-xl font-semibold text-gray-900">Create New Product</h2>
      <button
        on:click={closeModal}
        class="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Form -->
    <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
      <!-- Basic Information -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Basic Information</h3>

        <div>
          <label for="department" class="block text-sm font-medium text-gray-700 mb-1">
            Department *
          </label>
          <select
            id="department"
            bind:value={selectedOrganizationId}
            required
            disabled={isLoadingOrganizations}
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">{isLoadingOrganizations ? 'Loading departments...' : 'Select department'}</option>
            {#each organizations as org (org.organizationId)}
              <option value={org.organizationId}>{org.name}</option>
            {/each}
          </select>
        </div>
        
        <!-- Product Name -->
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
            Product Name *
          </label>
          <input
            id="name"
            type="text"
            bind:value={formData.name}
            placeholder="e.g., Vehicle Gateway ECU, Industrial Controller v2"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
            required
          />
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            bind:value={formData.description}
            placeholder="Brief description of the product's purpose and key features..."
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
          ></textarea>
        </div>

        <!-- Product Type -->
        <div>
          <label for="type" class="block text-sm font-medium text-gray-700 mb-1">
            Product Type *
          </label>
          <select
            id="type"
            bind:value={formData.product_type}
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Select product type</option>
            <option value="ECU">ECU</option>
            <option value="Gateway">Gateway</option>
            <option value="Sensor">Sensor</option>
            <option value="Actuator">Actuator</option>
            <option value="Network">Network</option>
            <option value="ExternalDevice">External Device</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <!-- Version and Status -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label for="version" class="block text-sm font-medium text-gray-700 mb-1">
              Version *
            </label>
            <input
              id="version"
              type="text"
              bind:value={formData.version}
              placeholder="1.0.0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
              required
            />
          </div>

          <div>
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
              Status *
            </label>
            <select
              id="status"
              bind:value={formData.status}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
            >
              {#each statusOptions as status}
                <option value={status.value}>{status.label} - {status.description}</option>
              {/each}
            </select>
          </div>
        </div>

        <!-- Owner Team -->
        <div>
          <label for="team" class="block text-sm font-medium text-gray-700 mb-1">
            Owner Team
          </label>
          <input
            id="team"
            type="text"
            bind:value={formData.owner_team}
            placeholder="e.g., Security Engineering, Platform Team"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
          />
        </div>
      </div>

      <!-- Compliance Standards -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Compliance Standards</h3>
        
        <!-- Add Custom Standard -->
        <div class="flex space-x-2">
          <input
            type="text"
            bind:value={complianceInput}
            placeholder="Add compliance standard..."
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
            on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addComplianceStandard())}
          />
          <button
            type="button"
            on:click={addComplianceStandard}
            class="px-4 py-2 bg-slate-100 text-slate-700 rounded-md hover:bg-slate-200 transition-colors"
          >
            Add
          </button>
        </div>

        <!-- Common Standards -->
        <div>
          <p class="text-sm text-gray-600 mb-2">Common standards:</p>
          <div class="flex flex-wrap gap-2">
            {#each commonStandards as standard}
              <button
                type="button"
                on:click={() => addPresetStandard(standard)}
                class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                disabled={formData.compliance_standards?.includes(standard)}
              >
                {standard}
              </button>
            {/each}
          </div>
        </div>

        <!-- Selected Standards -->
        {#if formData.compliance_standards && formData.compliance_standards.length > 0}
          <div>
            <p class="text-sm text-gray-600 mb-2">Selected standards:</p>
            <div class="flex flex-wrap gap-2">
              {#each formData.compliance_standards as standard}
                <span class="inline-flex items-center px-3 py-1 rounded-md text-sm bg-slate-100 text-slate-700">
                  {standard}
                  <button
                    type="button"
                    on:click={() => removeComplianceStandard(standard)}
                    class="ml-2 text-slate-500 hover:text-slate-700"
                  >
                    ×
                  </button>
                </span>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <!-- Error Message -->
      {#if error}
        <div class="bg-red-50 border border-red-200 rounded-md p-3">
          <p class="text-sm text-red-600">{error}</p>
        </div>
      {/if}

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          on:click={closeModal}
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 transition-colors disabled:opacity-50"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Product'}
        </button>
      </div>
    </form>
  </div>
</div>
