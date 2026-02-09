<script lang="ts">
  import type { Asset, SecurityLevel } from '../../../lib/types/asset';

  export let asset: Asset;

  function getTypeIcon(type: string) {
    switch (type) {
      case 'Firmware': return '💾';
      case 'Software': return '💻';
      case 'Configuration': return '⚙️';
      case 'Calibration': return '🎯';
      case 'Data': return '📊';
      case 'Diagnostic': return '🔍';
      case 'Communication': return '📡';
      case 'Hardware': return '🔧';
      case 'Interface': return '🔌';
      default: return '📦';
    }
  }

  function getSecurityColor(level: SecurityLevel) {
    switch (level) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      case 'N/A': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString();
  }
</script>

<div class="rounded-lg transition-all duration-200 group" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <!-- Card Header -->
  <div class="p-4" style="border-bottom: 1px solid var(--color-border-subtle);">
    <div class="flex items-start justify-between">
      <div class="flex items-center space-x-3">
        <div class="text-2xl">{getTypeIcon(asset.asset_type)}</div>
        <div>
          <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">
            {asset.name}
          </h3>
          <p class="text-xs" style="color: var(--color-text-tertiary);">
            {asset.asset_type} • v{asset.version}
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Card Body -->
  <div class="p-4 space-y-3">
    <!-- Description -->
    {#if asset.description}
      <p class="text-xs line-clamp-2" style="color: var(--color-text-secondary);">
        {asset.description}
      </p>
    {/if}

    <!-- Security Properties (CIA) -->
    <div class="space-y-2">
      <h4 class="text-[10px] font-medium uppercase tracking-wide" style="color: var(--color-text-tertiary);">Security Properties</h4>
      <div class="grid grid-cols-3 gap-2">
        <div class="text-center">
          <div class="text-[10px] mb-1" style="color: var(--color-text-tertiary);">Confidentiality</div>
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium {getSecurityColor(asset.confidentiality)}">
            {asset.confidentiality}
          </span>
        </div>
        <div class="text-center">
          <div class="text-[10px] mb-1" style="color: var(--color-text-tertiary);">Integrity</div>
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium {getSecurityColor(asset.integrity)}">
            {asset.integrity}
          </span>
        </div>
        <div class="text-center">
          <div class="text-[10px] mb-1" style="color: var(--color-text-tertiary);">Availability</div>
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium {getSecurityColor(asset.availability)}">
            {asset.availability}
          </span>
        </div>
      </div>
    </div>

    <!-- Additional Security Requirements -->
    {#if asset.authenticity_required || asset.authorization_required}
      <div class="flex flex-wrap gap-1">
        {#if asset.authenticity_required}
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700">
            Authenticity Required
          </span>
        {/if}
        {#if asset.authorization_required}
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700">
            Authorization Required
          </span>
        {/if}
      </div>
    {/if}

    <!-- Data Types -->
    {#if asset.data_types && asset.data_types.length > 0}
      <div>
        <h4 class="text-[10px] font-medium uppercase tracking-wide mb-1" style="color: var(--color-text-tertiary);">Data Types</h4>
        <div class="flex flex-wrap gap-1">
          {#each asset.data_types.slice(0, 3) as dataType}
            <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-slate-100 text-slate-700">
              {dataType}
            </span>
          {/each}
          {#if asset.data_types.length > 3}
            <span class="text-[10px]" style="color: var(--color-text-tertiary);">
              +{asset.data_types.length - 3} more
            </span>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Storage Location -->
    {#if asset.storage_location}
      <div>
        <h4 class="text-[10px] font-medium uppercase tracking-wide mb-1" style="color: var(--color-text-tertiary);">Storage Location</h4>
        <p class="text-xs" style="color: var(--color-text-secondary);">{asset.storage_location}</p>
      </div>
    {/if}

    <!-- Footer -->
    <div class="text-[10px] pt-2" style="color: var(--color-text-tertiary); border-top: 1px solid var(--color-border-subtle);">
      Created: {formatDate(asset.created_at)}
    </div>
  </div>
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
