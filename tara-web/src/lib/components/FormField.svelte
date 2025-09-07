<script lang="ts">
  import type { APIError } from '$lib/utils/errorHandler';
  import { getFieldError } from '$lib/utils/errorHandler';
  
  export let label: string;
  export let name: string;
  export let type: string = 'text';
  export let value: string = '';
  export let placeholder: string = '';
  export let required: boolean = false;
  export let disabled: boolean = false;
  export let error: APIError | null = null;
  export let options: Array<{value: string, label: string}> = [];
  export let rows: number = 3;
  export let maxlength: number | undefined = undefined;
  export let minlength: number | undefined = undefined;
  
  let inputElement: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
  
  $: fieldError = error ? getFieldError(error, name) : undefined;
  $: hasError = !!fieldError;
  
  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
    value = target.value;
  }
  
  export function focus() {
    inputElement?.focus();
  }
  
  export function validate(): boolean {
    if (required && (!value || value.trim() === '')) {
      return false;
    }
    
    if (minlength && value.length < minlength) {
      return false;
    }
    
    if (maxlength && value.length > maxlength) {
      return false;
    }
    
    return true;
  }
</script>

<div class="mb-4">
  <label for={name} class="block text-sm font-medium text-gray-700 mb-1">
    {label}
    {#if required}
      <span class="text-red-500">*</span>
    {/if}
  </label>
  
  {#if type === 'textarea'}
    <textarea
      bind:this={inputElement}
      id={name}
      {name}
      bind:value
      {placeholder}
      {required}
      {disabled}
      {rows}
      {maxlength}
      {minlength}
      class="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed {hasError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}"
      on:input={handleInput}
    ></textarea>
  {:else if type === 'select'}
    <select
      bind:this={inputElement}
      id={name}
      {name}
      bind:value
      {required}
      {disabled}
      class="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed {hasError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}"
      on:change={handleInput}
    >
      <option value="">{placeholder || 'Select an option'}</option>
      {#each options as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>
  {:else}
    <input
      bind:this={inputElement}
      id={name}
      {name}
      {type}
      bind:value
      {placeholder}
      {required}
      {disabled}
      {maxlength}
      {minlength}
      class="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed {hasError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}"
      on:input={handleInput}
    />
  {/if}
  
  {#if fieldError}
    <p class="mt-1 text-sm text-red-600">{fieldError}</p>
  {/if}
  
  {#if maxlength && value.length > 0}
    <p class="mt-1 text-xs text-gray-500 text-right">
      {value.length}/{maxlength} characters
    </p>
  {/if}
</div>
