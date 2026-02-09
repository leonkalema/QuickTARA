<script lang="ts">
  import { onMount } from 'svelte';
  import type { InventoryItem, InventorySummary, TargetMarket } from '$lib/types/cra';
  import { craApi } from '$lib/api/craApi';
  import { Plus, Trash2, Package, Globe, AlertTriangle } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    onupdate?: () => void;
  }

  let { assessmentId, onupdate }: Props = $props();

  let items: InventoryItem[] = $state([]);
  let summary: InventorySummary | null = $state(null);
  let loading = $state(true);
  let showAddForm = $state(false);
  let saving = $state(false);
  let deletingId: string | null = $state(null);

  let newItem = $state({
    sku: '',
    firmware_version: '',
    units_in_stock: 0,
    units_in_field: 0,
    oem_customer: '',
    target_market: 'eu' as TargetMarket,
    last_production_date: '',
    notes: '',
  });

  const MARKET_LABELS: Record<TargetMarket, string> = {
    eu: 'EU',
    non_eu: 'Non-EU',
    global: 'Global',
  };

  const MARKET_COLORS: Record<TargetMarket, string> = {
    eu: 'var(--color-accent-primary)',
    non_eu: 'var(--color-status-success)',
    global: 'var(--color-status-warning)',
  };

  async function loadData(): Promise<void> {
    loading = true;
    try {
      [items, summary] = await Promise.all([
        craApi.getInventory(assessmentId),
        craApi.getInventorySummary(assessmentId),
      ]);
    } catch (err) {
      console.error('Failed to load inventory:', err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadData();
  });

  function resetForm(): void {
    newItem = {
      sku: '',
      firmware_version: '',
      units_in_stock: 0,
      units_in_field: 0,
      oem_customer: '',
      target_market: 'eu',
      last_production_date: '',
      notes: '',
    };
    showAddForm = false;
  }

  async function addItem(): Promise<void> {
    if (!newItem.sku.trim()) return;
    saving = true;
    try {
      await craApi.createInventoryItem({
        assessment_id: assessmentId,
        sku: newItem.sku,
        firmware_version: newItem.firmware_version || undefined,
        units_in_stock: newItem.units_in_stock,
        units_in_field: newItem.units_in_field,
        oem_customer: newItem.oem_customer || undefined,
        target_market: newItem.target_market,
        last_production_date: newItem.last_production_date || undefined,
        notes: newItem.notes || undefined,
      });
      resetForm();
      await loadData();
      onupdate?.();
    } catch (err) {
      console.error('Failed to add inventory item:', err);
    } finally {
      saving = false;
    }
  }

  async function deleteItem(id: string): Promise<void> {
    deletingId = id;
    try {
      await craApi.deleteInventoryItem(id);
      await loadData();
      onupdate?.();
    } catch (err) {
      console.error('Failed to delete inventory item:', err);
    } finally {
      deletingId = null;
    }
  }
</script>

<div class="space-y-4">
  <!-- Summary Cards -->
  {#if summary}
    <div class="grid grid-cols-4 gap-4">
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="flex items-center gap-2 mb-2">
          <Package class="w-4 h-4" style="color: var(--color-text-tertiary);" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Total SKUs</span>
        </div>
        <div class="text-2xl font-bold" style="color: var(--color-text-primary);">{summary.total_skus}</div>
      </div>
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="flex items-center gap-2 mb-2">
          <Globe class="w-4 h-4" style="color: var(--color-accent-primary);" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">EU Units</span>
        </div>
        <div class="text-2xl font-bold" style="color: var(--color-accent-primary);">{summary.eu_units.toLocaleString()}</div>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">Requires mitigation</p>
      </div>
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="flex items-center gap-2 mb-2">
          <Globe class="w-4 h-4" style="color: var(--color-status-success);" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Non-EU Units</span>
        </div>
        <div class="text-2xl font-bold" style="color: var(--color-status-success);">{summary.non_eu_units.toLocaleString()}</div>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">Liquidation option</p>
      </div>
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">OEM Customers</span>
        </div>
        <div class="text-2xl font-bold" style="color: var(--color-text-primary);">{summary.oems.length}</div>
        <p class="text-xs mt-1 truncate" style="color: var(--color-text-tertiary);">
          {summary.oems.slice(0, 3).join(', ')}{summary.oems.length > 3 ? '...' : ''}
        </p>
      </div>
    </div>
  {/if}

  <!-- Inventory Table -->
  <div class="rounded-lg border overflow-hidden" style="border-color: var(--color-border-default);">
    <div class="flex items-center justify-between px-4 py-3" style="background: var(--color-bg-surface-hover);">
      <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">Inventory Items</h3>
      <button
        class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={() => { showAddForm = !showAddForm; }}
      >
        <Plus class="w-3 h-3" />
        Add SKU
      </button>
    </div>

    {#if showAddForm}
      <div class="px-4 py-3 border-t" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="grid grid-cols-4 gap-3">
          <div>
            <label for="inv-sku" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">SKU *</label>
            <input id="inv-sku" type="text" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.sku} placeholder="e.g. GEN1-V2.1" />
          </div>
          <div>
            <label for="inv-fw" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Firmware Version</label>
            <input id="inv-fw" type="text" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.firmware_version} placeholder="e.g. v2.1.0" />
          </div>
          <div>
            <label for="inv-stock" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Units in Stock</label>
            <input id="inv-stock" type="number" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.units_in_stock} min="0" />
          </div>
          <div>
            <label for="inv-field" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Units in Field</label>
            <input id="inv-field" type="number" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.units_in_field} min="0" />
          </div>
          <div>
            <label for="inv-oem" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">OEM Customer</label>
            <input id="inv-oem" type="text" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.oem_customer} placeholder="e.g. BMW, VW" />
          </div>
          <div>
            <label for="inv-market" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Target Market</label>
            <select id="inv-market" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.target_market}>
              <option value="eu">EU (Requires Mitigation)</option>
              <option value="non_eu">Non-EU (Liquidation)</option>
              <option value="global">Global</option>
            </select>
          </div>
          <div>
            <label for="inv-date" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Last Production Date</label>
            <input id="inv-date" type="date" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.last_production_date} />
          </div>
          <div>
            <label for="inv-notes" class="block text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Notes</label>
            <input id="inv-notes" type="text" class="w-full px-2 py-1.5 rounded text-sm border" style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);" bind:value={newItem.notes} placeholder="Optional notes" />
          </div>
        </div>
        <div class="flex gap-2 mt-3">
          <button
            class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
            style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
            onclick={addItem}
            disabled={saving || !newItem.sku.trim()}
          >
            {saving ? 'Adding...' : 'Add Item'}
          </button>
          <button
            class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
            style="background: var(--color-bg-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
            onclick={resetForm}
          >
            Cancel
          </button>
        </div>
      </div>
    {/if}

    {#if loading}
      <div class="px-4 py-8 text-center" style="color: var(--color-text-tertiary);">Loading inventory...</div>
    {:else if items.length === 0}
      <div class="px-4 py-8 text-center">
        <Package class="w-8 h-8 mx-auto mb-2" style="color: var(--color-text-tertiary);" />
        <p class="text-sm" style="color: var(--color-text-secondary);">No inventory items yet</p>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">Add SKUs to track EU vs non-EU inventory</p>
      </div>
    {:else}
      <table class="w-full text-sm">
        <thead>
          <tr style="background: var(--color-bg-surface-hover);">
            <th class="px-4 py-2 text-left text-xs font-medium" style="color: var(--color-text-tertiary);">SKU</th>
            <th class="px-4 py-2 text-left text-xs font-medium" style="color: var(--color-text-tertiary);">Firmware</th>
            <th class="px-4 py-2 text-right text-xs font-medium" style="color: var(--color-text-tertiary);">Stock</th>
            <th class="px-4 py-2 text-right text-xs font-medium" style="color: var(--color-text-tertiary);">Field</th>
            <th class="px-4 py-2 text-left text-xs font-medium" style="color: var(--color-text-tertiary);">OEM</th>
            <th class="px-4 py-2 text-center text-xs font-medium" style="color: var(--color-text-tertiary);">Market</th>
            <th class="px-4 py-2 text-center text-xs font-medium" style="color: var(--color-text-tertiary);"></th>
          </tr>
        </thead>
        <tbody>
          {#each items as item (item.id)}
            <tr class="border-t" style="border-color: var(--color-border-subtle);">
              <td class="px-4 py-2 font-medium" style="color: var(--color-text-primary);">{item.sku}</td>
              <td class="px-4 py-2" style="color: var(--color-text-secondary);">{item.firmware_version ?? '—'}</td>
              <td class="px-4 py-2 text-right font-mono" style="color: var(--color-text-primary);">{item.units_in_stock.toLocaleString()}</td>
              <td class="px-4 py-2 text-right font-mono" style="color: var(--color-text-primary);">{item.units_in_field.toLocaleString()}</td>
              <td class="px-4 py-2" style="color: var(--color-text-secondary);">{item.oem_customer ?? '—'}</td>
              <td class="px-4 py-2 text-center">
                <span class="px-2 py-0.5 rounded text-xs font-medium" style="background: {MARKET_COLORS[item.target_market]}15; color: {MARKET_COLORS[item.target_market]};">
                  {MARKET_LABELS[item.target_market]}
                </span>
              </td>
              <td class="px-4 py-2 text-center">
                <button
                  class="p-1 rounded cursor-pointer transition-opacity hover:opacity-100 opacity-50"
                  style="color: var(--color-status-error);"
                  onclick={() => deleteItem(item.id)}
                  disabled={deletingId === item.id}
                  title="Delete"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>

  <!-- CRA Guidance -->
  {#if summary && summary.eu_units > 0}
    <div class="rounded-lg border p-4" style="background: var(--color-status-warning)10; border-color: var(--color-status-warning);">
      <div class="flex items-start gap-3">
        <AlertTriangle class="w-5 h-5 flex-shrink-0" style="color: var(--color-status-warning);" />
        <div>
          <h4 class="text-sm font-medium" style="color: var(--color-text-primary);">EU Market Inventory Requires CRA Compliance</h4>
          <p class="text-xs mt-1" style="color: var(--color-text-secondary);">
            {summary.eu_units.toLocaleString()} units targeting EU market need either:
          </p>
          <ul class="text-xs mt-2 space-y-1" style="color: var(--color-text-secondary);">
            <li>• <strong>Direct Patch Path:</strong> SW updates via workshop/service channels</li>
            <li>• <strong>Compensating Control Path:</strong> Network-layer mitigations per Art. 5(3)</li>
          </ul>
        </div>
      </div>
    </div>
  {/if}
</div>
