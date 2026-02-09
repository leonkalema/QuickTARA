/**
 * Frontend permission checks mirroring core/workflow_rbac.py.
 * These are cosmetic gates — the backend enforces the real rules.
 */
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

/** Permission required for each transition target state */
const TRANSITION_PERMISSION: Record<string, string> = {
  draft: 'workflows:submit',
  review: 'workflows:submit',
  approved: 'workflows:approve',
  released: 'workflows:release',
};

const CREATE_PERMISSION = 'workflows:create';
const SIGNOFF_PERMISSION = 'workflows:signoff';

function userHasPermission(permission: string): boolean {
  const state = get(authStore);
  if (!state.user) return false;
  if (state.user.is_superuser) return true;
  const perms = authStore.getUserPermissions();
  return perms.includes(permission) || perms.includes('workflows:*');
}

function getCurrentUserEmail(): string {
  const state = get(authStore);
  return state.user?.email ?? '';
}

/** Can the current user create a new workflow? */
export function canCreateWorkflow(): boolean {
  return userHasPermission(CREATE_PERMISSION);
}

/** Can the current user add sign-offs? */
export function canSignoff(): boolean {
  return userHasPermission(SIGNOFF_PERMISSION);
}

/** Filter transition actions to only those the current user may perform. */
export function filterAllowedTransitions(
  transitions: { target: string; label: string }[],
  workflowCreatedBy: string,
): { target: string; label: string }[] {
  const email = getCurrentUserEmail();
  return transitions.filter((t) => {
    const perm = TRANSITION_PERMISSION[t.target];
    if (!perm) return false;
    if (!userHasPermission(perm)) return false;
    if (t.target === 'approved' && email === workflowCreatedBy) return false;
    return true;
  });
}
