<script lang="ts">
  import { auditApi } from '$lib/api/auditApi';
  import type { EvidenceAttachment } from '$lib/api/auditApi';
  import { authStore } from '$lib/stores/auth';

  export let scopeId: string;

  let artifactType = 'damage_scenario';
  let artifactId = '';
  let evidence: EvidenceAttachment[] = [];
  let loading = false;
  let showUpload = false;
  let uploading = false;
  // Upload form
  let uploadTitle = '';
  let uploadEvidenceType = 'test_report';
  let uploadDescription = '';
  let uploadFile: File | null = null;

  const EVIDENCE_TYPES = [
    { value: 'test_report', label: 'Test Report' },
    { value: 'pen_test', label: 'Penetration Test' },
    { value: 'scan_result', label: 'Scan Result' },
    { value: 'design_doc', label: 'Design Document' },
    { value: 'approval_record', label: 'Approval Record' },
  ] as const;

  async function searchEvidence(): Promise<void> {
    if (!artifactId.trim()) return;
    loading = true;
    try {
      evidence = await auditApi.listEvidence(artifactType, artifactId.trim());
    } catch (e) {
      console.error('Failed to load evidence', e);
      evidence = [];
    } finally {
      loading = false;
    }
  }

  async function uploadEvidence(): Promise<void> {
    if (!uploadFile || !uploadTitle || !artifactId) return;
    uploading = true;
    const user = $authStore.user?.email || 'unknown';
    try {
      await auditApi.uploadEvidence(
        artifactType, artifactId.trim(), uploadEvidenceType,
        uploadTitle, user, uploadFile, scopeId, uploadDescription || undefined,
      );
      showUpload = false;
      uploadTitle = '';
      uploadDescription = '';
      uploadFile = null;
      searchEvidence();
    } catch (e) {
      console.error('Upload failed', e);
    } finally {
      uploading = false;
    }
  }

  async function deleteEvidence(evidenceId: string): Promise<void> {
    if (!confirm('Delete this evidence?')) return;
    const user = $authStore.user?.email || 'unknown';
    try {
      await auditApi.deleteEvidence(evidenceId, user);
      searchEvidence();
    } catch (e) {
      console.error('Delete failed', e);
    }
  }

  function handleFileChange(e: Event): void {
    const target = e.target as HTMLInputElement;
    uploadFile = target.files?.[0] || null;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  function formatSize(bytes: number | null): string {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  }

  const TYPE_BADGE: Record<string, string> = {
    test_report: 'bg-blue-100 text-blue-800',
    pen_test: 'bg-red-100 text-red-800',
    scan_result: 'bg-orange-100 text-orange-800',
    design_doc: 'bg-green-100 text-green-800',
    approval_record: 'bg-purple-100 text-purple-800',
  };
</script>

<div>
  <!-- Search bar -->
  <div class="flex items-center gap-3 mb-4">
    <select bind:value={artifactType} class="rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
      <option value="damage_scenario">Damage Scenario</option>
      <option value="threat_scenario">Threat Scenario</option>
      <option value="asset">Asset</option>
      <option value="attack_path">Attack Path</option>
    </select>
    <input bind:value={artifactId} placeholder="Artifact ID (e.g. DS-AUTO-f06f...)"
      class="flex-1 rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
    <button on:click={searchEvidence}
      class="px-3 py-1.5 text-xs rounded-md" style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">Search</button>
    <button on:click={() => showUpload = !showUpload}
      class="px-3 py-1.5 text-xs rounded-md" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Upload</button>
  </div>

  <!-- Upload form -->
  {#if showUpload}
    <div class="rounded-lg p-4 mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
      <h4 class="text-xs font-medium mb-3" style="color: var(--color-text-primary);">Upload Evidence</h4>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label for="ev-title" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Title *</label>
          <input id="ev-title" bind:value={uploadTitle} placeholder="Evidence title"
            class="w-full rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
        </div>
        <div>
          <label for="ev-type" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Type</label>
          <select id="ev-type" bind:value={uploadEvidenceType}
            class="w-full rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
            {#each EVIDENCE_TYPES as t}
              <option value={t.value}>{t.label}</option>
            {/each}
          </select>
        </div>
      </div>
      <div class="mb-3">
        <label for="ev-desc" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Description</label>
        <input id="ev-desc" bind:value={uploadDescription} placeholder="Optional description"
          class="w-full rounded-md px-3 py-1.5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
      </div>
      <div class="mb-3">
        <label for="ev-file" class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">File *</label>
        <input id="ev-file" type="file" on:change={handleFileChange}
          class="w-full rounded-md px-3 py-1.5 text-xs" style="color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
      </div>
      <div class="flex gap-2">
        <button on:click={uploadEvidence} disabled={uploading || !uploadFile || !uploadTitle}
          class="px-3 py-1.5 text-xs rounded-md disabled:opacity-50" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
        <button on:click={() => showUpload = false}
          class="px-3 py-1.5 text-xs rounded-md" style="border: 1px solid var(--color-border-default); color: var(--color-text-secondary);">Cancel</button>
      </div>
    </div>
  {/if}

  <!-- Results -->
  {#if loading}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">Searching...</div>
  {:else if evidence.length === 0 && artifactId}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">No evidence found for {artifactType}/{artifactId}</div>
  {:else if evidence.length > 0}
    <div class="space-y-2">
      {#each evidence as ev}
        <div class="rounded-lg p-3 flex items-center justify-between" style="border: 1px solid var(--color-border-default);">
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="text-xs font-medium" style="color: var(--color-text-primary);">{ev.title}</span>
              <span class="px-2 py-0.5 rounded-full text-xs font-medium {TYPE_BADGE[ev.evidence_type] || 'bg-gray-100'}">
                {ev.evidence_type}
              </span>
            </div>
            <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">
              {ev.filename} · {formatSize(ev.file_size)} · {formatDate(ev.uploaded_at)} · by {ev.uploaded_by}
            </p>
            {#if ev.description}
              <p class="text-[10px] mt-1" style="color: var(--color-text-secondary);">{ev.description}</p>
            {/if}
          </div>
          <button on:click={() => deleteEvidence(ev.evidence_id)}
            class="text-xs ml-3" style="color: var(--color-error);">Delete</button>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">Enter an artifact ID and click Search</div>
  {/if}
</div>
