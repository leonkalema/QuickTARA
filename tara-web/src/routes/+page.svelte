<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { API_BASE_URL } from '$lib/config';
	
	let productScopes = [];
	let totalProducts = 0;
	let totalAssets = 0;
	let totalDamageScenarios = 0;
	let totalThreatScenarios = 0;
	let totalRiskAssessments = 0; // projects currently in Risk Assessment stage
	let totalTreatments = 0;
	let tarasByStage = {
		scoping: [],
		assets: [],
		damageScenarios: [],
		threatScenarios: [],
		riskAssessment: [],
		treatment: []
	};
	
	const taraStages = [
		{ id: 'scoping', name: 'Scoping', icon: '🎯', route: '/products' },
		{ id: 'assets', name: 'Assets', icon: '🔧', route: '/assets-components' },
		{ id: 'damageScenarios', name: 'Damage Scenarios', icon: '⚠️', route: '/damage-scenarios' },
		{ id: 'threatScenarios', name: 'Threat Scenarios', icon: '🎭', route: '/threat-scenarios' },
		{ id: 'riskAssessment', name: 'Risk Assessment', icon: '📊', route: '/risk-assessment' },
		{ id: 'treatment', name: 'Treatment', icon: '🛡️', route: '/risk-treatment' }
	];
	
	onMount(async () => {
		await loadDashboardData();
	});
	
	async function loadDashboardData() {
		try {
			const response = await fetch(`${API_BASE_URL}/products?skip=0&limit=100`);
			if (response.ok) {
				const data = await response.json();
				// The API returns { scopes: Product[], total: number }
				if (data.scopes && Array.isArray(data.scopes)) {
					productScopes = data.scopes;
				} else {
					productScopes = [];
				}
				totalProducts = data.total ?? productScopes.length;
				categorizeProjectsByStage();
			}
		} catch (error) {
			console.error('Error loading dashboard data:', error);
		}
	}
	
	async function categorizeProjectsByStage() {
		// Reset categories
		Object.keys(tarasByStage).forEach(stage => {
			tarasByStage[stage] = [];
		});

		// Reset totals
		totalAssets = 0;
		totalDamageScenarios = 0;
		totalThreatScenarios = 0;
		totalRiskAssessments = 0;
		totalTreatments = 0;
		
		for (const scope of productScopes) {
			const result = await determineProjectStage(scope);
			tarasByStage[result.stage].push(scope);
			totalAssets += result.assetsCount;
			totalDamageScenarios += result.damageCount;
			totalThreatScenarios += result.threatCount;
			totalTreatments += result.treatmentCount;
		}

		// projects in risk assessment stage (by our pipeline rule)
		totalRiskAssessments = tarasByStage.riskAssessment.length;
		
		// Trigger reactivity
		tarasByStage = { ...tarasByStage };
	}
	
	async function determineProjectStage(scope) {
		try {
			// Check what data exists for this scope to determine current stage
			const [assetsRes, damageRes, threatRes, riskRes] = await Promise.all([
				fetch(`${API_BASE_URL}/assets?scope_id=${scope.scope_id}`),
				fetch(`${API_BASE_URL}/damage-scenarios?scope_id=${scope.scope_id}`),
				fetch(`${API_BASE_URL}/threat-scenarios?scope_id=${scope.scope_id}`),
				fetch(`${API_BASE_URL}/risk-treatment?scope_id=${scope.scope_id}`)
			]);
			
			const [assetsData, damageData, threatData, riskData] = await Promise.all([
				assetsRes.ok ? assetsRes.json() : { assets: [] },
				damageRes.ok ? damageRes.json() : { scenarios: [], total: 0 },
				threatRes.ok ? threatRes.json() : { threat_scenarios: [], total: 0 },
				riskRes.ok ? riskRes.json() : { damage_scenarios: [], total_count: 0 }
			]);
			
			// Extract arrays and totals from response structures
			const assets = assetsData.assets || [];
			const damageList = damageData.scenarios || [];
			const damageTotal = (typeof damageData.total === 'number') ? damageData.total : damageList.length;
			const threatList = threatData.threat_scenarios || [];
			const threatTotal = (typeof threatData.total === 'number') ? threatData.total : threatList.length;
			const treatmentList = riskData.damage_scenarios || [];
			const treatmentTotal = (typeof riskData.total_count === 'number') ? riskData.total_count : treatmentList.length;
			
			// Determine stage based on data completeness
			let stage = 'scoping';
			if (treatmentTotal > 0) stage = 'treatment';
			else if (threatTotal > 0) stage = 'riskAssessment';
			else if (damageTotal > 0) stage = 'threatScenarios';
			else if (assets.length > 0) stage = 'assets';
			return { 
				stage, 
				assetsCount: assets.length,
				damageCount: damageTotal,
				threatCount: threatTotal,
				treatmentCount: treatmentTotal
			};
		} catch (error) {
			console.error('Error determining project stage:', error);
			return { stage: 'scoping', assetsCount: 0, damageCount: 0, threatCount: 0, treatmentCount: 0 };
		}
	}
	
	function navigateToStage(stage, scopeId = null) {
		const stageConfig = taraStages.find(s => s.id === stage);
		if (stageConfig) {
			const url = scopeId ? `${stageConfig.route}?scope_id=${scopeId}` : stageConfig.route;
			goto(url);
		}
	}
	
	function generateReport(scopeId) {
		window.open(`/api/reports/tara-pdf/${scopeId}`, '_blank');
	}
