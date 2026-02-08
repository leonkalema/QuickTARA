<script lang="ts">
  import { authStore } from '$lib/stores/auth';
  import { selectedProduct } from '$lib/stores/productStore';
  import { isToolAdmin, isOrgAdmin, canPerformTARA, canManageRisk, hasRole } from '$lib/utils/permissions';
  import { UserRole } from '$lib/types/roles';
  import { page } from '$app/stores';
  import { 
    FileText, 
    Package, 
    Zap, 
    AlertTriangle, 
    Shield, 
    BarChart3,
    Settings
  } from '@lucide/svelte';

  type StepPermission = 'tara' | 'risk' | 'reports' | 'all';

  interface WorkflowStep {
    id: string;
    title: string;
    icon: any;
    path: string;
    description: string;
    requiresProduct?: boolean;
    permission?: StepPermission;
  }

  interface AdminStep {
    id: string;
    title: string;
    icon: any;
    path: string;
    description: string;
    adminOnly: boolean;
  }

  const steps: WorkflowStep[] = [
    {
      id: 'products',
      title: 'Product Scope',
      icon: FileText,
      path: '/products',
      description: 'Select and manage products',
      permission: 'tara'
    },
    {
      id: 'assets',
      title: 'Assets & Components',
      icon: Package,
      path: '/assets',
      description: 'Define system components',
      requiresProduct: true,
      permission: 'tara'
    },
    {
      id: 'damage-scenarios',
      title: 'Damage Scenarios',
      icon: Zap,
      path: '/damage-scenarios',
      description: 'What could go wrong?',
      requiresProduct: true,
      permission: 'tara'
    },
    {
      id: 'threat-scenarios',
      title: 'Threat Scenarios',
      icon: AlertTriangle,
      path: '/threat-scenarios',
      description: 'How could it happen?',
      requiresProduct: true,
      permission: 'tara'
    },
    {
      id: 'risk-assessment',
      title: 'Risk Assessment',
      icon: Shield,
      path: '/risk-assessment',
      description: 'Analyze and rate risks',
      requiresProduct: true,
      permission: 'tara'
    },
    {
      id: 'risk-treatment',
      title: 'Risk Treatment',
      icon: Shield,
      path: '/risk-treatment',
      description: 'Treat and mitigate risks',
      requiresProduct: true,
      permission: 'tara'
    },
    {
      id: 'reports',
      title: 'Reports & Export',
      icon: BarChart3,
      path: '/reports',
      description: 'Generate documentation',
      requiresProduct: true,
      permission: 'reports'
    }
  ];

  const adminSteps: AdminStep[] = [
    {
      id: 'settings',
      title: 'Settings',
      icon: Settings,
      path: '/settings',
      description: 'System configuration',
      adminOnly: true
    }
  ];

  function hasPermissionForStep(permission?: StepPermission): boolean {
    if (!permission) return true;
    
    switch (permission) {
      case 'tara':
        return canPerformTARA();
      case 'risk':
        return canManageRisk();
      case 'reports':
        return canPerformTARA() || canManageRisk() || hasRole(UserRole.AUDITOR) || hasRole(UserRole.VIEWER);
      case 'all':
        return true;
      default:
        return true;
    }
  }

  function shouldShowStep(step: WorkflowStep): boolean {
    return hasPermissionForStep(step.permission);
  }

  function isStepAccessible(step: WorkflowStep | AdminStep): boolean {
    if ('adminOnly' in step && step.adminOnly) {
      return isToolAdmin() || isOrgAdmin();
    }
    if ('requiresProduct' in step && step.requiresProduct) {
      return $selectedProduct !== null;
    }
    return true;
  }

  function isCurrentStep(step: WorkflowStep | AdminStep): boolean {
    return $page.url.pathname.startsWith(step.path);
  }

  $: visibleSteps = steps.filter(shouldShowStep);
</script>

<aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
  <!-- Sidebar Header -->
  <div class="p-6 border-b border-gray-200">
    <h2 class="text-lg font-semibold text-gray-900">TARA Workflow</h2>
    {#if $selectedProduct}
      <p class="text-sm text-gray-600 mt-1">
        Working on: <span class="font-medium">{$selectedProduct.name}</span>
      </p>
    {:else}
      <p class="text-sm text-gray-500 mt-1">Select a product to begin</p>
    {/if}
  </div>

  <!-- Navigation Steps -->
  <nav class="flex-1 p-4 space-y-2">
    {#each visibleSteps as step, index}
      {@const isAccessible = isStepAccessible(step)}
      {@const isCurrent = isCurrentStep(step)}
      
      <a
        href={isAccessible ? step.path : '#'}
        class="flex items-center p-3 rounded-lg transition-colors group {isCurrent 
          ? 'bg-blue-50 text-blue-700 border border-blue-200' 
          : isAccessible 
            ? 'text-gray-700 hover:bg-gray-50 hover:text-gray-900' 
            : 'text-gray-400 cursor-not-allowed'}"
        class:pointer-events-none={!isAccessible}
      >
        <!-- Step Number -->
        <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium mr-3 {isCurrent
          ? 'bg-blue-100 text-blue-700'
          : isAccessible
            ? 'bg-gray-100 text-gray-600 group-hover:bg-gray-200'
            : 'bg-gray-50 text-gray-400'}">
          {index + 1}
        </div>

        <!-- Step Icon and Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center">
            <svelte:component 
              this={step.icon} 
              class="w-5 h-5 mr-2 {isCurrent ? 'text-blue-600' : isAccessible ? 'text-gray-500' : 'text-gray-300'}" 
            />
            <span class="text-sm font-medium truncate">{step.title}</span>
          </div>
          <p class="text-xs mt-1 {isCurrent ? 'text-blue-600' : isAccessible ? 'text-gray-500' : 'text-gray-400'}">
            {step.description}
          </p>
        </div>

        <!-- Status Indicator -->
        {#if !isAccessible && step.requiresProduct}
          <div class="flex-shrink-0 w-2 h-2 rounded-full bg-gray-300"></div>
        {:else if isCurrent}
          <div class="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500"></div>
        {:else}
          <div class="flex-shrink-0 w-2 h-2 rounded-full bg-gray-200"></div>
        {/if}
      </a>
    {/each}

    <!-- Admin Settings Section -->
    {#each adminSteps as step}
      {@const isAccessible = isStepAccessible(step)}
      {@const isCurrent = isCurrentStep(step)}
      
      {#if isAccessible}
        <div class="mt-4 pt-4 border-t border-gray-200">
          <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2 px-3">
            Administration
          </p>
          <a
            href={step.path}
            class="flex items-center p-3 rounded-lg transition-colors group {isCurrent 
              ? 'bg-blue-50 text-blue-700 border border-blue-200' 
              : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'}"
          >
            <svelte:component 
              this={step.icon} 
              class="w-5 h-5 mr-3 {isCurrent ? 'text-blue-600' : 'text-gray-500'}" 
            />
            <div class="flex-1 min-w-0">
              <span class="text-sm font-medium truncate">{step.title}</span>
              <p class="text-xs mt-1 {isCurrent ? 'text-blue-600' : 'text-gray-500'}">
                {step.description}
              </p>
            </div>
            {#if isCurrent}
              <div class="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500"></div>
            {:else}
              <div class="flex-shrink-0 w-2 h-2 rounded-full bg-gray-200"></div>
            {/if}
          </a>
        </div>
      {/if}
    {/each}
  </nav>

  <!-- Sidebar Footer -->
  <div class="p-4 border-t border-gray-200">
    <div class="text-xs text-gray-500">
      <p class="font-medium mb-1">Progress Tracking</p>
      <p>Complete each step in sequence for comprehensive threat analysis.</p>
    </div>
  </div>
</aside>
