<script lang="ts">
  // Active page state
  export let activePage = 'components';
  
  // Navigation items
  const navItems = [
    { id: 'components', label: 'Components', icon: 'chip' },
    { id: 'analysis', label: 'Analysis', icon: 'search' },
    { id: 'review', label: 'Review', icon: 'check-circle' },
    { id: 'reports', label: 'Reports', icon: 'file-text' },
    { id: 'settings', label: 'Settings', icon: 'settings' }
  ];
  
  // Handle navigation click
  function handleNavClick(pageId: string) {
    activePage = pageId;
  }
</script>

<nav style="background-color: var(--color-nav-bg); color: var(--color-nav-text);" class="shadow-md">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center h-16">
      <!-- Logo & App Name -->
      <div class="flex items-center">
        <span class="text-2xl font-bold">QuickTARA</span>
        <span class="ml-2 text-sm py-1 px-2 rounded" style="background-color: var(--color-primary); color: white;">Web</span>
      </div>
      
      <!-- Navigation Items -->
      <div class="flex space-x-4">
        {#each navItems as item}
          <button
            class="flex items-center px-4 py-2 rounded-md text-base font-medium transition-all duration-200 ease-in-out"
            style={activePage === item.id 
              ? 'background-color: var(--color-primary); color: white; transform: scale(1.05);' 
              : 'color: var(--color-nav-text); opacity: 0.85;'}
            on:mouseenter={(e) => {
              if (activePage !== item.id) e.currentTarget.style.opacity = '1';
            }}
            on:mouseleave={(e) => {
              if (activePage !== item.id) e.currentTarget.style.opacity = '0.85';
            }}
            on:click={() => handleNavClick(item.id)}
          >
            <!-- Icon (placeholder) -->
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              {#if item.icon === 'chip'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
              {:else if item.icon === 'search'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              {:else if item.icon === 'check-circle'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              {:else if item.icon === 'file-text'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              {:else if item.icon === 'settings'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              {/if}
            </svg>
            {item.label}
          </button>
        {/each}
      </div>
    </div>
  </div>
</nav>
