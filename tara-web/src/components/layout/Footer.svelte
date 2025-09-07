<script lang="ts">
  const currentYear = new Date().getFullYear();
</script>

<footer class="bg-gray-50 border-t border-gray-200">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="py-6">
      <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
        <!-- Left side - App info -->
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-600">
            <span class="font-medium">QuickTARA</span> - Threat Analysis & Risk Assessment
          </div>
          <div class="text-xs text-gray-400">
            v1.0.0
          </div>
        </div>

        <!-- Right side - Links and info -->
        <div class="flex items-center space-x-6 text-sm text-gray-500">
          <a href="/help" class="hover:text-gray-700 transition-colors">
            Help
          </a>
          <a href="/docs" class="hover:text-gray-700 transition-colors">
            Documentation
          </a>
          <div class="text-xs">
            © {currentYear} QuickTARA
          </div>
        </div>
      </div>
    </div>
  </div>
</footer>
