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
		<ShieldAlert class="w-4 h-4" style="color: var(--color-error);" />
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
				<div class="stat-indicator total"></div>
				<div class="stat-content">
					<div class="stat-label">Total Threats</div>
					<div class="stat-value">{stats.total}</div>
				</div>
			</div>
			<div class="stat-card">
				<div class="stat-indicator mitre"></div>
				<div class="stat-content">
					<div class="stat-label">MITRE ATT&CK ICS</div>
					<div class="stat-value">{stats.mitre_attack_ics}</div>
				</div>
			</div>
			<div class="stat-card">
				<div class="stat-indicator custom"></div>
				<div class="stat-content">
					<div class="stat-label">Custom</div>
					<div class="stat-value">{stats.custom}</div>
				</div>
			</div>
			<div class="stat-card">
				<div class="stat-indicator modified"></div>
				<div class="stat-content">
					<div class="stat-label">User Modified</div>
					<div class="stat-value">{stats.user_modified}</div>
				</div>
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
		background: var(--color-bg-surface);
		border: 1px solid var(--color-border-default);
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
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}
	.stat-card {
		background: var(--color-bg-inset);
		border: 1px solid var(--color-border-subtle);
		border-radius: 6px;
		padding: 0.75rem;
		display: flex;
		align-items: center;
		gap: 0.625rem;
	}
	.stat-indicator {
		width: 3px;
		height: 28px;
		border-radius: 2px;
		flex-shrink: 0;
	}
	.stat-indicator.total { background: var(--color-text-secondary); }
	.stat-indicator.mitre { background: var(--color-accent-primary); }
	.stat-indicator.custom { background: var(--color-status-accepted-text, #10b981); }
	.stat-indicator.modified { background: var(--color-status-draft-text, #f59e0b); }
	.stat-content {
		display: flex;
		flex-direction: column;
	}
	.stat-value {
		font-size: 1rem;
		font-weight: 700;
		color: var(--color-text-primary);
		line-height: 1.2;
	}
	.stat-label {
		font-size: 0.5625rem;
		color: var(--color-text-tertiary);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		line-height: 1.2;
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
		padding: 0.5rem 1rem;
		background: var(--color-accent-primary);
		color: var(--color-text-inverse);
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.75rem;
		transition: all 0.2s;
	}
	.btn-seed:hover:not(:disabled) { filter: brightness(1.1); }
	.btn-seed:disabled { opacity: 0.4; cursor: not-allowed; }
	.btn-force {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: transparent;
		color: var(--color-error);
		border: 1px solid var(--color-error);
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.75rem;
		transition: all 0.2s;
	}
	.btn-force:hover:not(:disabled) { background: color-mix(in srgb, var(--color-error) 10%, transparent); }
	.btn-force:disabled { opacity: 0.4; cursor: not-allowed; }
	.btn-refresh {
		display: flex;
		align-items: center;
		padding: 0.5rem;
		background: var(--color-bg-elevated);
		color: var(--color-text-tertiary);
		border: 1px solid var(--color-border-default);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
	}
	.btn-refresh:hover { filter: brightness(1.1); }
	.seed-result {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1rem;
		border-radius: 6px;
		font-size: 0.75rem;
		margin-bottom: 1rem;
	}
	.seed-result.success {
		background: color-mix(in srgb, var(--color-status-accepted-text, #10b981) 10%, transparent);
		color: var(--color-status-accepted-text, #10b981);
		border: 1px solid color-mix(in srgb, var(--color-status-accepted-text, #10b981) 30%, transparent);
	}
	.seed-result.error-msg {
		background: color-mix(in srgb, var(--color-error) 10%, transparent);
		color: var(--color-error);
		border: 1px solid color-mix(in srgb, var(--color-error) 30%, transparent);
	}
	.loading-state {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		color: var(--color-text-tertiary);
		font-size: 0.75rem;
	}
	.spinner {
		width: 1.25rem;
		height: 1.25rem;
		border: 2px solid var(--color-border-default);
		border-top-color: var(--color-accent-primary);
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}
	.attribution {
		margin: 0;
		font-size: 0.625rem;
		color: var(--color-text-tertiary);
		font-style: italic;
	}
	:global(.spinning) { animation: spin 1s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
</style>
