<script lang="ts">
	import '../app.css';
	import Header from '../components/layout/Header.svelte';
	import Footer from '../components/layout/Footer.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<title>QuickTARA - Threat Analysis & Risk Assessment</title>
	<meta name="description" content="Comprehensive threat analysis and risk assessment platform" />
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-50">
	<!-- Header -->
	<Header />
	
	<!-- Main Content -->
	<main class="flex-1">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			{@render children?.()}
		</div>
	</main>
	
	<!-- Footer -->
	<Footer />
</div>
