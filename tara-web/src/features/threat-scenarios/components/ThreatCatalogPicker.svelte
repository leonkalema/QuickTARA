<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { ShieldAlert, Search, X, ChevronDown, ChevronUp } from '@lucide/svelte';
	import { threatCatalogApi } from '$lib/api/threatCatalogApi';
	import type { ThreatCatalogItem } from '$lib/api/threatCatalogApi';

	export let isOpen = false;

	const dispatch = createEventDispatcher<{
		select: {
			name: string;
			description: string;
			attack_vector: string;
			mitre_technique_id: string;
			stride_category: string;
			automotive_context: string;
		};
		close: void;
	}>();

	let catalogItems: ThreatCatalogItem[] = [];
	let filteredItems: ThreatCatalogItem[] = [];
	let loading = false;
	let searchTerm = '';
	let expandedId: string | null = null;

	onMount(async () => {
		await loadCatalog();
	});

	async function loadCatalog(): Promise<void> {
		loading = true;
		try {
			const resp = await threatCatalogApi.getItems({ limit: 200 });
			catalogItems = resp.catalog_items;
			filteredItems = catalogItems;
		} catch (err) {
			console.error('Failed to load threat catalog:', err);
		} finally {
			loading = false;
		}
	}

	function filterItems(): void {
		const term = searchTerm.toLowerCase();
		if (!term) {
			filteredItems = catalogItems;
			return;
		}
		filteredItems = catalogItems.filter(item =>
			item.title.toLowerCase().includes(term) ||
			item.description.toLowerCase().includes(term) ||
			(item.mitre_technique_id?.toLowerCase().includes(term)) ||
			(item.automotive_context?.toLowerCase().includes(term)) ||
			item.stride_category.toLowerCase().includes(term) ||
			item.attack_vectors.some(v => v.toLowerCase().includes(term))
		);
	}

	function selectItem(item: ThreatCatalogItem): void {
		const attackVector = item.attack_vectors.join(', ');
		dispatch('select', {
			name: item.mitre_technique_id
				? `[${item.mitre_technique_id}] ${item.title}`
				: item.title,
			description: item.automotive_context || item.description,
			attack_vector: attackVector,
			mitre_technique_id: item.mitre_technique_id || '',
			stride_category: item.stride_category,
			automotive_context: item.automotive_context || ''
		});
		isOpen = false;
	}

	function toggleExpand(id: string): void {
		expandedId = expandedId === id ? null : id;
	}

	function close(): void {
		isOpen = false;
		dispatch('close');
	}

	function getSourceBadge(source: string): string {
		return source === 'mitre_attack_ics' ? 'MITRE' : 'Custom';
	}

	function getSourceClass(source: string): string {
		return source === 'mitre_attack_ics' ? 'badge-mitre' : 'badge-custom';
	}

	function getSeverityLabel(severity: number): string {
		const labels: Record<number, string> = { 1: 'Very Low', 2: 'Low', 3: 'Medium', 4: 'High', 5: 'Critical' };
		return labels[severity] || 'Unknown';
	}

	function getRelevanceStars(relevance: number): string {
		return '★'.repeat(relevance) + '☆'.repeat(5 - relevance);
	}

	$: if (searchTerm !== undefined) filterItems();
</script>

