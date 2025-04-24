<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Upload, X, FileText, CheckCircle, AlertCircle } from '@lucide/svelte';
  import { componentApi } from '../api/components';
  
  export let isOpen = false;
  
  let fileInput: HTMLInputElement;
  let selectedFile: File | null = null;
  let isUploading = false;
  let uploadError = '';
  let uploadSuccess = false;
  let importedComponents: any[] = [];
  
  const dispatch = createEventDispatcher();
  
  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      selectedFile = input.files[0];
      uploadError = '';
      uploadSuccess = false;
    }
  }
  
  function closeModal() {
    isOpen = false;
    selectedFile = null;
    uploadError = '';
    uploadSuccess = false;
    dispatch('close');
  }
  
  async function handleImport() {
    if (!selectedFile) {
      uploadError = 'Please select a CSV file to import.';
      return;
    }
    
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      uploadError = 'Selected file must be a CSV file.';
      return;
    }
    
    isUploading = true;
    uploadError = '';
    
    try {
      importedComponents = await componentApi.importFromCsv(selectedFile);
      uploadSuccess = true;
      dispatch('import', importedComponents);
    } catch (error: any) {
      uploadError = error.message || 'Failed to import components. Please check your CSV file format.';
      uploadSuccess = false;
    } finally {
      isUploading = false;
    }
  }
  
  function triggerFileInput() {
    if (fileInput) {
      fileInput.click();
    }
  }
</script>

{#if isOpen}
<div class="fixed inset-0 flex items-center justify-center z-50 backdrop-blur-sm bg-neutral-900/40 transition-opacity duration-200">
  <div class="bg-white rounded-xl shadow-lg p-6 w-full max-w-lg mx-4">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        <FileText size={24} class="mr-2 text-primary" />
        Import Components
      </h2>
      <button 
        on:click={closeModal}
        class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
        <X size={20} />
      </button>
    </div>
    
    <div class="mb-6">
      <p class="text-gray-600 mb-4">
        Upload a CSV file with component details. The file should have columns for component_id, name, type, safety_level, interfaces, etc.
      </p>
      
      <div 
        class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer"
        on:click={triggerFileInput}
        on:keydown={(e) => e.key === 'Enter' && triggerFileInput()}
        role="button"
        tabindex="0"
      >
        <input 
          type="file" 
          bind:this={fileInput}
          on:change={handleFileSelect}
          accept=".csv"
          class="hidden"
        />
        
        <Upload size={36} class="mx-auto mb-2 text-gray-400" />
        
        {#if selectedFile}
          <p class="font-medium text-primary">
            {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
          </p>
          <p class="text-sm text-gray-500 mt-1">Click to change file</p>
        {:else}
          <p class="font-medium text-gray-700">
            Drag and drop your CSV file here, or click to browse
          </p>
          <p class="text-sm text-gray-500 mt-1">
            Maximum file size: 10MB
          </p>
        {/if}
      </div>
      
      {#if uploadError}
        <div class="flex items-center mt-4 text-red-600 bg-red-50 p-3 rounded-lg">
          <AlertCircle size={18} class="mr-2 flex-shrink-0" />
          <p class="text-sm">{uploadError}</p>
        </div>
      {/if}
      
      {#if uploadSuccess}
        <div class="flex items-center mt-4 text-green-600 bg-green-50 p-3 rounded-lg">
          <CheckCircle size={18} class="mr-2 flex-shrink-0" />
          <p class="text-sm">Successfully imported {importedComponents.length} components!</p>
        </div>
      {/if}
    </div>
    
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <button 
        type="button"
        on:click={closeModal} 
        class="btn px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
        {uploadSuccess ? 'Close' : 'Cancel'}
      </button>
      <button 
        type="button"
        on:click={handleImport}
        class="btn btn-primary"
        disabled={!selectedFile || isUploading}>
        {#if isUploading}
          <span class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Importing...
          </span>
        {:else}
          Import Components
        {/if}
      </button>
    </div>
    
    {#if uploadSuccess && importedComponents.length > 0}
      <div class="mt-4 pt-4 border-t">
        <h3 class="font-semibold text-gray-800 mb-2">Imported Components:</h3>
        <div class="max-h-60 overflow-y-auto pr-2">
          <ul class="space-y-2">
            {#each importedComponents as component, i}
              <li class="text-sm bg-gray-50 p-2 rounded">
                <span class="font-medium">{component.name}</span>
                <span class="text-gray-500"> - {component.component_id}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  </div>
</div>
{/if}
