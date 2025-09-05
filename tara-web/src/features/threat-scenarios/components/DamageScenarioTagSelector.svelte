<script lang="ts">
	import { onMount } from 'svelte';
	import { selectedProduct } from '$lib/stores/productStore';
	import { damageScenarioApi } from '$lib/api/damageScenarioApi';
	import type { DamageScenario } from '$lib/types/damageScenario';

	export let selectedDamageScenarios: string[] = [];
	export let placeholder = 'Select damage scenarios...';

	let damageScenarios: DamageScenario[] = [];
	let loading = false;
	let error = '';
	let searchTerm = '';
	let showDropdown = false;

	$: filteredScenarios = damageScenarios.filter(scenario =>
		scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
		(scenario.description && scenario.description.toLowerCase().includes(searchTerm.toLowerCase()))
	);

	onMount(async () => {
		await loadDamageScenarios();
	});

	async function loadDamageScenarios() {
		if (!$selectedProduct) return;

		loading = true;
		error = '';

		try {
			const data = await damageScenarioApi.getDamageScenariosByProduct($selectedProduct.scope_id);
			damageScenarios = data.scenarios || [];
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load damage scenarios';
			console.error('Error loading damage scenarios:', err);
		} finally {
			loading = false;
		}
	}

	function toggleScenario(scenarioId: string) {
		if (selectedDamageScenarios.includes(scenarioId)) {
			selectedDamageScenarios = selectedDamageScenarios.filter(id => id !== scenarioId);
		} else {
			selectedDamageScenarios = [...selectedDamageScenarios, scenarioId];
		}
	}

	function removeScenario(scenarioId: string) {
		selectedDamageScenarios = selectedDamageScenarios.filter(id => id !== scenarioId);
	}

	function getScenarioById(id: string) {
		return damageScenarios.find(scenario => scenario.scenario_id === id);
	}

	function handleInputFocus() {
		showDropdown = true;
	}

	function handleInputBlur() {
		// Delay hiding dropdown to allow clicks on options
		setTimeout(() => {
			showDropdown = false;
		}, 200);
	}
</script>

<div class="damage-scenario-selector">
	<label class="block text-sm font-medium text-gray-700 mb-2">
		Damage Scenarios
	</label>

	<!-- Selected scenarios as tags -->
	{#if selectedDamageScenarios.length > 0}
		<div class="selected-tags mb-2">
			{#each selectedDamageScenarios as scenarioId}
				{@const scenario = getScenarioById(scenarioId)}
				{#if scenario}
					<span class="tag">
						{scenario.name}
						<button
							type="button"
							class="tag-remove"
							on:click={() => removeScenario(scenarioId)}
						>
							×
						</button>
					</span>
				{/if}
			{/each}
		</div>
	{/if}

	<!-- Search input -->
	<div class="search-container">
		<input
			type="text"
			bind:value={searchTerm}
			on:focus={handleInputFocus}
			on:blur={handleInputBlur}
			{placeholder}
			class="search-input"
		/>
		
		{#if showDropdown && !loading}
			<div class="dropdown">
				{#if filteredScenarios.length === 0}
					<div class="dropdown-item disabled">
						{searchTerm ? 'No scenarios match your search' : 'No damage scenarios available'}
					</div>
				{:else}
					{#each filteredScenarios as scenario}
						<button
							type="button"
							class="dropdown-item"
							class:selected={selectedDamageScenarios.includes(scenario.scenario_id)}
							on:click={() => toggleScenario(scenario.scenario_id)}
						>
							<div class="scenario-info">
								<div class="scenario-name">{scenario.name}</div>
								<div class="scenario-description">{scenario.description}</div>
							</div>
							{#if selectedDamageScenarios.includes(scenario.scenario_id)}
								<span class="checkmark">✓</span>
							{/if}
						</button>
					{/each}
				{/if}
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="loading">Loading damage scenarios...</div>
	{/if}

	{#if error}
		<div class="error">{error}</div>
	{/if}
</div>

<style>
	.damage-scenario-selector {
		position: relative;
	}

	.selected-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.tag {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		background: #3b82f6;
		color: white;
		padding: 4px 8px;
		border-radius: 16px;
		font-size: 14px;
	}

	.tag-remove {
		background: none;
		border: none;
		color: white;
		cursor: pointer;
		font-size: 16px;
		line-height: 1;
		padding: 0;
		margin-left: 4px;
	}

	.tag-remove:hover {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
		width: 16px;
		height: 16px;
	}

	.search-container {
		position: relative;
	}

	.search-input {
		width: 100%;
		padding: 8px 12px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 14px;
	}

	.search-input:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background: white;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		max-height: 200px;
		overflow-y: auto;
		z-index: 10;
	}

	.dropdown-item {
		width: 100%;
		padding: 12px;
		border: none;
		background: none;
		text-align: left;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.dropdown-item:hover:not(.disabled) {
		background: #f3f4f6;
	}

	.dropdown-item.selected {
		background: #eff6ff;
	}

	.dropdown-item.disabled {
		color: #9ca3af;
		cursor: not-allowed;
	}

	.scenario-info {
		flex: 1;
	}

	.scenario-name {
		font-weight: 500;
		margin-bottom: 2px;
	}

	.scenario-description {
		font-size: 12px;
		color: #6b7280;
		line-height: 1.3;
	}

	.checkmark {
		color: #3b82f6;
		font-weight: bold;
	}

	.loading {
		padding: 8px 0;
		color: #6b7280;
		font-size: 14px;
	}

	.error {
		padding: 8px 0;
		color: #dc2626;
		font-size: 14px;
	}
</style>
