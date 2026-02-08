<script lang="ts">
	import type { Product } from '$lib/types/product';

	export let products: readonly Product[];
	export let maxVisible: number = 3;

	const getVisibleProducts = (items: readonly Product[], maxItems: number): readonly Product[] => {
		return items.slice(0, maxItems);
	};

	const getRemainingCount = (items: readonly Product[], maxItems: number): number => {
		return Math.max(0, items.length - maxItems);
	};

	$: visibleProducts = getVisibleProducts(products, maxVisible);
	$: remainingCount = getRemainingCount(products, maxVisible);
</script>

{#if products.length === 0}
	<div class="mt-1 text-xs text-slate-400">No products</div>
{:else}
	<div class="mt-1 flex flex-wrap gap-1">
		{#each visibleProducts as product (product.scope_id)}
			<span class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
				{product.name}
			</span>
		{/each}
		{#if remainingCount > 0}
			<span class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
				+{remainingCount}
			</span>
		{/if}
	</div>
{/if}
