<script lang="ts">
  import { onMount } from 'svelte';
  import type { CompensatingControl, CreateCompensatingControlRequest, CompensatingControlCatalogItem, CraRequirementStatusRecord } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { Plus, Edit2, ShieldCheck, AlertCircle, ChevronDown, Trash2 } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    controls: CompensatingControl[];
    requirements: CraRequirementStatusRecord[];
    onupdate?: () => void;
  }

  let { assessmentId, controls, requirements, onupdate }: Props = $props();

  let showAddForm = $state(false);
  let saving = $state(false);
  let deletingId: string | null = $state(null);
  let catalog: CompensatingControlCatalogItem[] = $state([]);
  let selectedCatalogId = $state('');
  let formErrors: Record<string, string> = $state({});
  let formTouched: Record<string, boolean> = $state({});
  let newControl: CreateCompensatingControlRequest = $state({
    control_id: '',
    name: '',
    description: '',
    implementation_status: 'planned',
    supplier_actions: '',
    oem_actions: '',
    residual_risk: '',
    mitigated_requirement_ids: [],
  });

  // Get the currently selected catalog item
  const selectedCatalogItem = $derived(
    catalog.find(c => c.control_id === newControl.control_id)
  );

  // Get requirements with gaps that this control can actually mitigate
  const applicableGapRequirements = $derived(() => {
    const gaps = requirements.filter(r => r.status !== 'compliant' && r.status !== 'not_applicable');
    if (!selectedCatalogItem?.applicable_requirements) return [];
    return gaps.filter(r => selectedCatalogItem.applicable_requirements.includes(r.requirement_id));
  });

  onMount(async () => {
    try {
      catalog = await craApi.getCompensatingControlsCatalog();
    } catch (err) {
      console.error('Failed to load catalog:', err);
    }
  });

  function selectFromCatalog(catalogId: string): void {
    const item = catalog.find(c => c.control_id === catalogId);
    if (item) {
      newControl = {
        ...newControl,
        control_id: item.control_id,
        name: item.name,
        description: item.description,
        mitigated_requirement_ids: [],
      };
      formErrors = {};
      formTouched = { control_id: true, name: true };
    }
    selectedCatalogId = '';
  }

  function validateForm(): boolean {
    const errors: Record<string, string> = {};
    if (!newControl.control_id.trim()) {
      errors.control_id = 'Control ID is required';
    }
    if (!newControl.name.trim()) {
      errors.name = 'Name is required';
    }
    formErrors = errors;
    return Object.keys(errors).length === 0;
  }

  function markTouched(field: string): void {
    formTouched = { ...formTouched, [field]: true };
    validateForm();
  }

  const STATUS_COLORS: Record<string, string> = {
    planned: 'var(--color-text-tertiary)',
    implemented: 'var(--color-status-warning)',
    verified: 'var(--color-status-success)',
  } as const;

  const STATUS_LABELS: Record<string, string> = {
    planned: 'Planned',
    implemented: 'Implemented',
    verified: 'Verified',
  } as const;

  function resetForm(): void {
    newControl = {
      control_id: '',
      name: '',
      description: '',
      implementation_status: 'planned',
      supplier_actions: '',
      oem_actions: '',
      residual_risk: '',
      mitigated_requirement_ids: [],
    };
    formErrors = {};
    formTouched = {};
    selectedCatalogId = '';
    showAddForm = false;
  }

  function toggleRequirement(reqId: string): void {
    const current = newControl.mitigated_requirement_ids ?? [];
    if (current.includes(reqId)) {
      newControl = { ...newControl, mitigated_requirement_ids: current.filter(id => id !== reqId) };
    } else {
      newControl = { ...newControl, mitigated_requirement_ids: [...current, reqId] };
    }
  }

  async function addControl(): Promise<void> {
    formTouched = { control_id: true, name: true };
    if (!validateForm()) return;
    if (isDuplicate(newControl.control_id)) {
      formErrors = { ...formErrors, control_id: 'This control is already added to this assessment' };
      return;
    }
    saving = true;
    try {
      await craApi.createCompensatingControl(assessmentId, newControl);
      resetForm();
      onupdate?.();
    } catch (err) {
      console.error('Failed to create control:', err);
      formErrors = { ...formErrors, submit: 'Failed to save. Please try again.' };
    } finally {
      saving = false;
    }
  }

  async function updateStatus(controlId: string, newStatus: string): Promise<void> {
    try {
      await craApi.updateCompensatingControl(controlId, { implementation_status: newStatus as any });
      onupdate?.();
    } catch (err) {
      console.error('Failed to update control:', err);
    }
  }

  async function deleteControl(controlId: string): Promise<void> {
    deletingId = controlId;
    try {
      await craApi.deleteCompensatingControl(controlId);
      onupdate?.();
    } catch (err) {
      console.error('Failed to delete control:', err);
    } finally {
      deletingId = null;
    }
  }

  function confirmDelete(controlId: string): void {
    deletingId = controlId;
  }

  function cancelDelete(): void {
    deletingId = null;
  }

  function isDuplicate(controlId: string): boolean {
    return controls.some(c => c.control_id === controlId);
  }
