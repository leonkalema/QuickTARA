<script lang="ts">
  import { User, Plus, X, Wand2 } from '@lucide/svelte';
  import { createEventDispatcher } from 'svelte';
  import type { Product } from '$lib/types/product';

  export let product: Product;
  export let isEditing: boolean = false;
  export let editedProduct: Partial<Product> = {};
  export let canEdit: boolean = true;

  const dispatch = createEventDispatcher<{ save: Partial<Product> }>();

  const TRUST_ZONES = ['Critical', 'Standard', 'Boundary', 'Untrusted'];

  function addItem(field: string, value: string) {
    if (!value.trim()) return;
    if (isEditing) {
      const arr = [...((editedProduct as any)[field] ?? [])];
      if (!arr.includes(value.trim())) {
        (editedProduct as any)[field] = [...arr, value.trim()];
        editedProduct = { ...editedProduct };
      }
    } else {
      // Inline mode — update and auto-save immediately
      const arr = [...((product as any)[field] ?? [])];
      if (!arr.includes(value.trim())) {
        arr.push(value.trim());
        (product as any)[field] = arr;
        product = { ...product };
        dispatch('save', { [field]: arr });
      }
    }
  }

  function removeItem(field: string, index: number) {
    if (isEditing) {
      const arr = [...((editedProduct as any)[field] ?? [])];
      arr.splice(index, 1);
      (editedProduct as any)[field] = arr;
      editedProduct = { ...editedProduct };
    } else {
      // Inline mode — update and auto-save immediately
      const arr = [...((product as any)[field] ?? [])];
      arr.splice(index, 1);
      (product as any)[field] = arr;
      product = { ...product };
      dispatch('save', { [field]: arr });
    }
  }

  // Auto-detect interfaces and access points from product description
  const INTERFACE_KEYWORDS: Record<string, string> = {
    'can-fd': 'CAN-FD', 'canfd': 'CAN-FD', 'can fd': 'CAN-FD', 'can bus': 'CAN',
    'uds': 'UDS', 'doip': 'DoIP', 'obd': 'OBD-II', 'ota': 'OTA',
    'ethernet': 'Automotive Ethernet', 'some/ip': 'SOME/IP', 'autosar': 'AUTOSAR',
    'bluetooth': 'Bluetooth', 'wifi': 'Wi-Fi', 'wi-fi': 'Wi-Fi',
    'lin': 'LIN', 'flexray': 'FlexRay', 'most': 'MOST',
    'uart': 'UART', 'spi': 'SPI', 'i2c': 'I2C',
  };
  const ACCESS_POINT_KEYWORDS: Record<string, string> = {
    'jtag': 'JTAG', 'swd': 'SWD', 'usb': 'USB',
    'obd-ii': 'OBD-II port', 'obd2': 'OBD-II port', 'diagnostic connector': 'Diagnostic connector',
    'physical access': 'Physical access', 'supply chain': 'Supply chain',
    'telematics': 'Telematics interface', 'v2x': 'V2X',
  };

  function autoDetect() {
    const desc = (product.description || '').toLowerCase();
    const suggestInterfaces: string[] = [];
    const suggestAccessPoints: string[] = [];

    for (const [kw, label] of Object.entries(INTERFACE_KEYWORDS)) {
      if (desc.includes(kw)) suggestInterfaces.push(label);
    }
    for (const [kw, label] of Object.entries(ACCESS_POINT_KEYWORDS)) {
      if (desc.includes(kw)) suggestAccessPoints.push(label);
    }

    // OTA implies OTA as both interface and access point
    if (desc.includes('ota')) suggestAccessPoints.push('OTA update channel');

    // Add unique suggestions
    suggestInterfaces.forEach(i => addItem('interfaces', i));
    suggestAccessPoints.forEach(a => addItem('access_points', a));
    if (suggestInterfaces.length + suggestAccessPoints.length === 0) {
      alert('No recognisable interfaces detected in description. Add manually.');
    }
  }

  let newInterface = '';
  let newAccessPoint = '';
  let newBoundary = '';
  let newObjective = '';
  let newStakeholder = '';


