<script lang="ts">
  /**
   * CRA Art. 13(6) — SBOM upload and inspection.
   *
   * Used by: routes/cra/[id]/+page.svelte
   * Depends on: lib/api/craApi.ts (uploadSbom, listSboms, getSbom, deleteSbom)
   */
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type { SbomDetail, SbomListItem } from '$lib/types/cra';
  import {
    Upload, Package, Trash2, ChevronDown, ChevronRight,
    AlertTriangle, FileCode, Calendar, Clock, ExternalLink,
  } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    onupdate?: () => void;
  }

  let { assessmentId, onupdate }: Props = $props();

  let sboms: SbomListItem[] = $state([]);
  let loading = $state(true);
  let uploading = $state(false);
  let uploadError: string | null = $state(null);
  let uploadWarnings: string[] = $state([]);
  let deletingId: string | null = $state(null);
  let expandedId: string | null = $state(null);
  let detailCache: Record<string, SbomDetail> = $state({});
  let detailLoadingId: string | null = $state(null);
  let fileInput: HTMLInputElement | undefined = $state();

  async function loadSboms(): Promise<void> {
    loading = true;
    try {
      sboms = await craApi.listSboms(assessmentId);
    } catch (err) {
      console.error('Failed to load SBOMs:', err);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadSboms();
  });

  async function handleFileSelected(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    uploadError = null;
    uploadWarnings = [];
    uploading = true;

    try {
      const result = await craApi.uploadSbom(assessmentId, file);
      uploadWarnings = [...result.warnings];
      await loadSboms();
      onupdate?.();
    } catch (err) {
      uploadError = err instanceof Error ? err.message : 'Upload failed';
    } finally {
      uploading = false;
      if (fileInput) fileInput.value = '';
    }
  }

  async function toggleExpanded(sbom: SbomListItem): Promise<void> {
    if (expandedId === sbom.id) {
      expandedId = null;
      return;
    }
    expandedId = sbom.id;
    if (!detailCache[sbom.id]) {
      detailLoadingId = sbom.id;
      try {
        detailCache[sbom.id] = await craApi.getSbom(sbom.id);
      } catch (err) {
        console.error('Failed to load SBOM detail:', err);
      } finally {
        detailLoadingId = null;
      }
    }
  }

  async function deleteSbom(sbom: SbomListItem): Promise<void> {
    if (!confirm(`Delete this SBOM (${sbom.component_count} components)? This does not affect TARA data.`)) return;
    deletingId = sbom.id;
    try {
      await craApi.deleteSbom(sbom.id);
      delete detailCache[sbom.id];
      if (expandedId === sbom.id) expandedId = null;
      await loadSboms();
      onupdate?.();
    } catch (err) {
      console.error('Failed to delete SBOM:', err);
    } finally {
      deletingId = null;
    }
  }

  function formatBytes(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MiB`;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  function formatLabel(format: string): string {
    return format === 'cyclonedx' ? 'CycloneDX' : 'SPDX';
  }
</script>

<div class="space-y-4">
  <!-- Header / explainer -->
  <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h2 class="text-sm font-semibold flex items-center gap-2" style="color: var(--color-text-primary);">
          <FileCode class="w-4 h-4" style="color: var(--color-accent-primary);" />
          Software Bill of Materials
        </h2>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary);">
          CRA Art. 13(6) — manufacturers must identify components in a machine-readable format.
          Upload a CycloneDX (1.4–1.6) or SPDX (2.3) JSON file. Uploading sets <strong>CRA-10</strong>
          to <em>partial</em>; mark it compliant once you've signed off completeness and accuracy.
        </p>
      </div>
      <div>
        <input
          type="file"
          accept=".json,application/json"
          class="hidden"
          bind:this={fileInput}
          onchange={handleFileSelected}
          aria-label="SBOM file input"
        />
        <button
          class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium cursor-pointer disabled:opacity-50 transition-colors"
          style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
          onclick={() => fileInput?.click()}
          disabled={uploading}
        >
          <Upload class="w-3.5 h-3.5" />
          {uploading ? 'Uploading…' : 'Upload SBOM'}
        </button>
      </div>
    </div>

    {#if uploadError}
      <div class="mt-3 rounded-md p-3 flex items-start gap-2.5" role="alert" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.35);">
        <AlertTriangle class="w-4 h-4 flex-shrink-0 mt-0.5" style="color: var(--color-status-error);" />
        <div class="text-xs" style="color: var(--color-status-error);">{uploadError}</div>
      </div>
    {/if}

    {#if uploadWarnings.length > 0}
      <div class="mt-3 rounded-md p-3" style="background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.35);">
        <div class="text-xs font-semibold mb-1" style="color: var(--color-status-warning);">Parser warnings</div>
        <ul class="text-xs space-y-0.5 list-disc pl-4" style="color: var(--color-text-secondary);">
          {#each uploadWarnings as w}
            <li>{w}</li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>

  <!-- List -->
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div role="status" aria-label="Loading SBOMs" class="animate-spin rounded-full h-5 w-5 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if sboms.length === 0}
    <div class="rounded-xl border border-dashed py-16 text-center" style="border-color: var(--color-border-default);">
      <div class="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3" style="background: var(--color-bg-elevated);">
        <Package class="w-6 h-6" style="color: var(--color-text-tertiary);" />
      </div>
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No SBOM uploaded</h3>
      <p class="text-xs max-w-sm mx-auto" style="color: var(--color-text-tertiary);">
        Generate one with Syft, CycloneDX-cli, or your build pipeline, then upload it here.
      </p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each sboms as sbom (sbom.id)}
        {@const isOpen = expandedId === sbom.id}
        {@const detail = detailCache[sbom.id]}
        <div class="rounded-lg border overflow-hidden" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="flex items-stretch">
            <button
              type="button"
              class="flex-1 min-w-0 text-left px-4 py-3 flex items-center gap-3 cursor-pointer transition-colors hover:bg-[var(--color-bg-surface-hover)]"
              onclick={() => toggleExpanded(sbom)}
              aria-expanded={isOpen}
            >
              <span class="flex-shrink-0" style="color: var(--color-text-tertiary);">
                {#if isOpen}
                  <ChevronDown class="w-4 h-4" />
                {:else}
                  <ChevronRight class="w-4 h-4" />
                {/if}
              </span>
              <Package class="w-4 h-4 flex-shrink-0" style="color: var(--color-accent-primary);" />
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium truncate" style="color: var(--color-text-primary);">
                  {sbom.primary_component_name ?? sbom.document_name ?? 'SBOM'}
                  {#if sbom.primary_component_version}
                    <span class="font-normal" style="color: var(--color-text-tertiary);">
                      @ {sbom.primary_component_version}
                    </span>
                  {/if}
                </div>
                <div class="flex items-center gap-3 mt-0.5 text-xs" style="color: var(--color-text-tertiary);">
                  <span class="inline-flex items-center gap-1">
                    <FileCode class="w-3 h-3" />
                    {formatLabel(sbom.sbom_format)} {sbom.spec_version}
                  </span>
                  <span>{sbom.component_count} components</span>
                  <span>{formatBytes(sbom.raw_size_bytes)}</span>
                  <span class="inline-flex items-center gap-1">
                    <Clock class="w-3 h-3" />
                    {formatDate(sbom.uploaded_at)}
                  </span>
                </div>
              </div>
            </button>
            <button
              type="button"
              class="flex-shrink-0 px-3 cursor-pointer transition-colors hover:bg-[rgba(239,68,68,0.1)]"
              style="color: var(--color-status-error);"
              onclick={() => deleteSbom(sbom)}
              disabled={deletingId === sbom.id}
              aria-label="Delete SBOM"
              title="Delete SBOM"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>

          {#if isOpen}
            <div class="border-t px-4 py-3" style="border-color: var(--color-border-subtle); background: var(--color-bg-elevated);">
              {#if detailLoadingId === sbom.id || !detail}
                <div class="flex items-center justify-center py-6">
                  <div class="animate-spin rounded-full h-4 w-4 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
                </div>
              {:else}
                {#if detail.serial_number}
                  <div class="text-xs mb-3" style="color: var(--color-text-tertiary);">
                    <span class="font-semibold">Serial:</span>
                    <code class="ml-1" style="color: var(--color-text-secondary);">{detail.serial_number}</code>
                  </div>
                {/if}

                {#if detail.components.length === 0}
                  <p class="text-xs italic" style="color: var(--color-text-tertiary);">
                    No components recorded in this SBOM.
                  </p>
                {:else}
                  <div class="overflow-x-auto rounded border" style="border-color: var(--color-border-subtle);">
                    <table class="w-full text-xs">
                      <thead style="background: var(--color-bg-surface);">
                        <tr>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">Name</th>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">Version</th>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">Type</th>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">Supplier</th>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">License</th>
                          <th class="text-left px-3 py-2 font-semibold" style="color: var(--color-text-secondary);">purl</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each detail.components as comp (comp.id)}
                          <tr style="border-top: 1px solid var(--color-border-subtle);">
                            <td class="px-3 py-1.5 font-medium" style="color: var(--color-text-primary);">{comp.name}</td>
                            <td class="px-3 py-1.5" style="color: var(--color-text-secondary);">{comp.version ?? '—'}</td>
                            <td class="px-3 py-1.5" style="color: var(--color-text-tertiary);">{comp.component_type ?? '—'}</td>
                            <td class="px-3 py-1.5" style="color: var(--color-text-secondary);">{comp.supplier ?? '—'}</td>
                            <td class="px-3 py-1.5" style="color: var(--color-text-secondary);">
                              {comp.licenses.length > 0 ? comp.licenses.join(', ') : '—'}
                            </td>
                            <td class="px-3 py-1.5 font-mono text-[10px]" style="color: var(--color-text-tertiary);">
                              {comp.purl ?? '—'}
                            </td>
                          </tr>
                        {/each}
                      </tbody>
                    </table>
                  </div>
                  <div class="mt-2 text-[11px]" style="color: var(--color-text-tertiary);">
                    {detail.components.length} components shown.
                    Components with a <code>purl</code> can be matched against NVD when CVE feed integration ships.
                  </div>
                {/if}
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
