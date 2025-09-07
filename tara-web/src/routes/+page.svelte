<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	
	let productScopes = [];
	let tarasByStage = {
		scoping: [],
		assets: [],
		damageScenarios: [],
		threatScenarios: [],
		riskAssessment: [],
		treatment: []
	};
	
	const taraStages = [
		{ id: 'scoping', name: 'Scoping', icon: '🎯', route: '/product-scopes' },
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
			const response = await fetch('http://127.0.0.1:8080/api/products?skip=0&limit=100');
			if (response.ok) {
				const data = await response.json();
				// The API returns { scopes: Product[], total: number }
				if (data.scopes && Array.isArray(data.scopes)) {
					productScopes = data.scopes;
				} else {
					productScopes = [];
				}
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
		
		for (const scope of productScopes) {
			const stage = await determineProjectStage(scope);
			tarasByStage[stage].push(scope);
		}
		
		// Trigger reactivity
		tarasByStage = { ...tarasByStage };
	}
	
	async function determineProjectStage(scope) {
		try {
			// Check what data exists for this scope to determine current stage
			const [assetsRes, damageRes, threatRes, riskRes] = await Promise.all([
				fetch(`http://127.0.0.1:8080/api/assets?scope_id=${scope.scope_id}`),
				fetch(`http://127.0.0.1:8080/api/damage-scenarios?scope_id=${scope.scope_id}`),
				fetch(`http://127.0.0.1:8080/api/threat-scenarios?scope_id=${scope.scope_id}`),
				fetch(`http://127.0.0.1:8080/api/risk-treatment?scope_id=${scope.scope_id}`)
			]);
			
			const [assetsData, damageScenarios, threatScenarios, riskTreatments] = await Promise.all([
				assetsRes.ok ? assetsRes.json() : { assets: [] },
				damageRes.ok ? damageRes.json() : [],
				threatRes.ok ? threatRes.json() : [],
				riskRes.ok ? riskRes.json() : []
			]);
			
			// Extract assets array from the response structure
			const assets = assetsData.assets || [];
			
			// Determine stage based on data completeness
			if (riskTreatments.length > 0) return 'treatment';
			if (threatScenarios.length > 0) return 'riskAssessment';
			if (damageScenarios.length > 0) return 'threatScenarios';
			if (assets.length > 0) return 'assets';
			return 'scoping';
		} catch (error) {
			console.error('Error determining project stage:', error);
			return 'scoping';
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
				<div class="text-sm text-gray-600">
					Total Projects: <span class="font-semibold text-gray-900">{productScopes.length}</span>
				</div>
			</div>
			
			<div class="grid grid-cols-1 lg:grid-cols-6 gap-4">
				{#each taraStages as stage, index}
					<div class="relative">
						<!-- Stage Card -->
						<div class="bg-gray-50 rounded-lg p-4 border-2 border-gray-200 hover:border-blue-300 transition-colors">
							<div class="text-center">
								<div class="text-2xl mb-2">{stage.icon}</div>
								<h3 class="font-semibold text-sm text-gray-900 mb-2">{stage.name}</h3>
								
								<!-- Project Count Display -->
								<div class="text-center">
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
