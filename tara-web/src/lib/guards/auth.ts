import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { isToolAdmin, isOrgAdmin, hasAnyRole } from '$lib/utils/permissions';
import { UserRole } from '$lib/types/roles';

export interface RouteGuardOptions {
    requireAuth?: boolean;
    requiredRoles?: string[];
    requiredPermissions?: string[];
    redirectTo?: string;
}

// Backend role values (snake_case) - simplified 6 roles
export const Role = {
    TOOL_ADMIN: 'tool_admin',
    ORG_ADMIN: 'org_admin',
    ANALYST: 'analyst',
    RISK_MANAGER: 'risk_manager',
    AUDITOR: 'auditor',
    VIEWER: 'viewer'
} as const;

export async function authGuard(options: RouteGuardOptions = {}) {
    const {
        requireAuth = true,
        requiredRoles = [],
        requiredPermissions = [],
        redirectTo = '/auth'
    } = options;

    const auth = get(authStore);

	// Check authentication
	if (requireAuth && !auth.isAuthenticated) {
		throw redirect(302, redirectTo);
	}

	// Check token validity and refresh if needed
	if (auth.isAuthenticated) {
		const tokenValid = await authStore.checkAndRefreshToken();
		if (!tokenValid) {
			throw redirect(302, redirectTo);
		}
	}

	    // Helper: determine superuser, prefer user payload, fallback to token decode
    const isSuperuser = (() => {
        const userFlag = (auth.user as any)?.is_superuser === true;
        if (userFlag) return true;
        try {
            const token = auth.token as string | null;
            if (!token) return false;
            const payload = JSON.parse(atob(token.split('.')[1]));
            return !!payload.is_superuser;
        } catch {
            return false;
        }
    })();

    // Check roles using centralized permission system
    if (requiredRoles.length > 0) {
        const hasRequiredRole = isSuperuser || requiredRoles.some(role => {
            // Convert role constants to UserRole enum values
            const roleMap: Record<string, UserRole> = {
                [Role.TOOL_ADMIN]: UserRole.TOOL_ADMIN,
                [Role.ORG_ADMIN]: UserRole.ORG_ADMIN,
                [Role.ANALYST]: UserRole.ANALYST,
                [Role.RISK_MANAGER]: UserRole.RISK_MANAGER,
                [Role.AUDITOR]: UserRole.AUDITOR,
                [Role.VIEWER]: UserRole.VIEWER
            };
            const userRoleEnum = roleMap[role];
            return userRoleEnum ? hasAnyRole([userRoleEnum]) : false;
        });
        
        if (!hasRequiredRole) {
            throw redirect(302, '/unauthorized');
        }
    }

    // Check permissions using centralized system
    if (requiredPermissions.length > 0) {
        if (!isSuperuser && !isToolAdmin()) {
            throw redirect(302, '/unauthorized');
        }
    }

    return true;
}

// Predefined guard functions for common use cases using centralized permissions
export const requireAuth = () => {
    const auth = get(authStore);
    if (!auth.isAuthenticated) {
        throw redirect(302, '/auth');
    }
};

export const requireAdmin = () => {
    requireAuth();
    if (!isToolAdmin()) {
        throw redirect(302, '/unauthorized');
    }
};

export const requireOrgAdmin = () => {
    requireAuth();
    if (!isOrgAdmin()) {
        throw redirect(302, '/unauthorized');
    }
};

export const requireRiskManager = () => {
    requireAuth();
    if (!hasAnyRole([UserRole.TOOL_ADMIN, UserRole.ORG_ADMIN, UserRole.RISK_MANAGER])) {
        throw redirect(302, '/unauthorized');
    }
};

export const requireAnalyst = () => {
    requireAuth();
    if (!hasAnyRole([UserRole.ORG_ADMIN, UserRole.ANALYST, UserRole.RISK_MANAGER])) {
        throw redirect(302, '/unauthorized');
    }
};

// Permission-based guards
export const requireCreatePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['create_threat', 'create_damage_scenario', 'create_asset']
});

export const requireReadPermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['read_threat', 'read_damage_scenario', 'read_asset']
});

export const requireUpdatePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['update_threat', 'update_damage_scenario', 'update_asset']
});

export const requireDeletePermission = () => authGuard({
	requireAuth: true,
	requiredPermissions: ['delete_threat', 'delete_damage_scenario', 'delete_asset']
});
