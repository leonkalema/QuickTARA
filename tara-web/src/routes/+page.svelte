<script lang="ts">
	import { onMount } from 'svelte';
	import { API_BASE_URL } from '$lib/config';
	import { authStore } from '$lib/stores/auth';
	import { isToolAdmin, canPerformTARA } from '$lib/utils/permissions';
	import { get } from 'svelte/store';
	import AnalystDashboard from '../features/dashboard/components/AnalystDashboard.svelte';
	import AdminDashboard from '../features/dashboard/components/AdminDashboard.svelte';
	import ViewerDashboard from '../features/dashboard/components/ViewerDashboard.svelte';

	type DashboardType = 'admin' | 'analyst' | 'viewer';

	let dashboardType: DashboardType = 'viewer';
	let loading = true;
	let productScopes: any[] = [];
	let totalProducts = 0;
	let totalAssets = 0;
	let totalDamageScenarios = 0;
	let totalThreatScenarios = 0;
	let totalRiskAssessments = 0;
	let totalTreatments = 0;
	let totalUsers = 0;
	let totalOrganizations = 0;

	function determineDashboardType(): DashboardType {
		if (isToolAdmin()) return 'admin';
		if (canPerformTARA()) return 'analyst';
		return 'viewer';
	}

	function getAuthHeaders(): HeadersInit {
		const auth = get(authStore);
		const headers: HeadersInit = { 'Content-Type': 'application/json' };
		const token = auth.token ?? (typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null);
		if (token) headers['Authorization'] = `Bearer ${token}`;
		return headers;
	}

	onMount(async () => {
		dashboardType = determineDashboardType();
		if (dashboardType === 'admin') await loadAdminData();
		else if (dashboardType === 'analyst') await loadAnalystData();
		else await loadViewerData();
		loading = false;
	});

	async function loadAnalystData(): Promise<void> {
		try {
			const res = await fetch(`${API_BASE_URL}/products?skip=0&limit=100`, { headers: getAuthHeaders() });
			if (!res.ok) return;
			const data = await res.json();
			productScopes = data.scopes ?? [];
			totalProducts = data.total ?? productScopes.length;
			await aggregateTotals();
		} catch (e) { console.error('Dashboard load error:', e); }
	}

	async function aggregateTotals(): Promise<void> {
		totalAssets = 0; totalDamageScenarios = 0; totalThreatScenarios = 0; totalTreatments = 0;
		for (const scope of productScopes) {
			try {
				const [aRes, dRes, tRes, rRes] = await Promise.all([
					fetch(`${API_BASE_URL}/assets?scope_id=${scope.scope_id}`),
					fetch(`${API_BASE_URL}/damage-scenarios?scope_id=${scope.scope_id}`),
					fetch(`${API_BASE_URL}/threat-scenarios?scope_id=${scope.scope_id}`),
					fetch(`${API_BASE_URL}/risk-treatment?scope_id=${scope.scope_id}`)
				]);
				const [a, d, t, r] = await Promise.all([
					aRes.ok ? aRes.json() : { assets: [] },
					dRes.ok ? dRes.json() : { scenarios: [], total: 0 },
					tRes.ok ? tRes.json() : { threat_scenarios: [], total: 0 },
					rRes.ok ? rRes.json() : { total_count: 0 }
				]);
				totalAssets += (a.assets?.length ?? 0);
				totalDamageScenarios += (typeof d.total === 'number' ? d.total : d.scenarios?.length ?? 0);
				totalThreatScenarios += (typeof t.total === 'number' ? t.total : t.threat_scenarios?.length ?? 0);
				totalTreatments += (typeof r.total_count === 'number' ? r.total_count : 0);
			} catch { /* skip failed scope */ }
		}
		totalRiskAssessments = totalThreatScenarios > 0 ? productScopes.length : 0;
	}

	async function loadAdminData(): Promise<void> {
		const headers = getAuthHeaders();
		try {
			const [uRes, oRes] = await Promise.all([
				fetch(`${API_BASE_URL}/users`, { headers }),
				fetch(`${API_BASE_URL}/organizations`, { headers })
			]);
			if (uRes.ok) { const d = await uRes.json(); totalUsers = d.total ?? d.length ?? 0; }
			if (oRes.ok) { const d = await oRes.json(); totalOrganizations = d.organizations?.length ?? (Array.isArray(d) ? d.length : 0); }
		} catch (e) { console.error('Admin dashboard error:', e); }
	}

	async function loadViewerData(): Promise<void> {
		try {
			const res = await fetch(`${API_BASE_URL}/products?skip=0&limit=100`, { headers: getAuthHeaders() });
			if (!res.ok) return;
			const data = await res.json();
			productScopes = data.scopes ?? [];
			totalProducts = data.total ?? productScopes.length;
		} catch (e) { console.error('Viewer dashboard error:', e); }
	}

	const TITLES: Record<DashboardType, { heading: string; sub: string }> = {
		admin:   { heading: 'System Administration', sub: 'Manage users, organizations, and system settings' },
		analyst: { heading: 'Risk Command Center',   sub: 'ISO/SAE 21434 Threat Analysis & Risk Assessment' },
		viewer:  { heading: 'TARA Overview',          sub: 'View threat analysis and risk assessment reports' },
	};
</script>

<svelte:head>
	<title>{TITLES[dashboardType].heading} - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page header -->
	<div>
		<h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">
			{TITLES[dashboardType].heading}
		</h1>
		<p class="text-sm mt-1" style="color: var(--color-text-secondary);">
			{TITLES[dashboardType].sub}
		</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
		</div>
	{:else if dashboardType === 'admin'}
		<AdminDashboard {totalUsers} {totalOrganizations} />
	{:else if dashboardType === 'viewer'}
		<ViewerDashboard {productScopes} {totalProducts} />
	{:else}
		<AnalystDashboard
			{productScopes} {totalProducts} {totalAssets}
			{totalDamageScenarios} {totalThreatScenarios}
			{totalRiskAssessments} {totalTreatments}
		/>
	{/if}
</div>
