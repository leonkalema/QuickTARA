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
		<div class="bg-white rounded-xl shadow-2xl w-full max-w-md pointer-events-auto">
			<div class="px-6 py-4 border-b border-slate-100">
				<h3 class="text-lg font-semibold text-slate-900">New Department</h3>
			</div>
			<div class="px-6 py-4 space-y-4">
				<div>
					<label for="create-name" class="block text-sm font-medium text-slate-700 mb-1">Name <span class="text-red-500">*</span></label>
					<input id="create-name" type="text" bind:value={name} placeholder="e.g., Engineering" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
				</div>
				<div>
					<label for="create-description" class="block text-sm font-medium text-slate-700 mb-1">Description</label>
					<textarea id="create-description" bind:value={description} placeholder="Optional description" rows="2" class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"></textarea>
				</div>
			</div>
			<div class="px-6 py-4 bg-slate-50 rounded-b-xl flex justify-end space-x-3">
				<button class="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors" on:click={cancel}>Cancel</button>
				<button class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors" on:click={create}>
					<Plus class="w-4 h-4 mr-1.5 inline" />
					Create
				</button>
			</div>
		</div>
	</div>
{/if}