</script>

<div class="min-h-screen bg-gray-50 p-6">
	<div class="max-w-7xl mx-auto">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-2">TARA Dashboard</h1>
			<p class="text-gray-600">ISO/SAE 21434 Threat Analysis and Risk Assessment</p>
		</div>
		
		<!-- TARA Pipeline -->
		<div class="bg-white rounded-lg shadow-md p-6 mb-8">
			<div class="flex justify-between items-center mb-6">
				<h2 class="text-xl font-semibold text-gray-900">TARA Workflow Pipeline</h2>
				
			</div>
			
			<div class="grid grid-cols-1 lg:grid-cols-6 gap-4">
				{#each taraStages as stage, index}
					<div class="relative">
						<!-- Stage Card -->
						<div class="bg-gray-50 rounded-lg p-4 border-2 border-gray-200 hover:border-blue-300 transition-colors">
							<div class="text-center">
								<div class="text-2xl mb-2">{stage.icon}</div>
								<h3 class="font-semibold text-sm text-gray-900 mb-2">{stage.name}</h3>
								
								<!-- Metrics per stage -->
								<div class="text-center">
									{#if stage.id === 'scoping'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalProducts}</div>
										<div class="text-xs text-gray-500">total products</div>
									{:else if stage.id === 'assets'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalAssets}</div>
										<div class="text-xs text-gray-500">total assets</div>
									{:else if stage.id === 'damageScenarios'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalDamageScenarios}</div>
										<div class="text-xs text-gray-500">total damage scenarios</div>
									{:else if stage.id === 'threatScenarios'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalThreatScenarios}</div>
										<div class="text-xs text-gray-500">total threats</div>
									{:else if stage.id === 'riskAssessment'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalRiskAssessments}</div>
										<div class="text-xs text-gray-500">projects in risk assessment</div>
									{:else if stage.id === 'treatment'}
										<div class="text-2xl font-bold text-blue-600 mb-1">{totalTreatments}</div>
										<div class="text-xs text-gray-500">total treatments</div>
									{:else}
										{#if tarasByStage[stage.id].length > 0}
											<div class="text-2xl font-bold text-blue-600 mb-1">
												{tarasByStage[stage.id].length}
											</div>
											<div class="text-xs text-gray-500">
												{tarasByStage[stage.id].length === 1 ? 'project' : 'projects'}
											</div>
										{:else}
											<div class="text-lg text-gray-300">—</div>
										{/if}
									{/if}
								</div>
							</div>
						</div>
						
						<!-- Arrow -->
						{#if index < taraStages.length - 1}
							<div class="hidden lg:block absolute top-1/2 -right-2 transform -translate-y-1/2 text-gray-400 text-xl">
								→
							</div>
						{/if}
					</div>
				{/each}
			</div>
			
			<!-- Pipeline Actions -->
			<div class="mt-6 flex justify-center">
				<button 
					on:click={() => navigateToStage('scoping')}
					class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
				>
					Start New TARA
				</button>
			</div>
		</div>
		
		<!-- Recent Projects -->
		<div class="bg-white rounded-lg shadow-md p-6">
			<h2 class="text-xl font-semibold mb-4 text-gray-900">Recent Projects</h2>
			
			{#if productScopes.length === 0}
				<div class="text-center py-8 text-gray-500">
					<div class="text-4xl mb-4">📋</div>
					<p>No TARA projects yet. Start your first assessment above.</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each productScopes.slice(0, 5) as scope}
						<div class="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
							<div class="flex justify-between items-start">
								<div class="flex-1">
									<h3 class="font-semibold text-gray-900">{scope.name}</h3>
									<p class="text-sm text-gray-600 mt-1">
										{scope.product_type} • {scope.safety_level}
									</p>
									<p class="text-xs text-gray-500 mt-2">
										Created: {new Date(scope.created_at).toLocaleDateString()}
									</p>
								</div>
								
								<div class="flex space-x-2 ml-4">
									<button 
										on:click={() => navigateToStage('damageScenarios', scope.scope_id)}
										class="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200 transition-colors"
									>
										Resume
									</button>
									<button 
										on:click={() => generateReport(scope.scope_id)}
										class="px-3 py-1 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200 transition-colors"
									>
										Report
									</button>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
