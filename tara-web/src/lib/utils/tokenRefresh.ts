import { authStore } from '$lib/stores/auth';
import { browser } from '$app/environment';

let refreshInterval: NodeJS.Timeout | null = null;

// Start automatic token refresh checking
export function startTokenRefreshTimer() {
	if (!browser) return;
	
	// Check every 5 minutes
	refreshInterval = setInterval(async () => {
		await authStore.checkAndRefreshToken();
	}, 5 * 60 * 1000);
}

// Stop automatic token refresh checking
export function stopTokenRefreshTimer() {
	if (refreshInterval) {
		clearInterval(refreshInterval);
		refreshInterval = null;
	}
}

// Initialize token refresh timer when module loads
if (browser) {
	startTokenRefreshTimer();
}
