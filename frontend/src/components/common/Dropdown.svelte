<script lang="ts">
  export let id: string = '';
  export let label: string = '';
  export let value: string = '';
  export let options: { value: string; label: string }[] = [];
  export let required: boolean = false;
  export let disabled: boolean = false;
  export let className: string = '';
  export let placeholder: string = 'Select an option';
</script>

<div class="dropdown-container">
  {#if label}
    <label for={id} class="block text-sm font-medium text-gray-700 mb-1">{label}</label>
  {/if}
  <select
    {id}
    bind:value
    {required}
    {disabled}
    class="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm {className}"
    on:change
  >
    <option value="" disabled selected>{placeholder}</option>
    {#each options as option}
      <option value={option.value}>{option.label}</option>
    {/each}
  </select>
</div>

<style>
  .dropdown-container {
    width: 100%;
    margin-bottom: 1rem;
  }
</style>
