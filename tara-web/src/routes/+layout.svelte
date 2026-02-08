<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import '$lib/utils/tokenRefresh';
	import '../app.css';
	import Header from '../components/layout/Header.svelte';
	import Sidebar from '../components/layout/Sidebar.svelte';
	import Footer from '../components/layout/Footer.svelte';
	import NotificationContainer from '../components/ui/NotificationContainer.svelte';

	let { children } = $props();
	
	// Check if current route is auth page or settings page
	let isAuthPage = $derived($page.url.pathname === '/auth');
	let isSettingsPage = $derived($page.url.pathname.startsWith('/settings'));
	
	// Initialize auth store on mount
	onMount(() => {
		authStore.init();
	});

	// Redirect unauthenticated users to /auth when visiting protected routes
	// Only redirect AFTER auth store has initialized
	$effect(() => {
		if ($authStore.isInitialized && !isAuthPage && !$authStore.isAuthenticated) {
			goto('/auth');
		}
	});

	// If already authenticated and on /auth, send to default page
	$effect(() => {
		if ($authStore.isInitialized && isAuthPage && $authStore.isAuthenticated) {
			goto('/products');
		}
	});
</script>

<svelte:head>
	<title>QuickTARA - Threat Analysis & Risk Assessment</title>
	<meta name="description" content="Comprehensive threat analysis and risk assessment platform" />
</svelte:head>

{#if !$authStore.isInitialized}
	<!-- Show loading while auth initializes -->
	<div class="min-h-screen flex items-center justify-center bg-slate-900">
		<div class="text-center">
			<div class="animate-spin rounded-full h-10 w-10 border-2 border-blue-500 border-t-transparent mx-auto"></div>
		</div>
	</div>
{:else if isAuthPage}
	<!-- Auth page layout - no navigation -->
	<div class="min-h-screen">
		{@render children?.()}
	</div>
{:else if $authStore.isAuthenticated}
	<!-- Main app layout -->
	<div class="min-h-screen flex flex-col bg-gray-50">
		<Header />
		
		<div class="flex flex-1">
			{#if !isSettingsPage}
				<Sidebar />
			{/if}
			
			<main class="flex-1 overflow-auto">
				{#if isSettingsPage}
					{@render children?.()}
				{:else}
					<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
						{@render children?.()}
					</div>
				{/if}
			</main>
		</div>
		
		<Footer />
		<NotificationContainer />
	</div>
{/if}
