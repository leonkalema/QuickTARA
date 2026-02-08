<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher<{ cancel: void; save: { name: string; description: string } }>();

	export let name: string;
	export let description: string;

	const cancel = (): void => {
		dispatch('cancel');
	};

	const save = (): void => {
		dispatch('save', { name, description });
	};
</script>

<tr class="bg-amber-50">
	<td colspan="4" class="px-4 py-4">
		<div class="flex items-end space-x-4">
			<div class="flex-1">
				<label for="edit-name" class="block text-xs font-medium text-slate-600 mb-1">Name</label>
				<input id="edit-name" type="text" bind:value={name} class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
			</div>
			<div class="flex-1">
				<label for="edit-description" class="block text-xs font-medium text-slate-600 mb-1">Description</label>
				<input id="edit-description" type="text" bind:value={description} class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
			</div>
			<div class="flex space-x-2">
				<button class="px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors" on:click={cancel}>Cancel</button>
				<button class="px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors" on:click={save}>Save</button>
			</div>
		</div>
	</td>
</tr>
