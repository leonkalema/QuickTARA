<script lang="ts">
	import { page } from '$app/stores';
	import { Users, Building2, Database, Settings } from '@lucide/svelte';
	import { authStore } from '$lib/stores/auth';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

	let { children } = $props();

	let isToolAdmin = $state(false);
	let isOrgAdmin = $state(false);
	let hasCheckedAuth = $state(false);

	// Reactive permission checks - wait for auth to be initialized
	$effect(() => {
		const state = $authStore;
		
		// Wait for auth to be initialized
		if (!state.isInitialized) return;
		
		if (!state.isAuthenticated || !state.token) {
			window.location.href = '/auth';
			return;
		}

		let isSuperuser = !!state?.user?.is_superuser;
		if (!isSuperuser && state?.token) {
			try {
				const payload = JSON.parse(atob(state.token.split('.')[1]));
				isSuperuser = !!payload.is_superuser;
			} catch {}
		}

		const isAdminEmail = state?.user?.email === 'admin@quicktara.local';
		
		// Check roles from user organizations
		const userOrgs = state?.user?.organizations || [];
		const hasToolAdminRole = userOrgs.some((org: any) => org.role?.toLowerCase() === 'tool_admin');
		const hasOrgAdminRole = userOrgs.some((org: any) => org.role?.toLowerCase() === 'org_admin');
		
		isToolAdmin = isSuperuser || hasToolAdminRole || isAdminEmail;
		isOrgAdmin = hasOrgAdminRole;
		
		const allowed = isToolAdmin || isOrgAdmin;
		if (!allowed && !hasCheckedAuth) {
			hasCheckedAuth = true;
			window.location.href = '/unauthorized';
		}
	});

	const allSteps = [
		{
			id: 'users',
			title: 'User Management',
			icon: Users,
			path: '/settings/users',
			description: 'Manage users and roles',
			requiresToolAdmin: false
		},
		{
			id: 'organizations',
			title: 'Departments',
			icon: Building2,
			path: '/settings/organizations',
			description: 'Manage departments and teams',
			requiresToolAdmin: false
		},
		{
			id: 'database',
			title: 'Database',
			icon: Database,
			path: '/settings/database',
			description: 'Database configuration',
			requiresToolAdmin: true
		},
		{
			id: 'system',
			title: 'System Settings',
			icon: Settings,
			path: '/settings/system',
			description: 'Configure system',
			requiresToolAdmin: true
		}
	];

	let visibleSteps = $derived(allSteps.filter(step => !step.requiresToolAdmin || isToolAdmin));

	function isCurrentStep(step: typeof allSteps[0]) {
		return $page.url.pathname === step.path;
	}
</script>

<div class="flex flex-1">
	<!-- Left Sidebar -->
	<aside class="w-64 flex flex-col" style="background: var(--color-bg-surface); border-right: 1px solid var(--color-border-default);">
		<!-- Sidebar Header -->
		<div class="p-6" style="border-bottom: 1px solid var(--color-border-default);">
			<h2 class="text-xs font-semibold" style="color: var(--color-text-primary);">Administration</h2>
			<p class="text-[11px] mt-1" style="color: var(--color-text-tertiary);">System configuration and user management</p>
		</div>

		<!-- Navigation Steps -->
		<nav class="flex-1 p-4 space-y-2">
			{#each visibleSteps as step, index}
				{@const isCurrent = isCurrentStep(step)}
				
				<a
					href={step.path}
					class="flex items-center p-3 rounded-lg transition-colors group"
					style="{isCurrent 
						? 'background: var(--color-bg-elevated); color: var(--color-accent-primary); border: 1px solid var(--color-accent-primary);' 
						: 'color: var(--color-text-secondary);'}"
				>
					<!-- Step Number -->
					<div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium mr-3"
						style="{isCurrent
						? 'background: var(--color-accent-primary); color: var(--color-text-inverse);'
						: 'background: var(--color-bg-inset); color: var(--color-text-tertiary);'}">
						{index + 1}
					</div>

					<!-- Step Icon and Content -->
					<div class="flex-1 min-w-0">
						<div class="flex items-center">
							<step.icon 
								class="w-4 h-4 mr-2"
								style="color: {isCurrent ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'};"
							/>
							<span class="text-xs font-medium truncate">{step.title}</span>
						</div>
						<p class="text-[10px] mt-1" style="color: {isCurrent ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'};">
							{step.description}
						</p>
					</div>

					<!-- Status Indicator -->
					{#if isCurrent}
						<div class="flex-shrink-0 w-2 h-2 rounded-full" style="background: var(--color-accent-primary);"></div>
					{:else}
						<div class="flex-shrink-0 w-2 h-2 rounded-full" style="background: var(--color-border-subtle);"></div>
					{/if}
				</a>
			{/each}
		</nav>

		<!-- Back to Workflow Link -->
		<div class="p-4" style="border-top: 1px solid var(--color-border-default);">
			<a 
				href="/" 
				class="flex items-center p-2 rounded-lg transition-colors" style="color: var(--color-text-secondary);"
			>
				<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
				</svg>
				<span class="text-xs font-medium">Back to Dashboard</span>
			</a>
		</div>

		<!-- Sidebar Footer -->
		<div class="p-4" style="border-top: 1px solid var(--color-border-default);">
			<div class="text-[10px]" style="color: var(--color-text-tertiary);">
				{#if isToolAdmin}
					<p class="font-medium mb-1">System Administration</p>
					<p>Full system access</p>
				{:else}
					<p class="font-medium mb-1">Department Admin</p>
					<p>Manage your department users</p>
				{/if}
			</div>
		</div>
	</aside>

	<!-- Main Content -->
	<main class="flex-1 overflow-auto">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			{@render children?.()}
		</div>
	</main>
</div>