</script>

<div class="space-y-3">
  <div class="flex items-center justify-between">
    <h3 class="text-sm font-semibold flex items-center gap-2" style="color: var(--color-text-primary);">
      <ShieldCheck class="w-4 h-4" style="color: var(--color-accent-primary);" />
      Compensating Controls (Art. 5(3))
    </h3>
    <button
      class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded text-xs font-medium cursor-pointer transition-colors"
      style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
      onclick={() => { showAddForm = !showAddForm; }}
    >
      <Plus class="w-3 h-3" />
      Add Control
    </button>
  </div>

  <!-- Add form -->
  {#if showAddForm}
    <div class="rounded-lg border p-4 space-y-4" style="background: var(--color-bg-surface-hover); border-color: var(--color-border-default);">

      <!-- Catalog picker -->
      <div>
        <label for="cc-catalog" class="block text-xs font-medium mb-1" style="color: var(--color-accent-primary);">
          Quick Pick from Catalog
        </label>
        <div class="relative">
          <select
            id="cc-catalog"
            class="w-full px-3 py-2 rounded text-sm border appearance-none cursor-pointer"
            style="background: var(--color-bg-surface); border-color: var(--color-accent-primary); color: var(--color-text-primary);"
            bind:value={selectedCatalogId}
            onchange={(e) => selectFromCatalog((e.target as HTMLSelectElement).value)}
          >
            <option value="">Select a pre-approved control to auto-fill...</option>
            {#each catalog as item}
              <option value={item.control_id}>{item.control_id} — {item.name}</option>
            {/each}
          </select>
          <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none" style="color: var(--color-text-tertiary);" />
        </div>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">
          Or enter custom control details below
        </p>
      </div>

      <div class="border-t pt-4" style="border-color: var(--color-border-default);">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="cc-id" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">
              Control ID <span style="color: var(--color-status-error);">*</span>
            </label>
            <input
              id="cc-id"
              type="text"
              class="w-full px-2 py-1.5 rounded text-sm border"
              style="background: var(--color-bg-surface); border-color: {formTouched.control_id && formErrors.control_id ? 'var(--color-status-error)' : 'var(--color-border-default)'}; color: var(--color-text-primary);"
              bind:value={newControl.control_id}
              onblur={() => markTouched('control_id')}
              placeholder="e.g. CC-NET-001"
            />
            {#if formTouched.control_id && formErrors.control_id}
              <p class="text-xs mt-1 flex items-center gap-1" style="color: var(--color-status-error);">
                <AlertCircle class="w-3 h-3" />
                {formErrors.control_id}
              </p>
            {/if}
          </div>
          <div>
            <label for="cc-name" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">
              Name <span style="color: var(--color-status-error);">*</span>
            </label>
            <input
              id="cc-name"
              type="text"
              class="w-full px-2 py-1.5 rounded text-sm border"
              style="background: var(--color-bg-surface); border-color: {formTouched.name && formErrors.name ? 'var(--color-status-error)' : 'var(--color-border-default)'}; color: var(--color-text-primary);"
              bind:value={newControl.name}
              onblur={() => markTouched('name')}
              placeholder="Control name"
            />
            {#if formTouched.name && formErrors.name}
              <p class="text-xs mt-1 flex items-center gap-1" style="color: var(--color-status-error);">
                <AlertCircle class="w-3 h-3" />
                {formErrors.name}
              </p>
            {/if}
          </div>
        <div class="col-span-2">
          <label for="cc-desc" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Description</label>
          <textarea id="cc-desc" class="w-full px-2 py-1.5 rounded text-sm border resize-none" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" rows="2" bind:value={newControl.description}></textarea>
        </div>
        <div>
          <label for="cc-supplier" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Supplier Actions</label>
          <textarea id="cc-supplier" class="w-full px-2 py-1.5 rounded text-sm border resize-none" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" rows="2" bind:value={newControl.supplier_actions}></textarea>
        </div>
        <div>
          <label for="cc-oem" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">OEM Actions</label>
          <textarea id="cc-oem" class="w-full px-2 py-1.5 rounded text-sm border resize-none" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" rows="2" bind:value={newControl.oem_actions}></textarea>
        </div>
        <div class="col-span-2">
          <label for="cc-risk" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Residual Risk</label>
          <textarea id="cc-risk" class="w-full px-2 py-1.5 rounded text-sm border resize-none" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" rows="2" bind:value={newControl.residual_risk}></textarea>
        </div>

        <!-- Mitigated Requirements selector -->
        <div class="col-span-2">
          <label class="block text-xs font-medium mb-2" style="color: var(--color-accent-primary);">
            Mitigates Requirements (Gap Analysis)
          </label>
          {#if !selectedCatalogItem}
            <p class="text-xs" style="color: var(--color-text-tertiary);">
              Select a control from the catalog to see applicable requirements.
            </p>
          {:else if applicableGapRequirements().length === 0}
            <p class="text-xs" style="color: var(--color-status-success);">
              ✓ All requirements this control addresses are already compliant.
            </p>
          {:else}
            <div class="flex flex-wrap gap-2">
              {#each applicableGapRequirements() as req}
                {@const isSelected = (newControl.mitigated_requirement_ids ?? []).includes(req.id)}
                <button
                  type="button"
                  class="px-2 py-1.5 rounded text-xs cursor-pointer transition-colors border text-left"
                  style="background: {isSelected ? 'var(--color-accent-primary)' : 'var(--color-bg-surface)'}; color: {isSelected ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'}; border-color: {isSelected ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};"
                  onclick={() => toggleRequirement(req.id)}
                >
                  <span class="font-medium">{req.requirement_article ?? 'Art. ?'}</span>
                  <span class="opacity-80"> — {req.requirement_name ?? req.requirement_id}</span>
                </button>
              {/each}
            </div>
            <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">
              These are the CRA requirements that "{selectedCatalogItem.name}" can technically mitigate
            </p>
          {/if}
        </div>
        </div>
      </div>

      <!-- Submit error -->
      {#if formErrors.submit}
        <div class="flex items-center gap-2 p-2 rounded" style="background: var(--color-status-error)10; color: var(--color-status-error);">
          <AlertCircle class="w-4 h-4" />
          <span class="text-xs">{formErrors.submit}</span>
        </div>
      {/if}

      <div class="flex gap-2">
        <button class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer" style="background: var(--color-accent-primary); color: var(--color-text-inverse);" onclick={addControl} disabled={saving}>
          {saving ? 'Saving...' : 'Add'}
        </button>
        <button class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer" style="background: var(--color-bg-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);" onclick={resetForm}>
          Cancel
        </button>
      </div>
    </div>
  {/if}

  <!-- Controls list -->
  {#if controls.length === 0 && !showAddForm}
    <div class="text-center py-6 text-sm" style="color: var(--color-text-tertiary);">
      No compensating controls defined yet.
    </div>
  {:else}
    <div class="space-y-2">
      {#each controls as ctrl (ctrl.id)}
        <div class="rounded-lg border p-3" style="background: var(--color-bg-surface); border-color: {deletingId === ctrl.id ? 'var(--color-status-error)' : 'var(--color-border-default)'};">
          {#if deletingId === ctrl.id}
            <!-- Delete confirmation -->
            <div class="flex items-center justify-between">
              <div class="text-sm" style="color: var(--color-text-primary);">
                Remove <strong>{ctrl.name}</strong>?
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="px-3 py-1 rounded text-xs font-medium cursor-pointer"
                  style="background: var(--color-status-error); color: white;"
                  onclick={() => deleteControl(ctrl.id)}
                >
                  Remove
                </button>
                <button
                  class="px-3 py-1 rounded text-xs font-medium cursor-pointer"
                  style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);"
                  onclick={cancelDelete}
                >
                  Cancel
                </button>
              </div>
            </div>
          {:else}
            <!-- Normal view -->
            <div class="flex items-start justify-between mb-2">
              <div>
                <span class="text-xs font-mono" style="color: var(--color-accent-primary);">{ctrl.control_id}</span>
                <span class="text-sm font-medium ml-2" style="color: var(--color-text-primary);">{ctrl.name}</span>
              </div>
              <div class="flex items-center gap-2">
                <select
                  class="text-xs px-2 py-1 rounded border cursor-pointer"
                  style="background: var(--color-bg-surface-hover); border-color: var(--color-border-default); color: {STATUS_COLORS[ctrl.implementation_status] ?? 'var(--color-text-secondary)'};"
                  value={ctrl.implementation_status}
                  onchange={(e) => updateStatus(ctrl.id, (e.target as HTMLSelectElement).value)}
                >
                  <option value="planned">Planned</option>
                  <option value="implemented">Implemented</option>
                  <option value="verified">Verified</option>
                </select>
                <button
                  class="p-1 rounded cursor-pointer transition-colors hover:bg-red-500/10"
                  style="color: var(--color-text-tertiary);"
                  onclick={() => confirmDelete(ctrl.id)}
                  title="Remove control"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          {#if ctrl.description}
            <p class="text-xs mb-2" style="color: var(--color-text-secondary);">{ctrl.description}</p>
          {/if}
          <div class="grid grid-cols-3 gap-2 text-xs">
            {#if ctrl.supplier_actions}
              <div>
                <span class="font-medium" style="color: var(--color-text-tertiary);">Supplier:</span>
                <span style="color: var(--color-text-secondary);"> {ctrl.supplier_actions}</span>
              </div>
            {/if}
            {#if ctrl.oem_actions}
              <div>
                <span class="font-medium" style="color: var(--color-text-tertiary);">OEM:</span>
                <span style="color: var(--color-text-secondary);"> {ctrl.oem_actions}</span>
              </div>
            {/if}
            {#if ctrl.residual_risk}
              <div>
                <span class="font-medium" style="color: var(--color-text-tertiary);">Residual Risk:</span>
                <span style="color: var(--color-status-warning);"> {ctrl.residual_risk}</span>
              </div>
            {/if}
          </div>
          {#if ctrl.mitigated_requirements && ctrl.mitigated_requirements.length > 0}
            <div class="mt-2 pt-2 border-t" style="border-color: var(--color-border-default);">
              <span class="text-xs font-medium" style="color: var(--color-accent-primary);">Mitigates:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                {#each ctrl.mitigated_requirements as mitigated}
                  <span class="px-1.5 py-0.5 rounded text-xs" style="background: var(--color-accent-primary)15; color: var(--color-accent-primary);">
                    {mitigated.requirement_id}
                  </span>
                {/each}
              </div>
            </div>
          {/if}
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
