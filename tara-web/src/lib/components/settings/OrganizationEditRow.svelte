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

<tr style="background: var(--color-bg-elevated);">
	<td colspan="4" class="px-4 py-4">
		<div class="flex items-end space-x-4">
			<div class="flex-1">
				<label for="edit-name" class="block text-[10px] font-medium mb-1" style="color: var(--color-text-tertiary);">Name</label>
				<input id="edit-name" type="text" bind:value={name} class="w-full px-3 py-2 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
			</div>
			<div class="flex-1">
				<label for="edit-description" class="block text-[10px] font-medium mb-1" style="color: var(--color-text-tertiary);">Description</label>
				<input id="edit-description" type="text" bind:value={description} class="w-full px-3 py-2 text-xs rounded-lg" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
			</div>
			<div class="flex space-x-2">
				<button class="px-3 py-2 text-xs font-medium transition-colors" style="color: var(--color-text-secondary);" on:click={cancel}>Cancel</button>
				<button class="px-3 py-2 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);" on:click={save}>Save</button>
			</div>
		</div>
	</td>
</tr>
