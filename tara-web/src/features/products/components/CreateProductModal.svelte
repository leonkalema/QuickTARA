<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { productApi } from '../../../lib/api/productApi';
  import type { CreateProductRequest } from '../../../lib/types/product';

  const dispatch = createEventDispatcher();

  let isSubmitting = false;
  let error = '';

  // Form data
  let formData: CreateProductRequest = {
    name: '',
    description: '',
    product_type: 'automotive',
    version: '1.0.0',
    status: 'development',
    owner_team: '',
    compliance_standards: []
  };

  let complianceInput = '';

  const productTypes = [
    { value: 'automotive', label: 'Automotive', description: 'Vehicles, ECUs, infotainment systems' },
    { value: 'industrial', label: 'Industrial', description: 'Manufacturing, automation, control systems' },
    { value: 'iot', label: 'IoT', description: 'Connected devices, sensors, smart home' },
    { value: 'medical', label: 'Medical', description: 'Healthcare devices, diagnostic equipment' },
    { value: 'aerospace', label: 'Aerospace', description: 'Aircraft systems, satellites, avionics' },
    { value: 'other', label: 'Other', description: 'Custom or specialized systems' }
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

  async function handleSubmit() {
    error = '';
    
    if (!formData.name.trim()) {
      error = 'Product name is required';
      return;
    }

    if (!formData.version.trim()) {
      error = 'Version is required';
      return;
    }

    isSubmitting = true;

    try {
      await productApi.create({
        ...formData,
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        owner_team: formData.owner_team?.trim() || undefined
      });
      
      dispatch('created');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create product';
      console.error('Error creating product:', err);
    } finally {
      isSubmitting = false;
    }
  }

  function handleClose() {
    dispatch('close');
  }
</script>

<!-- Modal Backdrop -->
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
  <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200">
      <h2 class="text-xl font-semibold text-gray-900">Create New Product</h2>
      <button
        on:click={handleClose}
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
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
          >
            {#each productTypes as type}
              <option value={type.value}>{type.label} - {type.description}</option>
            {/each}
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
          on:click={handleClose}
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 transition-colors disabled:opacity-50"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Product'}
        </button>
      </div>
    </form>
  </div>
</div>
