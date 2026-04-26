<script lang="ts">
  import { selectedProduct } from '$lib/stores/productStore';
  import { notifications } from '$lib/stores/notificationStore';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { attackPathApi } from '$lib/api/attackPathApi';
  import { riskTreatmentApi } from '$lib/api/riskTreatmentApi';
  import { API_BASE_URL } from '$lib/config';
  import type { ThreatScenario } from '$lib/types/threatScenario';
  import type { AttackPath } from '$lib/types/attackPath';
  import type { RiskTreatmentData } from '$lib/api/riskTreatmentApi';

  let loading = false;
  let generating = false;
  let threatScenarios: ThreatScenario[] = [];
  let attackPaths: AttackPath[] = [];
  let riskTreatmentData: RiskTreatmentData[] = [];

  $: if ($selectedProduct?.scope_id) {
    loadData();
  }

  async function loadData() {
    if (!$selectedProduct?.scope_id) return;
    
    loading = true;
    try {
      const [threatResponse, attackPathResponse, riskResponse] = await Promise.all([
        threatScenarioApi.getThreatScenariosByProduct($selectedProduct.scope_id),
        attackPathApi.getByProduct($selectedProduct.scope_id),
        riskTreatmentApi.getRiskTreatmentData($selectedProduct.scope_id)
      ]);
      
      threatScenarios = threatResponse.threat_scenarios;
      attackPaths = attackPathResponse.attack_paths;
      riskTreatmentData = riskResponse.damage_scenarios;
      
    } catch (error) {
      console.error('Error loading data:', error);
      notifications.show('Failed to load report data', 'error');
    } finally {
      loading = false;
    }
  }

  function getRiskLevelColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'Critical': return 'var(--color-risk-critical)';
      case 'High': return 'var(--color-risk-high)';
      case 'Medium': return 'var(--color-risk-medium)';
      case 'Low': return 'var(--color-risk-low)';
      default: return 'var(--color-text-tertiary)';
    }
  }

  $: readinessChecks = [
    { label: 'Damage scenarios defined', done: riskTreatmentData.length > 0 },
    { label: 'Threat scenarios identified', done: threatScenarios.length > 0 },
    { label: 'Attack paths analysed', done: attackPaths.length > 0 },
    { label: 'Risk treatments decided', done: riskTreatmentData.some(r => r.selected_treatment) },
    { label: 'At least one treatment approved', done: riskTreatmentData.some(r => r.treatment_status === 'approved') },
  ];

  $: readinessScore = readinessChecks.filter(c => c.done).length;
  $: readinessPercent = Math.round((readinessScore / readinessChecks.length) * 100);
  $: reportReady = readinessScore >= 4;

  type ExportFormat = 'pdf' | 'json' | 'excel' | 'text';
  let selectedFormat: ExportFormat = 'pdf';

  const FORMAT_OPTIONS: { value: ExportFormat; label: string; mime: string; ext: string }[] = [
    { value: 'pdf',   label: 'PDF (ISO 21434)',  mime: 'application/pdf',        ext: 'pdf'  },
    { value: 'excel', label: 'Excel (.xlsx)',     mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', ext: 'xlsx' },
    { value: 'json',  label: 'JSON (machine)',    mime: 'application/json',       ext: 'json' },
    { value: 'text',  label: 'Plain text',        mime: 'text/plain',             ext: 'txt'  },
  ];

  async function generateTARAReport(): Promise<void> {
    if (!$selectedProduct) {
      notifications.show('Please select a product first', 'error');
      return;
    }
    generating = true;
    try {
      const scopeId = $selectedProduct.scope_id;
      const productName = $selectedProduct.name?.replace(/\s+/g, '_') ?? 'report';
      const dateStr = new Date().toISOString().split('T')[0];
      const fmt = FORMAT_OPTIONS.find(f => f.value === selectedFormat)!;

      const url = selectedFormat === 'pdf'
        ? `${API_BASE_URL}/reports/${scopeId}/pdf`
        : `${API_BASE_URL}/reports/${scopeId}/export/${selectedFormat}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token') ?? ''}` }
      });

      if (!response.ok) {
        const detail = await response.text().catch(() => response.statusText);
        throw new Error(detail);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = objectUrl;
      a.download = `TARA_${productName}_${dateStr}.${fmt.ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(objectUrl);

      notifications.show(`TARA report downloaded as ${fmt.label}`, 'success');
    } catch (error: any) {
      console.error('Error generating report:', error);
      notifications.show(error.message ?? 'Failed to generate report', 'error');
    } finally {
      generating = false;
    }
  }
</script>

<svelte:head>
  <title>Reports - QuickTARA</title>
</svelte:head>

<div class="space-y-5">
  <!-- Header -->
  <div>
    <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">Reports</h1>
    <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
      {#if $selectedProduct}
        Generate TARA documentation for <strong style="color: var(--color-text-primary);">{$selectedProduct.name}</strong>.
      {:else}
        Select a product to generate reports.
      {/if}
    </p>
  </div>

  {#if !$selectedProduct}
    <div class="rounded-xl border border-dashed py-20 text-center" style="border-color: var(--color-border-default);">
      <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style="background: var(--color-bg-elevated);">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
      </div>
      <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No product selected</h3>
      <p class="text-sm mb-6 max-w-sm mx-auto" style="color: var(--color-text-tertiary);">Select a product from the header dropdown to generate TARA reports.</p>
      <a href="/products" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Go to Products</a>
    </div>
  {:else if loading}
    <div class="flex flex-col items-center py-16">
      <div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent mb-3" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
      <p class="text-sm" style="color: var(--color-text-tertiary);">Loading report data...</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 items-start">

      <!-- Left: Readiness + Generate -->
      <div class="lg:col-span-2 space-y-4">

        <!-- Readiness card -->
        <div class="rounded-xl p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold" style="color: var(--color-text-primary);">Report Readiness</h2>
            <span class="text-xs font-bold px-2 py-0.5 rounded"
              style="background: {reportReady ? 'rgba(34,197,94,0.1)' : 'rgba(251,191,36,0.1)'}; color: {reportReady ? 'var(--color-status-success)' : '#fbbf24'};">
              {readinessPercent}% complete
            </span>
          </div>

          <!-- Progress bar -->
          <div class="w-full rounded-full h-1.5 mb-4" style="background: var(--color-bg-elevated);">
            <div class="h-1.5 rounded-full transition-all duration-500"
              style="width: {readinessPercent}%; background: {reportReady ? 'var(--color-status-success)' : '#fbbf24'};"></div>
          </div>

          <ul class="space-y-2.5">
            {#each readinessChecks as check}
              <li class="flex items-center gap-3">
                {#if check.done}
                  <div class="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center" style="background: rgba(34,197,94,0.12);">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-status-success);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                  </div>
                {:else}
                  <div class="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center" style="background: var(--color-bg-elevated);">
                    <div class="w-1.5 h-1.5 rounded-full" style="background: var(--color-border-default);"></div>
                  </div>
                {/if}
                <span class="text-xs" style="color: {check.done ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)'};">{check.label}</span>
              </li>
            {/each}
          </ul>
        </div>

        <!-- Generate card -->
        <div class="rounded-xl p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
          <h2 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">Generate Report</h2>
          <p class="text-xs mb-4" style="color: var(--color-text-secondary);">
            ISO 21434 compliant TARA document — executive summary, risk register, treatment strategies, and compliance statement.
          </p>

          {#if !reportReady}
            <div class="rounded-lg p-3 mb-4 flex items-start gap-2.5" style="background: rgba(251,191,36,0.07); border: 1px solid rgba(251,191,36,0.3);">
              <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #fbbf24;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
              <p class="text-xs" style="color: var(--color-text-secondary);">
                Complete the checklist above to generate a comprehensive report. A partial report may be generated but will have missing sections.
              </p>
            </div>
          {/if}

          <!-- Format selector -->
          <div class="flex items-center gap-2 mb-3">
            <label for="export-format" class="text-xs font-medium whitespace-nowrap" style="color: var(--color-text-secondary);">Format</label>
            <select id="export-format" bind:value={selectedFormat}
              class="flex-1 px-2 py-1.5 text-xs rounded-lg"
              style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
              {#each FORMAT_OPTIONS as opt}
                <option value={opt.value}>{opt.label}</option>
              {/each}
            </select>
          </div>

          <button
            on:click={generateTARAReport}
            disabled={generating || riskTreatmentData.length === 0}
            class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
            style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
          >
            {#if generating}
              <div class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></div>
              Generating...
            {:else}
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              {reportReady ? 'Download Full TARA Report' : 'Download Partial Report'}
            {/if}
          </button>
        </div>
      </div>

      <!-- Right: Stats sidebar -->
      <div class="space-y-3">
        <h3 class="text-xs font-semibold uppercase tracking-wide" style="color: var(--color-text-tertiary);">TARA Summary</h3>
        {#each [
          { label: 'Damage Scenarios', value: riskTreatmentData.length, icon: 'M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z' },
          { label: 'Threat Scenarios', value: threatScenarios.length, icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
          { label: 'Attack Paths', value: attackPaths.length, icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
          { label: 'Approved Treatments', value: riskTreatmentData.filter(r => r.treatment_status === 'approved').length, icon: 'M5 13l4 4L19 7' },
        ] as stat}
          <div class="rounded-xl px-4 py-3 flex items-center gap-3" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style="background: var(--color-bg-elevated);">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="{stat.icon}"/></svg>
            </div>
            <div>
              <div class="text-lg font-bold leading-none" style="color: {stat.value > 0 ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)'};">{stat.value}</div>
              <div class="text-[11px] mt-0.5" style="color: var(--color-text-tertiary);">{stat.label}</div>
            </div>
          </div>
        {/each}
      </div>

    </div>
  {/if}
</div>
