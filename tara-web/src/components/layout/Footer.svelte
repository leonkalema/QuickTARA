<script lang="ts">
  const currentYear = new Date().getFullYear();
</script>

<footer style="border-top: 1px solid var(--color-border-subtle);">
  <div class="px-5 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">QuickTARA</span>
      <span class="text-[10px]" style="color: var(--color-text-tertiary); opacity: 0.5;">v1.0.0</span>
    </div>
    <div class="text-[10px]" style="color: var(--color-text-tertiary); opacity: 0.5;">
      © {currentYear}
    </div>
  </div>
</footer>
