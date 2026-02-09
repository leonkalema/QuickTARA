<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Plus } from '@lucide/svelte';

	const dispatch = createEventDispatcher<{ cancel: void; create: void }>();

	export let isOpen: boolean;
	export let name: string;
	export let description: string;

	const cancel = (): void => {
		dispatch('cancel');
	};

	const create = (): void => {
		dispatch('create');
	};
</script>

{#if isOpen}
	<button class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 cursor-default" on:click={cancel} aria-label="Close modal"></button>
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
		<div class="rounded-xl shadow-2xl w-full max-w-md pointer-events-auto" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
			<div class="px-6 py-4" style="border-bottom: 1px solid var(--color-border-subtle);">
				<h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">New Department</h3>
			</div>
			<div class="px-6 py-4 space-y-4">
				<div>
					<label for="create-name" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">Name <span style="color: var(--color-error);">*</span></label>
					<input id="create-name" type="text" bind:value={name} placeholder="e.g., Engineering" class="w-full px-3 py-2 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
				</div>
				<div>
					<label for="create-description" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">Description</label>
					<textarea id="create-description" bind:value={description} placeholder="Optional description" rows="2" class="w-full px-3 py-2 text-xs rounded-lg resize-none" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"></textarea>
				</div>
			</div>
			<div class="px-6 py-4 rounded-b-xl flex justify-end space-x-3" style="background: var(--color-bg-elevated);">
				<button class="px-4 py-2 text-xs font-medium transition-colors" style="color: var(--color-text-secondary);" on:click={cancel}>Cancel</button>
				<button class="px-4 py-2 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);" on:click={create}>
					<Plus class="w-4 h-4 mr-1.5 inline" />
					Create
				</button>
			</div>
		</div>
	</div>
{/if}
