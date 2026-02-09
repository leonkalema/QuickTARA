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

<div class="fixed inset-0 flex items-center justify-center p-4 z-50" style="background: rgba(0,0,0,0.6);">
  <div class="rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);">
    <div class="flex items-center justify-between p-5" style="border-bottom: 1px solid var(--color-border-subtle);">
      <h2 class="text-sm font-semibold" style="color: var(--color-text-primary);">Create New Product</h2>
      <button on:click={closeModal} style="color: var(--color-text-tertiary);">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>

    <form on:submit|preventDefault={handleSubmit} class="p-5 space-y-5">
      <div class="space-y-3">
        <h3 class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-tertiary);">Basic Information</h3>
        <div>
          <label for="department" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Department *</label>
          <select id="department" bind:value={selectedOrganizationId} required disabled={isLoadingOrganizations}
            class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);">
            <option value="">{isLoadingOrganizations ? 'Loading...' : 'Select department'}</option>
            {#each organizations as org (org.organizationId)}
              <option value={org.organizationId}>{org.name}</option>
            {/each}
          </select>
        </div>
        <div>
          <label for="name" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Product Name *</label>
          <input id="name" type="text" bind:value={formData.name} placeholder="e.g., Vehicle Gateway ECU" required
            class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);" />
        </div>
        <div>
          <label for="description" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Description</label>
          <textarea id="description" bind:value={formData.description} placeholder="Brief description..." rows="3"
            class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);"></textarea>
        </div>
        <div>
          <label for="type" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Product Type *</label>
          <select id="type" bind:value={formData.product_type} required
            class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);">
            <option value="">Select type</option>
            <option value="ECU">ECU</option>
            <option value="Gateway">Gateway</option>
            <option value="Sensor">Sensor</option>
            <option value="Actuator">Actuator</option>
            <option value="Network">Network</option>
            <option value="ExternalDevice">External Device</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="version" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Version *</label>
            <input id="version" type="text" bind:value={formData.version} placeholder="1.0.0" required
              class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);" />
          </div>
          <div>
            <label for="status" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Status *</label>
            <select id="status" bind:value={formData.status}
              class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);">
              {#each statusOptions as status}
                <option value={status.value}>{status.label}</option>
              {/each}
            </select>
          </div>
        </div>
        <div>
          <label for="team" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Owner Team</label>
          <input id="team" type="text" bind:value={formData.owner_team} placeholder="e.g., Security Engineering"
            class="w-full px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);" />
        </div>
      </div>

      <div class="space-y-3">
        <h3 class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-tertiary);">Compliance Standards</h3>
        <div class="flex gap-2">
          <input type="text" bind:value={complianceInput} placeholder="Add standard..."
            class="flex-1 px-3 py-2 rounded-md text-sm border-0" style="background: var(--color-bg-inset); color: var(--color-text-primary);"
            on:keydown={(e) => e.key === 'Enter' && (e.preventDefault(), addComplianceStandard())} />
          <button type="button" on:click={addComplianceStandard}
            class="px-3 py-2 rounded-md text-xs font-medium" style="background: var(--color-bg-elevated); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">Add</button>
        </div>
        <div>
          <p class="text-[11px] mb-1.5" style="color: var(--color-text-tertiary);">Common:</p>
          <div class="flex flex-wrap gap-1.5">
            {#each commonStandards as standard}
              <button type="button" on:click={() => addPresetStandard(standard)}
                class="px-2 py-1 text-[11px] rounded transition-colors disabled:opacity-30"
                style="background: var(--color-bg-inset); color: var(--color-text-secondary);"
                disabled={formData.compliance_standards?.includes(standard)}>{standard}</button>
            {/each}
          </div>
        </div>
        {#if formData.compliance_standards && formData.compliance_standards.length > 0}
          <div class="flex flex-wrap gap-1.5">
            {#each formData.compliance_standards as standard}
              <span class="inline-flex items-center px-2 py-1 rounded text-[11px] font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
                {standard}
                <button type="button" on:click={() => removeComplianceStandard(standard)} class="ml-1.5 opacity-70 hover:opacity-100">×</button>
              </span>
            {/each}
          </div>
        {/if}
      </div>

      {#if error}
        <div class="rounded-md p-3" style="background: var(--color-error-bg); border: 1px solid var(--color-error);">
          <p class="text-xs" style="color: var(--color-error);">{error}</p>
        </div>
      {/if}

      <div class="flex justify-end gap-2 pt-4" style="border-top: 1px solid var(--color-border-subtle);">
        <button type="button" on:click={closeModal} disabled={isLoading}
          class="px-3 py-2 text-sm font-medium rounded-md" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">Cancel</button>
        <button type="submit" disabled={isLoading}
          class="px-3 py-2 text-sm font-medium rounded-md disabled:opacity-50" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
          {isLoading ? 'Creating...' : 'Create Product'}
        </button>
      </div>
    </form>
  </div>
</div>
