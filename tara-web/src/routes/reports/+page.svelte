<script lang="ts">
  import { onMount } from 'svelte';
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

  onMount(async () => {
    if ($selectedProduct?.scope_id) {
      await loadData();
    }
  });

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

  function getRiskLevel(impactLevel: string, feasibilityLevel: string): string {
    const riskMatrix: Record<string, Record<string, string>> = {
      "Severe": {"Very High": "Critical", "High": "Critical", "Medium": "High", "Low": "Medium", "Very Low": "Medium"},
      "Major": {"Very High": "High", "High": "High", "Medium": "Medium", "Low": "Low", "Very Low": "Low"},
      "Moderate": {"Very High": "Medium", "High": "Medium", "Medium": "Low", "Low": "Low", "Very Low": "Low"},
      "Negligible": {"Very High": "Low", "High": "Low", "Medium": "Low", "Low": "Low", "Very Low": "Low"}
    };
    
    return riskMatrix[impactLevel]?.[feasibilityLevel] || 'Unknown';
  }

  function getRiskLevelColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'Critical': return 'text-red-800';
      case 'High': return 'text-orange-800';
      case 'Medium': return 'text-yellow-800';
      case 'Low': return 'text-green-800';
      default: return 'text-gray-800';
    }
  }

  function formatDate(date: Date): string {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  function getAttackPathsForThreat(threatScenarioId: string): AttackPath[] {
    return attackPaths.filter(ap => ap.threat_scenario_id === threatScenarioId);
  }

  function getThreatScenarioName(threatScenarioId: string): string {
    const scenario = threatScenarios.find(ts => ts.threat_scenario_id === threatScenarioId);
    return scenario?.name || 'Unknown Threat Scenario';
  }

  function getAttackPathAFR(afs: number): string {
    if (afs >= 25) return 'Very Low';
    if (afs >= 20) return 'Low';
    if (afs >= 14) return 'Medium';
    if (afs >= 1) return 'High';
    return 'Very High';
  }

  async function generateTARAReport() {
    if (!$selectedProduct) {
      notifications.show('Please select a product first', 'error');
      return;
    }

    generating = true;
    try {
      // Call backend PDF generation endpoint
      const response = await fetch(`${API_BASE_URL}/reports/tara-pdf/${$selectedProduct.scope_id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to generate PDF: ${response.statusText}`);
      }
      
      // Download the PDF
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `TARA_Report_${$selectedProduct.name?.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      notifications.show('TARA PDF report generated successfully', 'success');
    } catch (error) {
      console.error('Error generating report:', error);
      notifications.show('Failed to generate PDF report', 'error');
    } finally {
      generating = false;
    }
  }

  function generateReportHTML(): string {
    const currentDate = formatDate(new Date());
    
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TARA Report - ${$selectedProduct?.name}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 40px; border-bottom: 2px solid #333; padding-bottom: 20px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
        .section h3 { color: #555; margin-top: 25px; }
        .risk-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .risk-table th, .risk-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .risk-table th { background-color: #f5f5f5; font-weight: bold; }
        .risk-critical { background-color: #fee; }
        .risk-high { background-color: #fef0e6; }
        .risk-medium { background-color: #fffbf0; }
        .risk-low { background-color: #f0f9f0; }
        .treatment-summary { background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-left: 4px solid #007bff; }
        .metadata { font-size: 12px; color: #666; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Threat Analysis and Risk Assessment (TARA)</h1>
        <h2>Product: ${$selectedProduct?.name}</h2>
        <p>Generated on: ${currentDate}</p>
        <p>ISO 21434 Regulatory Submission</p>
    </div>

    <div class="section">
        <h2>1. Executive Summary</h2>
        <p>This document presents the Threat Analysis and Risk Assessment (TARA) for <strong>${$selectedProduct?.name}</strong> conducted in accordance with ISO 21434:2021 cybersecurity engineering standards for automotive systems.</p>
        
        <h3>Risk Summary</h3>
        <ul>
            <li>Assets Analyzed: ${riskTreatmentData.length}</li>
            <li>Threat Scenarios Identified: ${threatScenarios.length}</li>
            <li>Critical Risks: ${riskTreatmentData.filter(r => getRiskLevel(r.impact_level || 'Unknown', r.feasibility_level || 'Unknown') === 'Critical').length}</li>
            <li>High Risks: ${riskTreatmentData.filter(r => getRiskLevel(r.impact_level || 'Unknown', r.feasibility_level || 'Unknown') === 'High').length}</li>
        </ul>
    </div>

    <div class="section">
        <h2>2. Product and Scope</h2>
        <p><strong>Product:</strong> ${$selectedProduct?.name || 'Unknown Product'}</p>
        <p><strong>Description:</strong> ${$selectedProduct?.description || 'No description provided'}</p>
        <p><strong>Assessment Scope:</strong> Cybersecurity analysis of all identified assets and their associated damage scenarios.</p>
    </div>

    <div class="section">
        <h2>3. Risk Assessment Results</h2>
        <table class="risk-table">
            <thead>
                <tr>
                    <th>Asset/Component</th>
                    <th>Damage Scenario</th>
                    <th>Impact Level</th>
                    <th>Risk Level</th>
                    <th>Treatment Decision</th>
                </tr>
            </thead>
            <tbody>
                ${riskTreatmentData.map(scenario => {
                    const riskLevel = getRiskLevel(scenario.impact_level || 'Unknown', scenario.feasibility_level || 'Unknown');
                    const rowClass = `risk-${riskLevel.toLowerCase()}`;
                    return `
                    <tr class="${rowClass}">
                        <td>${scenario.name}</td>
                        <td>${scenario.description}</td>
                        <td>${scenario.impact_level || 'Unknown'}</td>
                        <td><strong>${riskLevel}</strong></td>
                        <td>${scenario.selected_treatment || scenario.suggested_treatment || 'To be determined'}</td>
                    </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>4. Threat Scenarios</h2>
        ${threatScenarios.map(threat => {
            return `
            <h3>${threat.name}</h3>
            <p>${threat.description || 'No description provided'}</p>
            `;
        }).join('')}
    </div>

    <div class="section">
        <h2>5. Risk Treatment Strategy</h2>
        ${riskTreatmentData.filter(scenario => scenario.treatment_goal || scenario.selected_treatment).map(scenario => `
            <div class="treatment-summary">
                <h4>${scenario.name}</h4>
                <p><strong>Risk Level:</strong> ${getRiskLevel(scenario.impact_level || 'Unknown', scenario.feasibility_level || 'Unknown')}</p>
                <p><strong>Treatment:</strong> ${scenario.selected_treatment || scenario.suggested_treatment || 'Not specified'}</p>
                ${scenario.treatment_goal ? `<p><strong>Goal:</strong> ${scenario.treatment_goal}</p>` : ''}
                <p><strong>Status:</strong> ${scenario.treatment_status || 'Draft'}</p>
            </div>
        `).join('')}
    </div>

    <div class="section">
        <h2>6. Compliance Statement</h2>
        <p>This TARA has been conducted in accordance with:</p>
        <ul>
            <li><strong>ISO 21434:2021</strong> - Road vehicles — Cybersecurity engineering</li>
            <li><strong>UN-ECE WP.29</strong> - Regulation on Cybersecurity Management System</li>
        </ul>
        
        <p>The assessment methodology includes:</p>
        <ul>
            <li>Asset identification and cybersecurity property analysis</li>
            <li>Damage scenario development based on potential cybersecurity impacts</li>
            <li>Threat scenario identification and feasibility assessment</li>
            <li>Risk determination and treatment decision</li>
        </ul>
        
        <p><strong>Conclusion:</strong> All identified risks have been assessed and appropriate treatment strategies have been defined in accordance with regulatory requirements.</p>
    </div>

    <div class="metadata">
        <p><strong>Document Control:</strong></p>
        <p>Generated: ${currentDate} | Tool: QuickTARA | Product: ${$selectedProduct?.name}</p>
        <p>This document satisfies ISO 21434 TARA documentation requirements for regulatory submission.</p>
    </div>
</body>
</html>
    `;
  }

  function downloadReport(htmlContent: string) {
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TARA_Report_${$selectedProduct?.name?.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Product Selected</h3>
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Select a product from the header to generate reports.</p>
        <a href="/products" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Select a Product</a>
      </div>
    </div>
  {:else if loading}
    <div class="flex flex-col items-center py-16">
      <div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent mb-3" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
      <p class="text-sm" style="color: var(--color-text-tertiary);">Loading report data...</p>
    </div>
  {:else}
    <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <h2 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">Complete TARA Package</h2>
      <p class="text-xs mb-4" style="color: var(--color-text-secondary);">
        ISO 21434 compliant report with all scenarios, attack paths, and treatment plans.
      </p>

      <div class="rounded-md p-3 mb-4" style="background: var(--color-info-bg); border: 1px solid var(--color-info);">
        <h3 class="text-xs font-medium mb-1.5" style="color: var(--color-info);">Report Contents</h3>
        <ul class="text-xs space-y-0.5" style="color: var(--color-text-secondary);">
          <li>- Executive Summary with risk overview</li>
          <li>- Product scope and asset inventory</li>
          <li>- Damage & threat scenario analysis</li>
          <li>- Attack paths and feasibility ratings</li>
          <li>- Risk treatment strategies</li>
          <li>- ISO 21434 compliance statement</li>
        </ul>
      </div>

      <div class="grid grid-cols-3 gap-3 mb-5">
        <div class="rounded-md p-3 text-center" style="background: var(--color-bg-elevated);">
          <div class="text-lg font-bold" style="color: var(--color-text-primary);">{riskTreatmentData.length}</div>
          <div class="text-[11px]" style="color: var(--color-text-tertiary);">Damage Scenarios</div>
        </div>
        <div class="rounded-md p-3 text-center" style="background: var(--color-bg-elevated);">
          <div class="text-lg font-bold" style="color: var(--color-text-primary);">{threatScenarios.length}</div>
          <div class="text-[11px]" style="color: var(--color-text-tertiary);">Threat Scenarios</div>
        </div>
        <div class="rounded-md p-3 text-center" style="background: var(--color-bg-elevated);">
          <div class="text-lg font-bold" style="color: var(--color-text-primary);">{attackPaths.length}</div>
          <div class="text-[11px]" style="color: var(--color-text-tertiary);">Attack Paths</div>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          on:click={generateTARAReport}
          disabled={generating || riskTreatmentData.length === 0}
          class="px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        >
          {#if generating}
            <div class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></div>
            Generating...
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            Generate TARA Report
          {/if}
        </button>
      </div>

      {#if riskTreatmentData.length === 0}
        <div class="mt-4 rounded-md p-3" style="background: var(--color-warning-bg); border: 1px solid var(--color-warning);">
          <h3 class="text-xs font-medium" style="color: var(--color-warning);">No Data Available</h3>
          <p class="text-xs mt-0.5" style="color: var(--color-text-secondary);">
            Complete the TARA workflow (damage scenarios → threat scenarios → risk assessment) before generating reports.
          </p>
        </div>
      {/if}
    </div>
  {/if}
</div>
