<script lang="ts">
  import { Package, Shield, FileText } from '@lucide/svelte';
</script>

<div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
  <h3 class="text-lg font-semibold text-blue-900 mb-4">Next Steps</h3>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <a
      href="/assets"
      class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
    >
      <Package class="w-5 h-5 text-blue-600 mr-3" />
      <div>
        <div class="font-medium text-blue-900">Manage Assets</div>
        <div class="text-sm text-blue-700">Add system components</div>
      </div>
    </a>

    <a
      href="/damage-scenarios"
      class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
    >
      <Shield class="w-5 h-5 text-blue-600 mr-3" />
      <div>
        <div class="font-medium text-blue-900">Damage Scenarios</div>
        <div class="text-sm text-blue-700">Define potential damages</div>
      </div>
    </a>

    <a
      href="/reports"
      class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
    >
      <FileText class="w-5 h-5 text-blue-600 mr-3" />
      <div>
        <div class="font-medium text-blue-900">Generate Report</div>
        <div class="text-sm text-blue-700">Export analysis results</div>
      </div>
    </a>
  </div>
</div>
