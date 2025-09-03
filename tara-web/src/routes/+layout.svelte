<script lang="ts">
	import '../app.css';
	import Header from '../components/layout/Header.svelte';
	import Sidebar from '../components/layout/Sidebar.svelte';
	import Footer from '../components/layout/Footer.svelte';
	import NotificationContainer from '../components/ui/NotificationContainer.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<title>QuickTARA - Threat Analysis & Risk Assessment</title>
	<meta name="description" content="Comprehensive threat analysis and risk assessment platform" />
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<!-- Header -->
	<Header />
	
	<!-- Main Layout with Sidebar -->
	<div class="flex flex-1">
		<!-- Left Sidebar -->
		<Sidebar />
		
		<!-- Main Content -->
		<main class="flex-1 overflow-auto">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				{@render children?.()}
			</div>
		</main>
	</div>
	
	<!-- Footer -->
	<Footer />
	
	<!-- Global Notifications -->
	<NotificationContainer />
</div>