{#if isOpen}
<div class="overlay" on:click|self={close} on:keydown={(e) => e.key === 'Escape' && close()} role="dialog" tabindex="-1">
	<div class="picker-panel">
		<div class="picker-header">
			<div class="header-title">
				<ShieldAlert class="w-5 h-5 text-blue-600" />
				<h3>Select from Threat Catalog</h3>
			</div>
			<button class="close-btn" on:click={close}><X class="w-5 h-5" /></button>
		</div>

		<div class="search-bar">
			<Search class="w-4 h-4 search-icon" />
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Search by name, technique ID, attack vector, STRIDE..."
				class="search-input"
			/>
			{#if searchTerm}
				<button class="clear-btn" on:click={() => { searchTerm = ''; }}>
					<X class="w-4 h-4" />
				</button>
			{/if}
		</div>

		<div class="results-count">
			{filteredItems.length} of {catalogItems.length} threats
		</div>

		<div class="catalog-list">
			{#if loading}
				<div class="loading">Loading catalog...</div>
			{:else if filteredItems.length === 0}
				<div class="empty">No threats match your search.</div>
			{:else}
				{#each filteredItems as item (item.id)}
					<div class="catalog-item">
						<button class="item-header" on:click={() => toggleExpand(item.id)}>
							<div class="item-main">
								<div class="item-title-row">
									<span class="badge {getSourceClass(item.source)}">{getSourceBadge(item.source)}</span>
									{#if item.mitre_technique_id}
										<span class="technique-id">{item.mitre_technique_id}</span>
									{/if}
									<span class="item-title">{item.title}</span>
								</div>
								<div class="item-meta">
									<span class="stride">{item.stride_category.replace('_', ' ')}</span>
									<span class="separator">·</span>
									<span class="severity">Sev: {getSeverityLabel(item.typical_severity)}</span>
									<span class="separator">·</span>
									<span class="relevance" title="Automotive relevance">{getRelevanceStars(item.automotive_relevance)}</span>
								</div>
							</div>
							<div class="expand-icon">
								{#if expandedId === item.id}
									<ChevronUp class="w-4 h-4" />
								{:else}
									<ChevronDown class="w-4 h-4" />
								{/if}
							</div>
						</button>

						{#if expandedId === item.id}
							<div class="item-details">
								{#if item.automotive_context}
									<p class="detail-text"><strong>Automotive Context:</strong> {item.automotive_context}</p>
								{/if}
								<p class="detail-text"><strong>Description:</strong> {item.description}</p>
								<div class="detail-tags">
									<strong>Attack Vectors:</strong>
									{#each item.attack_vectors as vec}
										<span class="tag">{vec}</span>
									{/each}
								</div>
								{#if item.examples.length > 0}
									<div class="detail-examples">
										<strong>Examples:</strong>
										<ul>
											{#each item.examples as ex}
												<li>{ex}</li>
											{/each}
										</ul>
									</div>
								{/if}
								<button class="btn-select" on:click={() => selectItem(item)}>
									Use This Threat
								</button>
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>
	</div>
</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.5);
		z-index: 100;
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 3rem;
	}
	.picker-panel {
		background: white;
		border-radius: 12px;
		width: 90%;
		max-width: 720px;
		max-height: 80vh;
		display: flex;
		flex-direction: column;
		box-shadow: 0 25px 50px rgba(0,0,0,0.25);
	}
	.picker-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}
	.header-title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.header-title h3 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #1f2937;
	}
	.close-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #6b7280;
		padding: 0.25rem;
		border-radius: 4px;
	}
	.close-btn:hover { background: #f3f4f6; }
	.search-bar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		position: relative;
	}
	.search-icon { color: #9ca3af; flex-shrink: 0; }
	.search-input {
		flex: 1;
		border: none;
		outline: none;
		font-size: 0.875rem;
		color: #1f2937;
	}
	.clear-btn {
		background: none;
		border: none;
		cursor: pointer;
		color: #9ca3af;
		padding: 0.25rem;
	}
	.results-count {
		padding: 0.5rem 1.5rem;
		font-size: 0.75rem;
		color: #6b7280;
		border-bottom: 1px solid #f3f4f6;
	}
	.catalog-list {
		overflow-y: auto;
		flex: 1;
	}
	.loading, .empty {
		padding: 2rem;
		text-align: center;
		color: #6b7280;
	}
	.catalog-item {
		border-bottom: 1px solid #f3f4f6;
	}
	.item-header {
		width: 100%;
		background: none;
		border: none;
		padding: 0.875rem 1.5rem;
		cursor: pointer;
		display: flex;
		justify-content: space-between;
		align-items: center;
		text-align: left;
		transition: background 0.15s;
	}
	.item-header:hover { background: #f9fafb; }
	.item-main { flex: 1; }
	.item-title-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.badge {
		font-size: 0.625rem;
		font-weight: 600;
		padding: 0.125rem 0.375rem;
		border-radius: 3px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.badge-mitre { background: #dbeafe; color: #1e40af; }
	.badge-custom { background: #d1fae5; color: #065f46; }
	.technique-id {
		font-family: monospace;
		font-size: 0.8rem;
		color: #3b82f6;
		font-weight: 600;
	}
	.item-title {
		font-size: 0.875rem;
		font-weight: 500;
		color: #1f2937;
	}
	.item-meta {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.25rem;
		font-size: 0.75rem;
		color: #6b7280;
	}
	.stride { text-transform: capitalize; }
	.separator { color: #d1d5db; }
	.relevance { color: #f59e0b; letter-spacing: 1px; }
	.expand-icon { color: #9ca3af; flex-shrink: 0; }
	.item-details {
		padding: 0 1.5rem 1rem;
		border-top: 1px solid #f3f4f6;
		background: #fafbfc;
	}
	.detail-text {
		font-size: 0.8125rem;
		color: #374151;
		margin: 0.75rem 0 0;
		line-height: 1.5;
	}
	.detail-tags {
		margin-top: 0.75rem;
		font-size: 0.8125rem;
		color: #374151;
		display: flex;
		align-items: center;
		gap: 0.375rem;
		flex-wrap: wrap;
	}
	.tag {
		background: #f3f4f6;
		padding: 0.125rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		color: #4b5563;
	}
	.detail-examples {
		margin-top: 0.75rem;
		font-size: 0.8125rem;
		color: #374151;
	}
	.detail-examples ul {
		margin: 0.25rem 0 0;
		padding-left: 1.25rem;
	}
	.detail-examples li {
		margin-bottom: 0.25rem;
		font-size: 0.8rem;
		color: #4b5563;
	}
	.btn-select {
		margin-top: 1rem;
		padding: 0.5rem 1.25rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.8125rem;
		transition: background 0.2s;
	}
	.btn-select:hover { background: #2563eb; }
</style>
