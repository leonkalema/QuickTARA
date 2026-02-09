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
	<div class="mt-1 text-[10px]" style="color: var(--color-text-tertiary);">No products</div>
{:else}
	<div class="mt-1 flex flex-wrap gap-1">
		{#each visibleProducts as product (product.scope_id)}
			<span class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px]" style="background: var(--color-bg-elevated); color: var(--color-text-secondary); border: 1px solid var(--color-border-subtle);">
				{product.name}
			</span>
		{/each}
		{#if remainingCount > 0}
			<span class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px]" style="background: var(--color-bg-elevated); color: var(--color-text-tertiary); border: 1px solid var(--color-border-subtle);">
				+{remainingCount}
			</span>
		{/if}
	</div>
{/if}
