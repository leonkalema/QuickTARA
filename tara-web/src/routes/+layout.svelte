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
	
	// Initialize auth store without immediate redirects
	onMount(() => {
		authStore.init();
	});

	// Redirect unauthenticated users to /auth when visiting protected routes
	$effect(() => {
		if (!isAuthPage && !$authStore.isAuthenticated) {
			goto('/auth');
		}
	});

	// If already authenticated and on /auth, send to default page
	$effect(() => {
		if (isAuthPage && $authStore.isAuthenticated) {
			goto('/products');
		}
	});
</script>

<svelte:head>
	<title>QuickTARA - Threat Analysis & Risk Assessment</title>
	<meta name="description" content="Comprehensive threat analysis and risk assessment platform" />
</svelte:head>

{#if isAuthPage}
	<!-- Auth page layout - no navigation -->
	<div class="min-h-screen bg-gray-50">
		{@render children?.()}
	</div>
{:else}
	<!-- Main app layout - only show if authenticated -->
	{#if $authStore.isAuthenticated}
		<div class="min-h-screen flex flex-col bg-gray-50">
			<!-- Header -->
			<Header />
			
			<!-- Main Layout with Sidebar -->
			<div class="flex flex-1">
				<!-- Left Sidebar - only show for non-settings pages -->
				{#if !isSettingsPage}
					<Sidebar />
				{/if}
				
				<!-- Main Content -->
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
			
			<!-- Footer -->
			<Footer />
			
			<!-- Global Notifications -->
			<NotificationContainer />
		</div>
	{:else}
		<!-- Show loading while auth initializes -->
		<div class="min-h-screen flex items-center justify-center bg-gray-50">
			<div class="text-center">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
				<p class="mt-4 text-gray-600">Loading...</p>
			</div>
		</div>
	{/if}
{/if}
