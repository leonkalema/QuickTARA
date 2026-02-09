<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import '$lib/utils/tokenRefresh';
	import '../app.css';
	import CommandBar from '../components/layout/CommandBar.svelte';
	import SideNav from '../components/layout/SideNav.svelte';
	import NotificationContainer from '../components/ui/NotificationContainer.svelte';

	let { children } = $props();

	let isAuthPage = $derived($page.url.pathname === '/auth');
	let isSettingsPage = $derived($page.url.pathname.startsWith('/settings'));

	onMount(() => {
		authStore.init();
	});

	$effect(() => {
		if ($authStore.isInitialized && !isAuthPage && !$authStore.isAuthenticated) {
			goto('/auth');
		}
	});

	$effect(() => {
		if ($authStore.isInitialized && isAuthPage && $authStore.isAuthenticated) {
			goto('/products');
		}
	});
</script>

<svelte:head>
	<title>QuickTARA - Threat Analysis & Risk Assessment</title>
	<meta name="description" content="ISO/SAE 21434 threat analysis and risk assessment platform" />
</svelte:head>

{#if !$authStore.isInitialized}
	<div class="min-h-screen flex items-center justify-center" style="background: var(--color-bg-app);">
		<div class="animate-spin rounded-full h-8 w-8 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
	</div>
{:else if isAuthPage}
	<div class="min-h-screen" style="background: var(--color-bg-app);">
		{@render children?.()}
	</div>
{:else if $authStore.isAuthenticated}
	<div class="h-screen flex flex-col overflow-hidden" style="background: var(--color-bg-app);">
		<CommandBar />
		<div class="flex flex-1 overflow-hidden">
			{#if !isSettingsPage}
				<SideNav />
			{/if}
			<main class="flex-1 overflow-y-auto">
				<div class="max-w-[1400px] mx-auto px-6 py-6">
					{@render children?.()}
				</div>
			</main>
		</div>
		<NotificationContainer />
	</div>
{/if}