</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

  <!-- Technical Details -->
  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Technical Details</h2>
    <div class="space-y-3">
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Product ID</div>
        <p class="text-xs font-mono px-2 py-1 rounded" style="color: var(--color-text-primary); background: var(--color-bg-inset);">{product.scope_id}</p>
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Trust Zone</div>
        {#if isEditing}
          <select
            bind:value={editedProduct.trust_zone}
            class="w-full px-2 py-1.5 text-xs rounded"
            style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
          >
            {#each TRUST_ZONES as z}
              <option value={z}>{z}</option>
            {/each}
          </select>
        {:else}
          <p class="text-xs" style="color: var(--color-text-primary);">{product.trust_zone || 'Standard'}</p>
        {/if}
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Version</div>
        <p class="text-xs" style="color: var(--color-text-primary);">{product.version || 1}</p>
      </div>
    </div>
  </div>

  <!-- Configuration -->
  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold" style="color: var(--color-text-primary);">Configuration</h2>
      {#if canEdit && product.description}
        <button on:click={autoDetect} class="flex items-center gap-1 text-[10px] px-2 py-1 rounded transition-colors"
          style="color: var(--color-accent-primary); border: 1px solid var(--color-accent-primary);"
          title="Auto-detect interfaces and access points from the product description">
          <Wand2 class="w-3 h-3" /> Auto-detect
        </button>
      {/if}
    </div>
    <div class="space-y-3">

      <!-- Interfaces -->
      <div>
        <div class="flex items-center justify-between mb-1">
          <div class="text-[11px] font-medium" style="color: var(--color-text-tertiary);">Interfaces</div>
          <span class="text-[10px]" style="color: var(--color-text-tertiary);">{(isEditing ? editedProduct.interfaces : product.interfaces)?.length ?? 0} defined</span>
        </div>
        <div class="flex flex-wrap gap-1 mb-1">
          {#each ((isEditing ? editedProduct.interfaces : product.interfaces) ?? []) as iface, i}
            <span class="flex items-center gap-1 px-2 py-0.5 text-[10px] rounded" style="background: var(--color-info-bg); color: var(--color-info);">
              {iface}
              {#if canEdit}<button on:click={() => removeItem('interfaces', i)} class="hover:opacity-70"><X class="w-2.5 h-2.5" /></button>{/if}
            </span>
          {/each}
        </div>
        {#if canEdit}
          <div class="flex gap-1">
            <input bind:value={newInterface} placeholder="e.g. CAN-FD, UDS, OTA — press Enter" class="flex-1 px-2 py-1 text-xs rounded" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem('interfaces', newInterface); newInterface = ''; }}} />
            <button on:click={() => { addItem('interfaces', newInterface); newInterface = ''; }} class="px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"><Plus class="w-3 h-3" /></button>
          </div>
          {#if !((isEditing ? editedProduct.interfaces : product.interfaces)?.length)}
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">Required — used to filter relevant threat scenarios (e.g. CAN-FD, UDS, OTA)</p>
          {/if}
        {:else if !product.interfaces?.length}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No interfaces defined</p>
        {/if}
      </div>

      <!-- Access Points -->
      <div>
        <div class="flex items-center justify-between mb-1">
          <div class="text-[11px] font-medium" style="color: var(--color-text-tertiary);">Access Points</div>
          <span class="text-[10px]" style="color: var(--color-text-tertiary);">{(isEditing ? editedProduct.access_points : product.access_points)?.length ?? 0} defined</span>
        </div>
        <div class="flex flex-wrap gap-1 mb-1">
          {#each ((isEditing ? editedProduct.access_points : product.access_points) ?? []) as pt, i}
            <span class="flex items-center gap-1 px-2 py-0.5 text-[10px] rounded" style="background: var(--color-success-bg); color: var(--color-success);">
              {pt}
              {#if canEdit}<button on:click={() => removeItem('access_points', i)} class="hover:opacity-70"><X class="w-2.5 h-2.5" /></button>{/if}
            </span>
          {/each}
        </div>
        {#if canEdit}
          <div class="flex gap-1">
            <input bind:value={newAccessPoint} placeholder="e.g. OBD-II, JTAG, USB — press Enter" class="flex-1 px-2 py-1 text-xs rounded" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem('access_points', newAccessPoint); newAccessPoint = ''; }}} />
            <button on:click={() => { addItem('access_points', newAccessPoint); newAccessPoint = ''; }} class="px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"><Plus class="w-3 h-3" /></button>
          </div>
          {#if !((isEditing ? editedProduct.access_points : product.access_points)?.length)}
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">Required — physical and logical attack entry points (e.g. OBD-II, JTAG, USB)</p>
          {/if}
        {:else if !product.access_points?.length}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No access points defined</p>
        {/if}
      </div>

    </div>
  </div>

  <!-- Analysis Scope -->
  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Analysis Scope</h2>
    <div class="space-y-3">

      <!-- Boundaries -->
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Boundaries</div>
        <div class="space-y-1 mb-1">
          {#each ((isEditing ? editedProduct.boundaries : product.boundaries) ?? []) as b, i}
            <div class="flex items-center gap-1">
              <span class="w-1 h-1 rounded-full flex-shrink-0" style="background: var(--color-text-tertiary);"></span>
              <span class="flex-1 text-xs" style="color: var(--color-text-primary);">{b}</span>
              {#if canEdit}<button on:click={() => removeItem('boundaries', i)} class="hover:opacity-70"><X class="w-3 h-3" style="color: var(--color-error);" /></button>{/if}
            </div>
          {/each}
        </div>
        {#if canEdit}
          <div class="flex gap-1">
            <input bind:value={newBoundary} placeholder="e.g. ECU only — OEM backend out of scope" class="flex-1 px-2 py-1 text-xs rounded" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem('boundaries', newBoundary); newBoundary = ''; }}} />
            <button on:click={() => { addItem('boundaries', newBoundary); newBoundary = ''; }} class="px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"><Plus class="w-3 h-3" /></button>
          </div>
          {#if !((isEditing ? editedProduct.boundaries : product.boundaries)?.length)}
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">Defines what is in/out of scope for this TARA</p>
          {/if}
        {:else if !product.boundaries?.length}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No boundaries defined</p>
        {/if}
      </div>

      <!-- Objectives -->
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Objectives</div>
        <div class="space-y-1 mb-1">
          {#each ((isEditing ? editedProduct.objectives : product.objectives) ?? []) as o, i}
            <div class="flex items-center gap-1">
              <span class="w-1 h-1 rounded-full flex-shrink-0" style="background: var(--color-text-tertiary);"></span>
              <span class="flex-1 text-xs" style="color: var(--color-text-primary);">{o}</span>
              {#if canEdit}<button on:click={() => removeItem('objectives', i)} class="hover:opacity-70"><X class="w-3 h-3" style="color: var(--color-error);" /></button>{/if}
            </div>
          {/each}
        </div>
        {#if canEdit}
          <div class="flex gap-1">
            <input bind:value={newObjective} placeholder="e.g. Ensure torque command integrity" class="flex-1 px-2 py-1 text-xs rounded" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem('objectives', newObjective); newObjective = ''; }}} />
            <button on:click={() => { addItem('objectives', newObjective); newObjective = ''; }} class="px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"><Plus class="w-3 h-3" /></button>
          </div>
          {#if !((isEditing ? editedProduct.objectives : product.objectives)?.length)}
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">Cybersecurity objectives for this item (used in goal traceability)</p>
          {/if}
        {:else if !product.objectives?.length}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No objectives defined</p>
        {/if}
      </div>

    </div>
  </div>

  <!-- Stakeholders -->
  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Stakeholders</h2>
    <div class="space-y-1 mb-2">
      {#each ((isEditing ? editedProduct.stakeholders : product.stakeholders) ?? []) as s, i}
        <div class="flex items-center gap-2">
          <User class="w-3.5 h-3.5 flex-shrink-0" style="color: var(--color-text-tertiary);" />
          <span class="flex-1 text-xs" style="color: var(--color-text-primary);">{s}</span>
          {#if canEdit}<button on:click={() => removeItem('stakeholders', i)} class="hover:opacity-70"><X class="w-3 h-3" style="color: var(--color-error);" /></button>{/if}
        </div>
      {/each}
    </div>
    {#if canEdit}
      <div class="flex gap-1">
        <input bind:value={newStakeholder} placeholder="e.g. OEM Safety Team, Tier-1 Engineering" class="flex-1 px-2 py-1 text-xs rounded" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
          on:keydown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addItem('stakeholders', newStakeholder); newStakeholder = ''; }}} />
        <button on:click={() => { addItem('stakeholders', newStakeholder); newStakeholder = ''; }} class="px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"><Plus class="w-3 h-3" /></button>
      </div>
    {:else if !product.stakeholders?.length}
      <p class="text-xs" style="color: var(--color-text-tertiary);">No stakeholders defined</p>
    {/if}
  </div>

</div>
