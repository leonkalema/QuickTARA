<script lang="ts">
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type {
    GapAnalysisResponse,
    GapRequirementItem,
    InventoryItem,
    InventorySummary,
    CraClassification,
  } from '$lib/types/cra';
  import { Shield, Printer, Download, X, ShieldCheck } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    productName: string;
    classification?: CraClassification;
    complianceDeadline?: string;
    onclose: () => void;
  }

  let {
    assessmentId,
    productName,
    classification,
    complianceDeadline,
    onclose,
  }: Props = $props();

  let analysis: GapAnalysisResponse | null = $state(null);
  let inventory: InventoryItem[] = $state([]);
  let inventorySummary: InventorySummary | null = $state(null);
  let loading = $state(true);

  const CLASSIFICATION_LABELS: Record<string, string> = {
    default: 'Default', class_i: 'Class I', class_ii: 'Class II', critical: 'Critical',
  };

  const CLASSIFICATION_DEFINITIONS: Record<string, string> = {
    default: 'Non-critical digital product per CRA Annex III. Eligible for self-assessment (Module A) without third-party involvement.',
    class_i: 'Important product (Class I) per CRA Annex III. Self-assessment permitted if harmonised standards fully cover the product; otherwise third-party assessment required.',
    class_ii: 'Important product (Class II) per CRA Annex III. Mandatory third-party conformity assessment by a notified body (Module B+C or Module H).',
    critical: 'Critical product per CRA Annex IV. Mandatory European cybersecurity certification under an applicable EUCC scheme.',
  };

  const STATUS_DEFINITIONS: Record<string, string> = {
    compliant: 'Implemented, verified through testing or review, and supporting evidence documented.',
    partial: 'Implementation in progress; not yet fully verified or evidence incomplete.',
    not_started: 'No implementation activity has begun.',
    not_applicable: 'Requirement does not apply to this product (justification documented internally).',
  };

  onMount(async () => {
    try {
      const [gapData, invData, invSummary] = await Promise.all([
        craApi.getGapAnalysis(assessmentId),
        craApi.getInventory(assessmentId).catch(() => []),
        craApi.getInventorySummary(assessmentId).catch(() => null),
      ]);
      analysis = gapData;
      inventory = invData;
      inventorySummary = invSummary;
    } catch (err) {
      console.error('Failed to load summary data:', err);
    } finally {
      loading = false;
    }
  });

  function getCompliantRequirements(): GapRequirementItem[] {
    if (!analysis) return [];
    return analysis.requirements.filter(r => !r.is_gap);
  }

  function getStatusLabel(status: string): string {
    const labels: Record<string, string> = { not_started: 'Not Started', partial: 'In Progress', compliant: 'Compliant', not_applicable: 'N/A' };
    return labels[status] ?? status;
  }

  function getSecurityCapabilities(): string[] {
    const caps: string[] = [];
    const compliant = getCompliantRequirements();
    const ids = new Set(compliant.map(r => r.requirement_id));
    if (ids.has('CRA-REQ-01')) caps.push('Secure by design architecture');
    if (ids.has('CRA-REQ-02')) caps.push('No known exploitable vulnerabilities');
    if (ids.has('CRA-REQ-03')) caps.push('Secure default configuration');
    if (ids.has('CRA-REQ-04')) caps.push('Protection against unauthorized access');
    if (ids.has('CRA-REQ-05')) caps.push('Data confidentiality protection');
    if (ids.has('CRA-REQ-06')) caps.push('Data integrity protection');
    if (ids.has('CRA-REQ-07')) caps.push('Data minimization practices');
    if (ids.has('CRA-REQ-08')) caps.push('Availability and resilience');
    if (ids.has('CRA-REQ-09')) caps.push('Minimized attack surface');
    if (ids.has('CRA-REQ-10')) caps.push('Incident impact reduction');
    if (ids.has('CRA-REQ-11')) caps.push('Security monitoring and logging');
    if (ids.has('CRA-REQ-12')) caps.push('Secure software update mechanism');
    if (ids.has('CRA-REQ-13')) caps.push('Vulnerability handling process');
    if (ids.has('CRA-REQ-14')) caps.push('Software Bill of Materials (SBOM)');
    if (ids.has('CRA-REQ-15')) caps.push('Coordinated vulnerability disclosure');
    if (ids.has('CRA-REQ-16')) caps.push('Vulnerability remediation process');
    if (ids.has('CRA-REQ-17')) caps.push('Security information sharing');
    if (ids.has('CRA-REQ-18')) caps.push('Security testing program');
    return caps;
  }

  const CAPABILITY_LABELS: Record<string, string> = {
    'CRA-REQ-01': 'secure design',
    'CRA-REQ-02': 'vulnerability remediation',
    'CRA-REQ-03': 'secure defaults',
    'CRA-REQ-04': 'access control',
    'CRA-REQ-05': 'data confidentiality',
    'CRA-REQ-06': 'data integrity',
    'CRA-REQ-07': 'data minimization',
    'CRA-REQ-08': 'availability & resilience',
    'CRA-REQ-09': 'attack surface reduction',
    'CRA-REQ-10': 'incident impact reduction',
    'CRA-REQ-11': 'logging & monitoring',
    'CRA-REQ-12': 'secure update mechanism',
    'CRA-REQ-13': 'vulnerability handling',
    'CRA-REQ-14': 'SBOM',
    'CRA-REQ-15': 'coordinated disclosure',
    'CRA-REQ-16': 'vulnerability remediation',
    'CRA-REQ-17': 'security information sharing',
    'CRA-REQ-18': 'security testing',
  };

  interface Milestone {
    readonly quarter: string;
    readonly capabilities: string[];
  }

  function getMilestones(): Milestone[] {
    if (!analysis) return [];
    const pending = analysis.requirements.filter(r => r.is_gap && r.target_date);
    if (pending.length === 0) return [];
    const grouped: Record<string, Set<string>> = {};
    for (const req of pending) {
      const d = new Date(req.target_date!);
      const q = `Q${Math.ceil((d.getMonth() + 1) / 3)} ${d.getFullYear()}`;
      if (!grouped[q]) grouped[q] = new Set();
      const cap = CAPABILITY_LABELS[req.requirement_id] ?? req.requirement_name;
      grouped[q].add(cap);
    }
    return Object.entries(grouped)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([quarter, caps]) => ({ quarter, capabilities: [...caps] }));
  }

  function getSupportPeriod(): string {
    if (!complianceDeadline) return 'To be confirmed';
    return 'Minimum 5 years from date of placing on the market';
  }

  function formatDate(d?: string): string {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function today(): string {
    return new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function handlePrint(): void {
    window.print();
  }

  function exportCsv(): void {
    const lines: string[][] = [];
    lines.push(['CRA Customer Compliance Summary']);
    lines.push(['Product', productName]);
    lines.push(['Classification', CLASSIFICATION_LABELS[classification ?? ''] ?? 'Not classified']);
    lines.push(['Support Period', getSupportPeriod()]);
    lines.push(['Generated', today()]);
    lines.push([]);
    lines.push(['--- Security Capabilities ---']);
    getSecurityCapabilities().forEach(cap => lines.push([cap, 'Compliant']));
    lines.push([]);
    lines.push(['--- Compliance Summary ---']);
    lines.push(['Total Requirements', String(analysis?.summary.total ?? 0)]);
    lines.push(['Compliant', String(analysis?.summary.compliant ?? 0)]);
    lines.push([]);
    if (inventory.length > 0) {
      lines.push(['--- Product Inventory ---']);
      lines.push(['SKU', 'Firmware', 'Units in Field', 'Units in Stock', 'OEM Customer', 'Target Market']);
      inventory.forEach(item => {
        lines.push([
          item.sku,
          item.firmware_version ?? '—',
          String(item.units_in_field),
          String(item.units_in_stock),
          item.oem_customer ?? '—',
          item.target_market.toUpperCase(),
        ]);
      });
    }
    const csvContent = lines
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `CRA_Customer_Summary_${productName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
</script>

<svelte:head>
  <style>
    @media print {
      body * { visibility: hidden !important; }
      .customer-summary, .customer-summary * { visibility: visible !important; }
      .customer-summary { position: absolute; left: 0; top: 0; width: 100%; }
      .no-print { display: none !important; }
    }
  </style>
</svelte:head>

<div class="customer-summary">
  <!-- Toolbar -->
  <div class="no-print flex items-center justify-between mb-4 px-4 py-3 rounded-lg border" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="flex items-center gap-2">
      <Shield class="w-4 h-4" style="color: var(--color-status-success);" />
      <span class="text-sm font-semibold" style="color: var(--color-text-primary);">Customer Compliance Summary</span>
      <span class="px-2 py-0.5 rounded text-xs font-medium" style="background: var(--color-status-success)15; color: var(--color-status-success);">EXTERNAL — SHAREABLE</span>
    </div>
    <div class="flex items-center gap-2">
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={handlePrint}
      >
        <Printer class="w-3 h-3" /> Print
      </button>
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
        onclick={exportCsv}
      >
        <Download class="w-3 h-3" /> Export CSV
      </button>
      <button class="p-1.5 rounded cursor-pointer" style="color: var(--color-text-tertiary);" onclick={onclose}>
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if analysis}
    <!-- Report header -->
    <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
      <div class="flex items-start justify-between mb-3">
        <div>
          <h2 class="text-base font-bold" style="color: var(--color-text-primary);">
            CRA Compliance Summary — {productName}
          </h2>
          <p class="text-xs mt-1" style="color: var(--color-text-secondary);">
            EU Cyber Resilience Act (Regulation 2024/2847) compliance status
          </p>
        </div>
        <div class="text-right text-xs" style="color: var(--color-text-tertiary);">
          <div>Generated: {today()}</div>
          <div>Document classification: <strong>EXTERNAL</strong></div>
        </div>
      </div>
      <div class="grid grid-cols-4 gap-4 mt-4">
        <div class="rounded p-3" style="background: var(--color-bg-surface-hover);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Classification</div>
          <div class="text-sm font-semibold mt-0.5" style="color: var(--color-text-primary);">
            {CLASSIFICATION_LABELS[classification ?? ''] ?? 'Not classified'}
          </div>
          <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">
            {CLASSIFICATION_DEFINITIONS[classification ?? ''] ?? ''}
          </p>
        </div>
        <div class="rounded p-3" style="background: var(--color-bg-surface-hover);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Compliance</div>
          <div class="text-sm font-semibold mt-0.5" style="color: var(--color-status-success);">
            {analysis.summary.compliant} / {analysis.summary.total} requirements
          </div>
        </div>
        <div class="rounded p-3" style="background: var(--color-bg-surface-hover);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Support Period</div>
          <div class="text-sm font-semibold mt-0.5" style="color: var(--color-text-primary);">
            {getSupportPeriod()}
          </div>
        </div>
        <div class="rounded p-3" style="background: var(--color-bg-surface-hover);">
          <div class="text-xs" style="color: var(--color-text-tertiary);">Compliance Target</div>
          <div class="text-sm font-semibold mt-0.5" style="color: var(--color-text-primary);">
            {formatDate(complianceDeadline)}
          </div>
        </div>
      </div>
      <!-- Milestone line -->
      {#if getMilestones().length > 0}
        <div class="mt-4 px-3 py-2 rounded text-xs" style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);">
          <strong style="color: var(--color-text-primary);">Milestones:</strong>
          {#each getMilestones() as ms, i}
            <span>
              {ms.quarter} — {ms.capabilities.join(' & ')}{i < getMilestones().length - 1 ? '; ' : '.'}
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Method & Assurance statements -->
    <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
      <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Compliance Methodology</h3>
      <div class="space-y-2 text-xs" style="color: var(--color-text-secondary);">
        <div class="flex items-start gap-2">
          <span class="font-semibold mt-px" style="color: var(--color-text-tertiary);">1.</span>
          <span>Requirements are derived from CRA Annex I (Parts I and II), mapped to 18 essential cybersecurity requirements covering technical, process, and documentation obligations.</span>
        </div>
        <div class="flex items-start gap-2">
          <span class="font-semibold mt-px" style="color: var(--color-text-tertiary);">2.</span>
          <span>"Compliant" means the requirement is fully implemented, verified through testing or review, and supporting evidence is documented. Partial compliance indicates work in progress.</span>
        </div>
        <div class="flex items-start gap-2">
          <span class="font-semibold mt-px" style="color: var(--color-text-tertiary);">3.</span>
          <span>Compliance status is reviewed and updated at least monthly. This summary reflects the status as of the generation date above.</span>
        </div>
      </div>
      <div class="mt-3 px-3 py-2 rounded text-xs" style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);">
        <strong style="color: var(--color-text-primary);">Assurance:</strong>
        A remediation plan exists for all outstanding requirements. Progress is tracked internally on a monthly cadence. Detailed evidence and gap analysis are available under NDA upon request.
      </div>
    </div>

    <!-- Security capabilities -->
    {#if getSecurityCapabilities().length > 0}
      <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Security Capabilities — Verified Compliant</h3>
        <div class="grid grid-cols-2 gap-2">
          {#each getSecurityCapabilities() as cap}
            <div class="flex items-center gap-2 text-sm">
              <ShieldCheck class="w-4 h-4 flex-shrink-0" style="color: var(--color-status-success);" />
              <span style="color: var(--color-text-secondary);">{cap}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Inventory -->
    {#if inventory.length > 0}
      <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">Product Inventory</h3>
        {#if inventorySummary}
          <div class="flex gap-4 mb-3 text-xs" style="color: var(--color-text-secondary);">
            <span>{inventorySummary.total_skus} SKU(s)</span>
            <span>{inventorySummary.total_units_in_field} units in field</span>
            <span>{inventorySummary.total_units_in_stock} units in stock</span>
            {#if inventorySummary.eu_units > 0}
              <span>{inventorySummary.eu_units} EU market units</span>
            {/if}
          </div>
        {/if}
        <div class="overflow-x-auto">
          <table class="w-full text-xs" style="border-collapse: collapse;">
            <thead>
              <tr style="background: var(--color-bg-surface-hover);">
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">SKU</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Firmware</th>
                <th class="px-3 py-2 text-right font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">In Field</th>
                <th class="px-3 py-2 text-right font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">In Stock</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">OEM Customer</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Market</th>
              </tr>
            </thead>
            <tbody>
              {#each inventory as item (item.id)}
                <tr style="border-bottom: 1px solid var(--color-border-subtle);">
                  <td class="px-3 py-2 font-mono" style="color: var(--color-text-primary);">{item.sku}</td>
                  <td class="px-3 py-2" style="color: var(--color-text-secondary);">{item.firmware_version ?? '—'}</td>
                  <td class="px-3 py-2 text-right" style="color: var(--color-text-primary);">{item.units_in_field.toLocaleString()}</td>
                  <td class="px-3 py-2 text-right" style="color: var(--color-text-primary);">{item.units_in_stock.toLocaleString()}</td>
                  <td class="px-3 py-2" style="color: var(--color-text-secondary);">{item.oem_customer ?? '—'}</td>
                  <td class="px-3 py-2" style="color: var(--color-text-secondary);">{item.target_market.toUpperCase()}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    <!-- Annex A: Requirement status overview -->
    {#if analysis}
      <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">Annex A — CRA Requirement Status Overview</h3>
        <p class="text-xs mb-3" style="color: var(--color-text-tertiary);">18 essential requirements per CRA Annex I, Parts I and II. Status definitions below.</p>
        <div class="overflow-x-auto">
          <table class="w-full text-xs" style="border-collapse: collapse;">
            <thead>
              <tr style="background: var(--color-bg-surface-hover);">
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">ID</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Requirement</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Article</th>
                <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Status</th>
              </tr>
            </thead>
            <tbody>
              {#each analysis.requirements as req (req.requirement_id)}
                <tr style="border-bottom: 1px solid var(--color-border-subtle);">
                  <td class="px-3 py-1.5 font-mono" style="color: var(--color-text-tertiary);">{req.requirement_id}</td>
                  <td class="px-3 py-1.5" style="color: var(--color-text-primary);">{req.requirement_name}</td>
                  <td class="px-3 py-1.5" style="color: var(--color-text-tertiary);">{req.article}</td>
                  <td class="px-3 py-1.5" style="color: {req.status === 'compliant' ? 'var(--color-status-success)' : req.status === 'partial' ? 'var(--color-status-warning)' : 'var(--color-text-secondary)'};">
                    {getStatusLabel(req.status)}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <div class="mt-3 grid grid-cols-4 gap-2 text-xs">
          {#each Object.entries(STATUS_DEFINITIONS) as [key, def]}
            <div>
              <span class="font-semibold" style="color: {key === 'compliant' ? 'var(--color-status-success)' : key === 'partial' ? 'var(--color-status-warning)' : 'var(--color-text-secondary)'};">
                {getStatusLabel(key)}:
              </span>
              <span style="color: var(--color-text-tertiary);">{def}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Applicable standards -->
    <div class="rounded-lg border p-5 mb-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
      <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Applicable Standards & Frameworks</h3>
      <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="flex items-start gap-2">
          <ShieldCheck class="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style="color: var(--color-status-success);" />
          <div>
            <div class="font-medium" style="color: var(--color-text-primary);">EU Cyber Resilience Act (2024/2847)</div>
            <div style="color: var(--color-text-tertiary);">Compliance tracked via this assessment</div>
          </div>
        </div>
        <div class="flex items-start gap-2">
          <ShieldCheck class="w-3.5 h-3.5 mt-0.5 flex-shrink-0" style="color: var(--color-status-success);" />
          <div>
            <div class="font-medium" style="color: var(--color-text-primary);">ISO/SAE 21434</div>
            <div style="color: var(--color-text-tertiary);">Automotive cybersecurity engineering</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="text-xs text-center py-3" style="color: var(--color-text-tertiary);">
      This document contains compliance information suitable for external distribution.
      Internal gap details, risk assessments, and remediation plans are excluded.
      Detailed evidence available under NDA upon request.
    </div>
  {/if}
</div>
