<script lang="ts">
	import { onMount } from 'svelte';
	import { ShieldAlert, Download, RefreshCw, CheckCircle, AlertTriangle } from '@lucide/svelte';
	import { API_BASE_URL } from '$lib/config';
	import { authStore } from '$lib/stores/auth';
	import { get } from 'svelte/store';

	interface CatalogStats {
		total: number;
		mitre_attack_ics: number;
		custom: number;
		user_modified: number;
	}

	interface SeedResult {
		created: number;
		updated: number;
		skipped: number;
		error?: string;
	}

	let stats: CatalogStats | null = null;
	let loading = false;
	let seeding = false;
	let seedResult: SeedResult | null = null;
	let error: string | null = null;

	function getAuthHeaders(): HeadersInit {
		const auth = get(authStore);
		const token = auth.token ?? localStorage.getItem('auth_token');
		const headers: HeadersInit = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;
		return headers;
	}

	async function loadStats(): Promise<void> {
		loading = true;
		error = null;
		try {
			const resp = await fetch(`${API_BASE_URL}/threat/catalog/stats`, {
				headers: getAuthHeaders()
			});
			if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
			stats = await resp.json();
		} catch (err) {
			error = 'Failed to load catalog stats';
			console.error('Catalog stats error:', err);
		} finally {
			loading = false;
		}
	}

	async function seedCatalog(forceUpdate = false): Promise<void> {
		seeding = true;
		seedResult = null;
		error = null;
		try {
			const url = `${API_BASE_URL}/threat/catalog/seed-mitre?force_update=${forceUpdate}`;
			const resp = await fetch(url, {
				method: 'POST',
				headers: getAuthHeaders()
			});
			if (!resp.ok) {
				const body = await resp.json().catch(() => ({}));
				throw new Error(body.detail || `HTTP ${resp.status}`);
			}
			seedResult = await resp.json();
			await loadStats();
		} catch (err: any) {
			error = err.message || 'Failed to seed catalog';
		} finally {
			seeding = false;
		}
	}

	onMount(() => {
		loadStats();
	});
</script>

<div class="settings-section">
	<div class="section-header">
		<ShieldAlert class="w-5 h-5 text-red-600" />
		<h3>Threat Catalog (MITRE ATT&CK® ICS)</h3>
	</div>

	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading catalog stats...</span>
		</div>
	{:else if stats}
		<div class="stats-grid">
			<div class="stat-card">
				<div class="stat-value">{stats.total}</div>
				<div class="stat-label">Total Threats</div>
			</div>
			<div class="stat-card mitre">
				<div class="stat-value">{stats.mitre_attack_ics}</div>
				<div class="stat-label">MITRE ATT&CK ICS</div>
			</div>
			<div class="stat-card custom">
				<div class="stat-value">{stats.custom}</div>
				<div class="stat-label">Custom</div>
			</div>
			<div class="stat-card modified">
				<div class="stat-value">{stats.user_modified}</div>
				<div class="stat-label">User Modified</div>
			</div>
		</div>

		<div class="actions">
			<button
				class="btn-seed"
				on:click={() => seedCatalog(false)}
				disabled={seeding}
			>
				{#if seeding}
					<RefreshCw class="w-4 h-4 spinning" />
					Seeding...
				{:else}
					<Download class="w-4 h-4" />
					Seed MITRE Threats
				{/if}
			</button>

			<button
				class="btn-force"
				on:click={() => seedCatalog(true)}
				disabled={seeding}
				title="Overwrites user-modified entries"
			>
				<RefreshCw class="w-4 h-4" />
				Force Re-seed
			</button>

			<button
				class="btn-refresh"
				on:click={loadStats}
				disabled={loading}
			>
				<RefreshCw class="w-4 h-4" />
			</button>
		</div>
	{/if}

	{#if seedResult}
		<div class="seed-result success">
			<CheckCircle class="w-4 h-4" />
			<span>
				Created: <strong>{seedResult.created}</strong>,
				Updated: <strong>{seedResult.updated}</strong>,
				Skipped: <strong>{seedResult.skipped}</strong>
			</span>
		</div>
	{/if}

	{#if error}
		<div class="seed-result error-msg">
			<AlertTriangle class="w-4 h-4" />
			<span>{error}</span>
		</div>
	{/if}

	<p class="attribution">
		Uses MITRE ATT&CK® for ICS (Apache 2.0). ATT&CK® is a registered trademark of The MITRE Corporation.
	</p>
</div>

<style>
	.settings-section {
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1.5rem;
	}
	.section-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	.section-header h3 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
	}
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1rem;
		margin-bottom: 1.5rem;
	}
	.stat-card {
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		padding: 1rem;
		text-align: center;
	}
	.stat-card.mitre { border-left: 3px solid #3b82f6; }
	.stat-card.custom { border-left: 3px solid #10b981; }
	.stat-card.modified { border-left: 3px solid #f59e0b; }
	.stat-value {
		font-size: 1.75rem;
		font-weight: 700;
		color: #1f2937;
	}
	.stat-label {
		font-size: 0.75rem;
		color: #6b7280;
		margin-top: 0.25rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.actions {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	.btn-seed {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.875rem;
		transition: background 0.2s;
	}
	.btn-seed:hover:not(:disabled) { background: #2563eb; }
	.btn-seed:disabled { background: #9ca3af; cursor: not-allowed; }
	.btn-force {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		background: white;
		color: #dc2626;
		border: 1px solid #dc2626;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.875rem;
		transition: all 0.2s;
	}
	.btn-force:hover:not(:disabled) { background: #fef2f2; }
	.btn-force:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-refresh {
		display: flex;
		align-items: center;
		padding: 0.625rem;
		background: white;
		color: #6b7280;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
	}
	.btn-refresh:hover { background: #f3f4f6; }
	.seed-result {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		border-radius: 6px;
		font-size: 0.875rem;
		margin-bottom: 1rem;
	}
	.seed-result.success {
		background: #f0fdf4;
		color: #166534;
		border: 1px solid #bbf7d0;
	}
	.seed-result.error-msg {
		background: #fef2f2;
		color: #991b1b;
		border: 1px solid #fecaca;
	}
	.loading-state {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		color: #6b7280;
	}
	.spinner {
		width: 1.25rem;
		height: 1.25rem;
		border: 2px solid #e5e7eb;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}
	.attribution {
		margin: 0;
		font-size: 0.7rem;
		color: #9ca3af;
		font-style: italic;
	}
	:global(.spinning) { animation: spin 1s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
